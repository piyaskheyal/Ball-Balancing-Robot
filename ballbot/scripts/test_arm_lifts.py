#!/usr/bin/env python3
"""
test_arm_lifts.py

Tests the physical direction of each servo individually:
Commanding -15 degrees from level to verify whether each arm lifts UP or lowers DOWN.
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
    print("      INDIVIDUAL SERVO LIFT DIRECTION VERIFICATION")
    print("=" * 65)
    print("We will command each servo to change by -15 degrees from level.")
    print("Watch that specific arm and note if it LIFTS UP or LOWERS DOWN.\n")

    model = RobotKinematics()
    robot = RobotController(model)
    robot.arm()

    h1 = servo_home(robot.cal["s1"])
    h2 = servo_home(robot.cal["s2"])
    h3 = servo_home(robot.cal["s3"])

    print(f"[INFO] Holding level pose: s1={h1:.1f}, s2={h2:.1f}, s3={h3:.1f}")
    robot.home_servos(hold_s=1.0)
    time.sleep(1.0)

    # 1. Servo 1 (Ch 0, Bottom-Left)
    print("\n>>> [1/3] SERVO 1 (Bottom-Left, Ch 0): Commanding -15 deg (from 122 to 107)...")
    robot._force_servo_angles(h1 - 15.0, h2, h3)
    time.sleep(3.0)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.0)

    # 2. Servo 2 (Ch 1, Right)
    print("\n>>> [2/3] SERVO 2 (Right, Ch 1): Commanding -15 deg (from 141 to 126)...")
    robot._force_servo_angles(h1, h2 - 15.0, h3)
    time.sleep(3.0)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.0)

    # 3. Servo 3 (Ch 2, Top-Left)
    print("\n>>> [3/3] SERVO 3 (Top-Left, Ch 2): Commanding -15 deg (from 140 to 125)...")
    robot._force_servo_angles(h1, h2, h3 - 15.0)
    time.sleep(3.0)
    robot._force_servo_angles(h1, h2, h3)
    time.sleep(1.0)

    print("\n[INFO] Returning to level pose and disarming.")
    robot.disarm()
    print("=" * 65)
    print("Done! For each servo (1, 2, 3), did -15 deg make it LIFT UP or LOWER DOWN?")
    print("=" * 65)

if __name__ == "__main__":
    main()
