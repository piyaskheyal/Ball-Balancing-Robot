#!/usr/bin/env python3
"""
test_channel_mapping.py

Identifies the exact physical arm connected to each PCA9685 channel (0, 1, 2)
by moving each channel individually while keeping the others at level.
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
    print("       EXACT CHANNEL TO PHYSICAL ARM IDENTIFICATION")
    print("=" * 65)
    print("We will move each PCA9685 channel (0, 1, 2) individually.")
    print("Look at the platform from the camera perspective and note:")
    print("Is the moving arm on the RIGHT, TOP-LEFT, or BOTTOM-LEFT?\n")

    model = RobotKinematics()
    robot = RobotController(model)
    robot.arm()

    h1 = servo_home(robot.cal["s1"])
    h2 = servo_home(robot.cal["s2"])
    h3 = servo_home(robot.cal["s3"])

    print(f"[INFO] Platform holding level: Ch0={h1:.1f}, Ch1={h2:.1f}, Ch2={h3:.1f}")
    robot.home_servos(hold_s=1.0)
    time.sleep(1.0)

    # 1. Move Channel 0 only
    print("\n" + "=" * 50)
    print(">>> [TEST 1/3] MOVING CHANNEL 0 ONLY (holding Ch1 & Ch2 level)...")
    print("Watch the platform now!")
    print("=" * 50)
    robot._force_servo_angles(h1 - 20.0, h2, h3)
    time.sleep(3.5)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.5)

    # 2. Move Channel 1 only
    print("\n" + "=" * 50)
    print(">>> [TEST 2/3] MOVING CHANNEL 1 ONLY (holding Ch0 & Ch2 level)...")
    print("Watch the platform now!")
    print("=" * 50)
    robot._force_servo_angles(h1, h2 - 20.0, h3)
    time.sleep(3.5)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.5)

    # 3. Move Channel 2 only
    print("\n" + "=" * 50)
    print(">>> [TEST 3/3] MOVING CHANNEL 2 ONLY (holding Ch0 & Ch1 level)...")
    print("Watch the platform now!")
    print("=" * 50)
    robot._force_servo_angles(h1, h2, h3 - 20.0)
    time.sleep(3.5)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.5)

    print("\n[INFO] Returning to level and disarming.")
    robot.disarm()
    print("=" * 65)
    print("Done! Please tell me which physical arm moved for each channel:")
    print("  - Channel 0 moved: [Right / Bottom-Left / Top-Left]?")
    print("  - Channel 1 moved: [Right / Bottom-Left / Top-Left]?")
    print("  - Channel 2 moved: [Right / Bottom-Left / Top-Left]?")
    print("=" * 65)

if __name__ == "__main__":
    main()
