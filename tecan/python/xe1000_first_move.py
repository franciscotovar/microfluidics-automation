from tecancavro.transport import TecanAPISerial
from tecancavro.models import XE1000

com = TecanAPISerial(
    0, "COM7", 9600,
    ser_timeout=1,
    max_attempts=3
)

pump = XE1000(com_link=com)

print("Connecting to XE1000...")
print("Firmware:", com.sendRcv("&"))

input("Press ENTER to initialize the pump...")

pump.init(in_port="right", init_speed=20)

print("INITIALIZATION COMPLETE!")
