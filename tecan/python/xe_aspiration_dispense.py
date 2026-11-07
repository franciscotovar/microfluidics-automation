from xe1000_controller import XE1000Controller


pump = XE1000Controller(
    port="COM7",
    syringe_ul=1000,
    in_port="left"
)

print("Firmware:", pump.firmware())

input("\nPress ENTER to initialize...")
pump.initialize(init_speed=20)

print("Position:", pump.position())
print("Volume:", pump.volume_in_syringe(), "uL")

input("\nPress ENTER to aspirate 100 uL...")
pump.aspirate(100)

input("\nPress ENTER to dispense 100 uL...")
pump.dispense(100)

print("\nFinal position:", pump.position())
print("Cycle complete.")
