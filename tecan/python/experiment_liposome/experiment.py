from dual_xe1000 import DualXE1000

ETHANOL_VOLUME_UL = 150
ASPIRATION_FLOW = {"PBS": 1500, "Ethanol": 1500}
DISPENSING_FLOW = {"PBS": 1500, "Ethanol": 500}
CYCLES = 2

if __name__ == "__main__":
    DualXE1000().run_cycle(
        ethanol_volume_ul=ETHANOL_VOLUME_UL,
        aspiration_flow=ASPIRATION_FLOW,
        dispensing_flow=DISPENSING_FLOW,
        cycles=CYCLES,
    )
