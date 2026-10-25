import serial
import time

PORT = "COM3"

with serial.Serial(PORT, 9600, timeout=1) as ser:

    tests = [
        ("NO COMMAND", None),
        ("SINGLE BYTE", b"\x55"),
        ("OEM QUERY", bytes.fromhex("FF 02 31 31 51 03 50")),
    ]

    for name, packet in tests:

        ser.reset_input_buffer()

        if packet is not None:
            ser.write(packet)
            ser.flush()

        time.sleep(0.5)

        rx = ser.read(100)

        print(name)
        print("RX:", rx.hex(" "))
        print("RAW:", repr(rx))
        print()