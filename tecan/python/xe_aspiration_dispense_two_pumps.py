
from concurrent.futures import ThreadPoolExecutor
from xe1000_controller import XE1000Controller


pump1 = XE1000Controller(
    port="COM10",
    syringe_ul=250,
    in_port="right"
)

pump2 = XE1000Controller(
    port="COM7",
    syringe_ul=1000,
    in_port="left"
)

pumps = [pump1, pump2]


def parallel(executor, operation, *args):
    """Execute the same operation on both pumps concurrently."""
    futures = [
        executor.submit(getattr(pump, operation), *args)
        for pump in pumps
    ]

    # Wait for both operations and propagate errors.
    for future in futures:
        future.result()


with ThreadPoolExecutor(max_workers=2) as executor:

    # 1. Communication
    parallel(executor, "firmware")

    # 2. Initialization
    input("\nENTER to initialize BOTH pumps...")
    parallel(executor, "initialize", 20)

    # 3. Select reservoir ports
    input("\nENTER to select both INPUT ports...")
    parallel(executor, "select_input")

    # 4. Aspirate
    input("\nENTER to aspirate 50 uL simultaneously...")
    parallel(executor, "aspirate", 50)

    # 5. Select output ports
    input("\nENTER to select both OUTPUT ports...")
    parallel(executor, "select_output")

    # 6. Dispense
    from concurrent.futures import ThreadPoolExecutor

    # Independent flow rates
    pump1.set_flow_rate(500)    # COM10, 250 uL syringe
    pump2.set_flow_rate(1000)   # COM7, 1000 uL syringe

    # Both syringes must already contain 50 uL.
    pump1.select_output()
    pump2.select_output()

    input("\nPress ENTER to start simultaneous dispensing...")

    with ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(pump1.dispense, 50)
        f2 = executor.submit(pump2.dispense, 50)

        # Equivalent to LabSmith WaitDone()
        f1.result()
        f2.result()

    print("Both dispensing operations completed.")


    print("\nFINAL POSITIONS")
    for pump in pumps:
        print(pump.port, pump.position())

print("\nDUAL PARALLEL TEST COMPLETE")
