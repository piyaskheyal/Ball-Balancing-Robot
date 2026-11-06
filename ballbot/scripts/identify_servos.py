#!/usr/bin/env python3
"""
identify_servos.py
Wiggles channels one by one so the user can easily see which physical servo
corresponds to which PCA9685 channel.

Press Ctrl+C to stop.
"""

import sys
import time
import argparse
from adafruit_servokit import ServoKit

def main():
    parser = argparse.ArgumentParser(description="Identify PCA9685 servo channels one by one.")
    parser.add_argument(
        "--channels",
        type=str,
        default="0,1,2",
        help="Comma-separated list of channels to test in sequence (default: 0,1,2)",
    )
    args = parser.parse_args()

    print("[INFO] Initializing PCA9685 ServoKit...")
    try:
        kit = ServoKit(channels=16)
    except Exception as e:
        print(f"[ERROR] Could not connect to PCA9685: {e}", file=sys.stderr)
        sys.exit(1)

    ch_list = [int(c.strip()) for c in args.channels.split(",")]
    
    print(f"[INFO] Configuring channels {ch_list} for 180° range (500-2500µs)...")
    servos = {}
    for ch in ch_list:
        s = kit.servo[ch]
        s.actuation_range = 180
        s.set_pulse_width_range(500, 2500)
        servos[ch] = s

    # First, center all target channels to 90 degrees
    print("[INFO] Centering all specified channels to 90°...")
    for ch, s in servos.items():
        s.angle = 90
    time.sleep(1.0)

    print("\n" + "="*50)
    print("STARTING INDIVIDUAL CHANNEL IDENTIFICATION")
    print("="*50)

    try:
        for ch in ch_list:
            s = servos[ch]
            print(f"\n>>> [TESTING CHANNEL {ch}] <<<")
            print(f"Watch your 3 servos! Wiggling CHANNEL {ch}...")
            
            # Wiggle back and forth twice
            for _ in range(2):
                s.angle = 60
                time.sleep(0.4)
                s.angle = 120
                time.sleep(0.4)
                s.angle = 90
                time.sleep(0.4)
            
            print(f"Channel {ch} test complete. Returned to 90° center.")
            time.sleep(0.8)

        print("\n" + "="*50)
        print("All channels in test list were wiggled and returned to 90°.")
        print("="*50)

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")
    finally:
        print("\n[INFO] Servos remain at 90° center position.")

if __name__ == "__main__":
    main()
