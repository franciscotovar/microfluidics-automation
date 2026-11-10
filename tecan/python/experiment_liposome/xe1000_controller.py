from tecancavro.transport import TecanAPISerial
from tecancavro.models import XE1000


class XE1000Controller:
    STEPS_PER_STROKE = 1000

    def __init__(self, port, syringe_ul, in_port, address=0):
        self.port = port
        self.syringe_ul = syringe_ul
        self.in_port = in_port
        self.initialized = False
        self.com = TecanAPISerial(
            address, port, 9600,
            ser_timeout=1,
            max_attempts=3
        )

        self.pump = XE1000(
            com_link=self.com,
            syringe_ul=syringe_ul
        )

    def firmware(self):
        return self.com.sendRcv("&")

    def position(self):
        return self.pump.getPlungerPos()

    def volume_in_syringe(self):
        return (
            self.position()
            * self.syringe_ul
            / self.STEPS_PER_STROKE
        )

    def initialize(self, init_speed=20):
        self.initialized = False

        self.pump.init(
            in_port=self.in_port,
            init_speed=init_speed
        )

        self.initialized = True
        print(f"{self.port}: initialized")

    def _require_initialized(self):
        if not self.initialized:
            raise RuntimeError(
                f"{self.port}: initialize pump first"
            )

    def select_input(self):
        self._require_initialized()

        if self.pump.state["cur_port"] != "input":
            self.pump.changePortInput(execute=True)

        print(f"{self.port}: INPUT selected")

    def select_output(self):
        self._require_initialized()

        if self.pump.state["cur_port"] != "output":
            self.pump.changePortOutput(execute=True)

        print(f"{self.port}: OUTPUT selected")

    def aspirate(self, volume_ul):
        self._require_initialized()

        if volume_ul <= 0:
            raise ValueError("Volume must be positive")

        pos_before = self.position()
        steps = int(
            volume_ul * self.STEPS_PER_STROKE
            / self.syringe_ul
        )

        if steps < 1:
            raise ValueError("Volume is below one step")

        if pos_before + steps > self.STEPS_PER_STROKE:
            raise ValueError("Insufficient syringe capacity")

        self.select_input()

        self.pump.extract(
            from_port="input",
            volume_ul=volume_ul,
            execute=True
        )

        pos_after = self.position()

        print(
            f"{self.port}: aspirated {volume_ul} uL nominal, "
            f"position {pos_before} -> {pos_after}"
        )

        return pos_after

    def dispense(self, volume_ul):
        self._require_initialized()

        if volume_ul <= 0:
            raise ValueError("Volume must be positive")

        pos_before = self.position()
        steps = int(
            volume_ul * self.STEPS_PER_STROKE
            / self.syringe_ul
        )

        if steps < 1:
            raise ValueError("Volume is below one step")

        if steps > pos_before:
            raise ValueError("Insufficient volume in syringe")

        self.select_output()

        self.pump.dispense(
            to_port="output",
            volume_ul=volume_ul,
            execute=True
        )

        pos_after = self.position()

        print(
            f"{self.port}: dispensed {volume_ul} uL nominal, "
            f"position {pos_before} -> {pos_after}"
        )

        return pos_after


    def set_flow_rate(self, flow_ul_min):
        self._require_initialized()

        if flow_ul_min <= 0:
            raise ValueError("Flow rate must be positive")

        # XE1000: speed / 10 = seconds per full stroke
        speed = round(
            600 * self.syringe_ul / flow_ul_min
        )

        if not 20 <= speed <= 600:
            raise ValueError(
                f"{self.port}: flow rate outside supported range"
            )

        self.pump.setSpeed(speed=speed, execute=True)

        print(
            f"{self.port}: requested {flow_ul_min} uL/min, "
            f"speed code S{speed}"
        )
