
import serial
import time

PORT = "COM7"
BAUD = 9600
DURATION = 30

with serial.Serial(PORT, BAUD, timeout=0.1) as ser:
    print("Transmitting 0x55 continuously...")
    end = time.monotonic() + DURATION

    while time.monotonic() < end:
        ser.write(b"\x55" * 100)
        ser.flush()

    print("Transmission complete.")
