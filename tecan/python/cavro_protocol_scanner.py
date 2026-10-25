
#python cavro_protocol_scanner.py --port COM3

"""
Cavro XLP3000 - Protocol Scanner, Phase 1

Exploratory scan based on Cavro-family protocols.
XLP3000 compatibility is NOT confirmed.

- Query commands only: Q and &
- DT, OEM, OEM_SYNC
- 9600 and 38400 baud
- Addresses 0x31 through 0x3F
- OEM sequences 0x31 through 0x3F
- Negative control 0x55
- Full CSV logging
- No motor movement commands

IMPORTANT:
Power-cycle the pump between protocol families.
Do not run this scanner with other serial software connected.
"""

import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

import serial


BAUDS = [9600, 38400]
ADDRESSES = range(0x31, 0x40)
SEQUENCES = range(0x31, 0x40)
COMMANDS = [b"Q", b"&"]
FAMILIES = ["DT", "OEM", "OEM_SYNC"]


def build_packet(family, address, sequence, command):

    if family == "DT":
        return b"/" + bytes([address]) + command + b"\r"

    frame = (
        b"\x02"
        + bytes([address, sequence])
        + command
        + b"\x03"
    )

    checksum = 0

    for byte in frame:
        checksum ^= byte

    packet = frame + bytes([checksum])

    if family == "OEM_SYNC":
        packet = b"\xff" + packet

    return packet


def classify(rx):

    if not rx:
        return "EMPTY"

    if all(byte == 0 for byte in rx):
        return "NULL_BYTE"

    return "CANDIDATE"


def exchange(ser, packet, wait):

    ser.reset_input_buffer()

    ser.write(packet)
    ser.flush()

    deadline = time.monotonic() + wait
    response = bytearray()

    while time.monotonic() < deadline:

        n = ser.in_waiting

        if n:
            response.extend(ser.read(n))

        time.sleep(0.005)

    return bytes(response)


def run(args):

    filename = Path(
        f"xlp3000_phase1_"
        f"{datetime.now():%Y%m%d_%H%M%S}.csv"
    )

    fields = [
        "timestamp",
        "family",
        "baud",
        "address",
        "sequence",
        "command",
        "tx",
        "rx",
        "classification",
        "control_rx",
        "control_classification",
    ]

    total = 0
    candidates = 0

    with filename.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        try:

            for family in FAMILIES:

                print("\n" + "=" * 55)
                print("Protocol:", family)
                print("=" * 55)

                print(
                    "\nSwitch off the 24 V supply, "
                    "wait a few seconds, then switch it on."
                )

                input(
                    "Press Enter when ready "
                    "(Ctrl+C to cancel): "
                )

                for baud in BAUDS:

                    print(f"\nTesting {baud} baud")

                    with serial.Serial(
                        port=args.port,
                        baudrate=baud,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=0.05,
                        write_timeout=2,
                        rtscts=False,
                        xonxoff=False,
                        dsrdtr=False,
                    ) as ser:

                        for address in ADDRESSES:

                            if family == "DT":
                                sequences = [0x31]
                            else:
                                sequences = SEQUENCES

                            for sequence in sequences:

                                for command in COMMANDS:

                                    packet = build_packet(
                                        family,
                                        address,
                                        sequence,
                                        command
                                    )

                                    rx = exchange(
                                        ser,
                                        packet,
                                        args.wait
                                    )

                                    status = classify(rx)

                                    # Negative control
                                    control = exchange(
                                        ser,
                                        b"\x55",
                                        args.wait
                                    )

                                    control_status = classify(
                                        control
                                    )

                                    writer.writerow({
                                        "timestamp": datetime.now().isoformat(),
                                        "family": family,
                                        "baud": baud,
                                        "address": f"{address:02X}",
                                        "sequence": f"{sequence:02X}",
                                        "command": command.decode(),
                                        "tx": packet.hex(" "),
                                        "rx": rx.hex(" "),
                                        "classification": status,
                                        "control_rx": control.hex(" "),
                                        "control_classification": control_status,
                                    })

                                    file.flush()

                                    total += 1

                                    if status == "CANDIDATE":

                                        candidates += 1

                                        print(
                                            "\nCANDIDATE DETECTED"
                                        )

                                        print(
                                            "Family:", family,
                                            "Baud:", baud
                                        )

                                        print(
                                            "Address:",
                                            f"0x{address:02X}"
                                        )

                                        print(
                                            "Sequence:",
                                            f"0x{sequence:02X}"
                                        )

                                        print(
                                            "Command:",
                                            command
                                        )

                                        print(
                                            "TX:",
                                            packet.hex(" ")
                                        )

                                        print(
                                            "RX:",
                                            rx.hex(" ")
                                        )

                                        print(
                                            "Control RX:",
                                            control.hex(" ")
                                        )

                                        print(
                                            "Candidate only; "
                                            "not a validated protocol response."
                                        )

                                    if total % 50 == 0:

                                        print(
                                            f"{total} queries completed | "
                                            f"{candidates} candidates"
                                        )

                                    time.sleep(args.gap)

        except KeyboardInterrupt:

            print("\nScan interrupted.")

        except serial.SerialException as exc:

            print("\nSerial error:", exc)

    print("\nSCAN FINISHED")
    print("Total queries:", total)
    print("Candidates:", candidates)
    print("CSV:", filename)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--port",
        default="COM3"
    )

    parser.add_argument(
        "--wait",
        type=float,
        default=0.25
    )

    parser.add_argument(
        "--gap",
        type=float,
        default=0.05
    )

    args = parser.parse_args()

    if args.wait <= 0 or args.gap < 0:
        parser.error("Invalid wait or gap")

    print("CAVRO XLP3000 PROTOCOL SCANNER")
    print("Phase 1: 9600 / 38400 baud")
    print("Port:", args.port)

    print(
        "\nWARNING: Protocol compatibility "
        "is not established."
    )

    print(
        "Queries only. No movement commands."
    )

    run(args)
