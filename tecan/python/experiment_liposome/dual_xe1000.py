
from concurrent.futures import ThreadPoolExecutor
from math import isfinite

from hardware_config import PUMPS
from xe1000_controller import XE1000Controller


class DualXE1000:

    def __init__(self):
        self.pumps = {
            name: XE1000Controller(**config)
            for name, config in PUMPS.items()
        }

    def _parallel(self, operation, args=None):
        args = args or {}

        with ThreadPoolExecutor(
            max_workers=len(self.pumps)
        ) as executor:

            futures = {
                name: executor.submit(
                    getattr(pump, operation),
                    *args.get(name, ())
                )
                for name, pump in self.pumps.items()
            }

            errors = []

            for name, future in futures.items():
                try:
                    future.result()
                except Exception as exc:
                    errors.append(f"{name}: {exc}")

            if errors:
                raise RuntimeError(
                    f"{operation} failed: "
                    + "; ".join(errors)
                )

    def _speed_code(self, name, pump, flow, stage):
        if (
            not isinstance(flow, (int, float))
            or not isfinite(flow)
            or flow <= 0
        ):
            raise ValueError(
                f"{name}: invalid {stage} flow: {flow!r}"
            )

        speed = round(
            600 * pump.syringe_ul / flow
        )

        if not 20 <= speed <= 600:
            raise ValueError(
                f"{name}: {stage.upper()} FLOW OUT OF RANGE\n"
                f"  Requested: {flow} uL/min\n"
                f"  Nominal minimum: {pump.syringe_ul} uL/min\n"
                f"  Nominal maximum: {30 * pump.syringe_ul} uL/min\n"
                f"  Calculated speed code: S{speed}"
            )

        return speed

    def run_cycle(
        self,
        ethanol_volume_ul,
        aspiration_flow,
        dispensing_flow,
        cycles=1
    ):
        # Validate parameters before moving hardware.
        if (
            not isinstance(cycles, int)
            or isinstance(cycles, bool)
            or cycles < 1
        ):
            raise ValueError(
                f"CYCLES must be a positive integer: {cycles!r}"
            )

        expected = {"PBS", "Ethanol"}

        if set(self.pumps) != expected:
            raise ValueError(
                "Hardware configuration must contain "
                "PBS and Ethanol"
            )

        for label, settings in (
            ("ASPIRATION_FLOW", aspiration_flow),
            ("DISPENSING_FLOW", dispensing_flow),
        ):
            if set(settings) != expected:
                raise ValueError(
                    f"{label}: expected PBS and Ethanol"
                )

        if (
            not isinstance(ethanol_volume_ul, (int, float))
            or not isfinite(ethanol_volume_ul)
            or ethanol_volume_ul <= 0
        ):
            raise ValueError(
                "ETHANOL_VOLUME_UL must be positive and finite"
            )

        for name, pump in self.pumps.items():
            self._speed_code(
                name, pump, aspiration_flow[name], "aspiration"
            )
            self._speed_code(
                name, pump, dispensing_flow[name], "dispensing"
            )

        # Ethanol is the independent volume.
        requested = {
            "Ethanol": ethanol_volume_ul,
            "PBS": (
                ethanol_volume_ul
                * dispensing_flow["PBS"]
                / dispensing_flow["Ethanol"]
            ),
        }

        # Convert volumes to achievable plunger steps.
        steps = {}
        actual = {}

        for name, pump in self.pumps.items():
            volume = requested[name]
            step_ul = pump.syringe_ul / 1000

            if volume > pump.syringe_ul:
                raise ValueError(
                    f"{name}: VOLUME EXCEEDS SYRINGE CAPACITY\n"
                    f"  Required: {volume:.3f} uL\n"
                    f"  Capacity: {pump.syringe_ul:.3f} uL"
                )

            n = round(volume / step_ul)

            if n < 1:
                raise ValueError(
                    f"{name}: VOLUME BELOW RESOLUTION\n"
                    f"  Required: {volume:.3f} uL\n"
                    f"  Minimum step: {step_ul:.3f} uL"
                )

            if n > 1000:
                raise ValueError(
                    f"{name}: {n} steps exceeds 1000"
                )

            steps[name] = n
            actual[name] = n * step_ul

        # Display the full plan.
        print("\nDISPENSING PLAN")
        print(f"Cycles: {cycles}")

        for name in ("PBS", "Ethanol"):
            pump = self.pumps[name]
            duration = (
                60 * actual[name] / dispensing_flow[name]
            )

            print(
                f"{name}: "
                f"aspirate={actual[name]:.3f} uL, "
                f"dispense={actual[name]:.3f} uL, "
                f"aspiration_flow={aspiration_flow[name]} uL/min, "
                f"dispensing_flow={dispensing_flow[name]} uL/min, "
                f"nominal_dispensing_time={duration:.3f} s"
            )

        print("\nHARDWARE CONFIGURATION")

        for name, pump in self.pumps.items():
            print(
                f"{name}: {pump.port}, "
                f"syringe={pump.syringe_ul} uL, "
                f"input={pump.in_port}"
            )
            print("Firmware:", pump.firmware())

        confirmation = input(
            "\nVerify physical connections. "
            "Type y to initialize both pumps: "
        )

        if confirmation != "y":
            print("Cancelled.")
            return

        # Initialize once, not on every cycle.
        self._parallel("initialize")

        print("\nINITIAL POSITIONS")
        for name, pump in self.pumps.items():
            position = pump.position()
            print(f"{name}: {position} steps")

            if position != 0:
                raise RuntimeError(
                    f"{name}: expected zero after initialization, "
                    f"measured {position} steps"
                )

        # Execute the requested number of cycles.
        for cycle in range(1, cycles + 1):

            print(f"\n========== CYCLE {cycle}/{cycles} ==========")

            # Verify that the previous cycle ended at zero.
            for name, pump in self.pumps.items():
                position = pump.position()

                if position != 0:
                    raise RuntimeError(
                        f"{name}: cannot start cycle {cycle}. "
                        f"Expected 0 steps, measured {position}"
                    )

            # Step 1: Select reservoir ports.
            self._parallel("select_input")

            # Step 2: Set aspiration flow rates.
            self._parallel(
                "set_flow_rate",
                {
                    name: (aspiration_flow[name],)
                    for name in self.pumps
                }
            )

            # Step 3: Aspirate concurrently.
            self._parallel(
                "aspirate",
                {
                    name: (actual[name],)
                    for name in self.pumps
                }
            )

            # Verify aspirated positions.
            for name, pump in self.pumps.items():
                position = pump.position()

                if position != steps[name]:
                    raise RuntimeError(
                        f"{name}: ASPIRATION POSITION MISMATCH\n"
                        f"  Expected: {steps[name]} steps\n"
                        f"  Measured: {position} steps"
                    )

            # Step 4: Select output ports.
            self._parallel("select_output")

            # Step 5: Set dispensing flow rates.
            self._parallel(
                "set_flow_rate",
                {
                    name: (dispensing_flow[name],)
                    for name in self.pumps
                }
            )

            # Step 6: Dispense concurrently.
            self._parallel(
                "dispense",
                {
                    name: (actual[name],)
                    for name in self.pumps
                }
            )

            # Step 7: Verify final positions.
            print("\nFINAL POSITIONS")

            for name, pump in self.pumps.items():
                position = pump.position()
                print(f"{name}: {position} steps")

                if position != 0:
                    raise RuntimeError(
                        f"{name}: DISPENSING POSITION MISMATCH\n"
                        f"  Expected: 0 steps\n"
                        f"  Measured: {position} steps"
                    )

            print(f"CYCLE {cycle} COMPLETE")

        print("\nALL CYCLES COMPLETE")
