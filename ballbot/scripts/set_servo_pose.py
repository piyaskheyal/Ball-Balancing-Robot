#!/usr/bin/env python3
"""
set_servo_pose.py
Utility script to position all 3 ballbot servos (s1=ch13, s2=ch15, s3=ch14)
to a specified angle or center position using Adafruit ServoKit.

Usage:
    python3 set_servo_pose.py --angle 0
    python3 set_servo_pose.py --angle 90   # standard 180-deg center
    python3 set_servo_pose.py --hold       # hold torque until Enter / Ctrl+C
"""

import os
import sys
import time
import argparse
from adafruit_servokit import ServoKit


def main():
    parser = argparse.ArgumentParser(description="Position Ball Balancing Robot servos safely.")
    parser.add_argument(
        "--angle",
        type=float,
        default=0.0,
        help="Target angle in degrees (default: 0.0)",
    )
    parser.add_argument(
        "--actuation-range",
        type=int,
        default=180,
        help="Servo total actuation range in degrees (default: 180 for MG99R)",
    )
    parser.add_argument(
        "--min-pulse",
        type=int,
        default=500,
        help="Minimum pulse width in microseconds (default: 500)",
    )
    parser.add_argument(
        "--max-pulse",
        type=int,
        default=2500,
        help="Maximum pulse width in microseconds (default: 2500)",
    )
    parser.add_argument(
        "--hold",
        action="store_true",
        help="Keep servos energized and holding position until Enter or Ctrl+C is pressed",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=3.0,
        help="Seconds to hold position before disarming (if --hold is not set, default: 3.0)",
    )
    parser.add_argument(
        "--disarm-on-exit",
        action="store_true",
        default=False,
        help="Disarm servos (release PWM) on exit",
    )
    args = parser.parse_args()

    print(f"[INFO] Initializing PCA9685 ServoKit (16 channels)...")
    try:
        kit = ServoKit(channels=16)
    except Exception as e:
        print(f"[ERROR] Failed to initialize ServoKit: {e}", file=sys.stderr)
        sys.exit(1)

    # Channels: s1=0, s2=1, s3=2
    ch1 = int(os.environ.get("BALLBOT_CH1", "0"))
    ch2 = int(os.environ.get("BALLBOT_CH2", "1"))
    ch3 = int(os.environ.get("BALLBOT_CH3", "2"))
    channels = {"s1": ch1, "s2": ch2, "s3": ch3}
    servos = {}

    target_angle = max(0.0, min(float(args.actuation_range), args.angle))
    pulse_us = args.min_pulse + (target_angle / args.actuation_range) * (args.max_pulse - args.min_pulse)

    print(f"[INFO] Servo Configuration:")
    print(f"       Actuation range : {args.actuation_range}°")
    print(f"       Pulse range     : {args.min_pulse}µs - {args.max_pulse}µs")
    print(f"       Target angle    : {target_angle}° (~{pulse_us:.1f}µs pulse)")
    print(f"       Channels        : s1->ch13, s2->ch15, s3->ch14")

    for name, ch in channels.items():
        s = kit.servo[ch]
        s.actuation_range = args.actuation_range
        s.set_pulse_width_range(args.min_pulse, args.max_pulse)
        servos[name] = s

    print(f"\n[INFO] Commanding all 3 servos to {target_angle}°...")
    for name, s in servos.items():
        s.angle = target_angle
        print(f"       {name} (channel {channels[name]}) -> {target_angle}°")

    if args.hold:
        print("\n[ACTIVE] Servos are powered and holding position.")
        print("         You can now safely attach/adjust horns at this position.")
        print("         Press [Enter] or Ctrl+C when finished to complete...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user.")
    else:
        print(f"\n[ACTIVE] Holding position for {args.duration} seconds...")
        time.sleep(args.duration)

    if args.disarm_on_exit:
        print("[INFO] Disarming servos (releasing torque)...")
        for name, s in servos.items():
            s.angle = None
    else:
        print("[INFO] Servos remain locked at target position.")

    print("[SUCCESS] Done.")


if __name__ == "__main__":
    main()
