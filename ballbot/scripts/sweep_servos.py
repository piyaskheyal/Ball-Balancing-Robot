#!/usr/bin/env python3
"""
sweep_servos.py
Sweeps servos through angles: 0° -> 60° -> 90° -> 0° in a continuous loop.
By default, broadcasts the signal across ALL 16 CHANNELS (0 through 15)
so regardless of which slots your servos are plugged into, they will receive the signal.

Press Ctrl+C to stop.
"""

import sys
import time
import argparse
from adafruit_servokit import ServoKit


def main():
    parser = argparse.ArgumentParser(description="Sweep PCA9685 servos.")
    parser.add_argument(
        "--channels",
        type=str,
        default="all",
        help="Comma-separated channel numbers (e.g. 13,14,15) or 'all' (default: all 16 channels)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.2,
        help="Delay in seconds between steps (default: 1.2s)",
    )
    args = parser.parse_args()

    print("[INFO] Initializing PCA9685 ServoKit (16 channels)...")
    try:
        kit = ServoKit(channels=16)
    except Exception as e:
        print(f"[ERROR] Could not connect to PCA9685 over I2C: {e}", file=sys.stderr)
        sys.exit(1)

    if args.channels.lower() == "all":
        ch_list = list(range(16))
    else:
        try:
            ch_list = [int(c.strip()) for c in args.channels.split(",")]
        except ValueError:
            print(f"[ERROR] Invalid channels argument: {args.channels}", file=sys.stderr)
            sys.exit(1)

    print(f"[INFO] Configuring channels: {ch_list}")
    servos = {}
    for ch in ch_list:
        if 0 <= ch < 16:
            s = kit.servo[ch]
            s.actuation_range = 180
            s.set_pulse_width_range(500, 2500)
            servos[ch] = s
        else:
            print(f"[WARNING] Channel {ch} is out of range (valid: 0-15), skipping.")

    sequence = [0, 60, 90, 0]

    print("\n[INFO] Starting sweep loop across channels:")
    print(f"       Channels : {list(servos.keys())}")
    print(f"       Sequence : {sequence}")
    print("       Press Ctrl+C to stop and disarm.\n")

    loop_count = 1
    try:
        while True:
            print(f"--- Cycle #{loop_count} ---")
            for angle in sequence:
                pulse_us = 500 + (angle / 180.0) * 2000
                print(f" -> Setting ALL channels to {angle:2d}° (~{pulse_us:4.0f}µs)...")
                for ch, s in servos.items():
                    s.angle = angle
                time.sleep(args.delay)
            loop_count += 1
            print()
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user (Ctrl+C).")
    finally:
        print("[INFO] Disarming servos on all active channels...")
        for ch, s in servos.items():
            s.angle = None
        print("[INFO] Done. Servos disarmed.")


if __name__ == "__main__":
    main()
