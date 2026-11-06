#!/usr/bin/env python3
"""
test_servo_directions.py

Moves each servo (s1, s2, s3) individually by +12 degrees from level pose
so the user can clearly identify which physical servo corresponds to which
direction in the camera frame (Top, Bottom, Left, Right).
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ballbot.runtime.controller import RobotController, servo_home
from ballbot.runtime.robotKinematics import RobotKinematics

def main():
    print("=" * 65)
    print("        SERVO & CAMERA AXIS ALIGNMENT TEST")
    print("=" * 65)
    print("This script will move each servo individually by +12 degrees.")
    print("Watch the platform and note where each servo lifts/tilts:")
    print("  - From the camera perspective, is it Top, Bottom, Left, or Right?\n")

    model = RobotKinematics()
    robot = RobotController(model)
    robot.arm()

    h1 = servo_home(robot.cal["s1"])
    h2 = servo_home(robot.cal["s2"])
    h3 = servo_home(robot.cal["s3"])

    print(f"[INFO] Neutral level pose: s1={h1:.1f}, s2={h2:.1f}, s3={h3:.1f}")
    robot.home_servos(hold_s=1.0)
    time.sleep(1.0)

    # 1. Test Servo 1
    print("\n>>> [1/3] JOGGING SERVO 1 (s1) by +12 degrees for 3 seconds...")
    robot._force_servo_angles(h1 + 12.0, h2, h3)
    time.sleep(3.0)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.0)

    # 2. Test Servo 2
    print("\n>>> [2/3] JOGGING SERVO 2 (s2) by +12 degrees for 3 seconds...")
    robot._force_servo_angles(h1, h2 + 12.0, h3)
    time.sleep(3.0)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.0)

    # 3. Test Servo 3
    print("\n>>> [3/3] JOGGING SERVO 3 (s3) by +12 degrees for 3 seconds...")
    robot._force_servo_angles(h1, h2, h3 + 12.0)
    time.sleep(3.0)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.0)

    print("\n[INFO] Returning to neutral and disarming.")
    robot.disarm()
    print("=" * 65)
    print("Done! Please tell me which physical location (e.g. Top, Bottom-Left,")
    print("Bottom-Right, etc.) each servo (s1, s2, s3) lifted from the camera view.")
    print("=" * 65)

if __name__ == "__main__":
    main()
