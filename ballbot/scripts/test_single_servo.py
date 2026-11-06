#!/usr/bin/env python3
"""
test_single_servo.py
Drives Channel 0 and Channel 15 (and 13, 14) through a continuous, visible sweep
to test the single connected servo.
"""

import sys
import time
from adafruit_servokit import ServoKit

def main():
    print("[INFO] Initializing PCA9685 on I2C...")
    try:
        kit = ServoKit(channels=16)
    except Exception as e:
        print(f"[ERROR] Could not connect to PCA9685: {e}", file=sys.stderr)
        sys.exit(1)

    # Test channels: 0 and 15 (and 13, 14 as well)
    test_channels = [0, 15, 13, 14]
    servos = {}

    for ch in test_channels:
        s = kit.servo[ch]
        s.actuation_range = 180
        s.set_pulse_width_range(500, 2500)
        servos[ch] = s

    print(f"[INFO] Configured channels {test_channels} for 180° sweep (500-2500µs, 50Hz).")
    print("[INFO] Sweeping angles: 0° -> 60° -> 120° -> 180° -> 90° -> 0°...")
    print("       Watch the servo carefully!")

    angles = [0, 60, 120, 180, 90, 0]
    
    for cycle in range(1, 3):
        print(f"\n--- Sweep Cycle {cycle}/2 ---")
        for angle in angles:
            pulse_us = 500 + (angle / 180.0) * 2000
            print(f" -> Setting channels {test_channels} to {angle:3d}° (~{pulse_us:4.0f}µs pulse)...")
            for ch, s in servos.items():
                s.angle = angle
            time.sleep(0.8)

    print("\n[INFO] Test sweep finished.")

if __name__ == "__main__":
    main()
