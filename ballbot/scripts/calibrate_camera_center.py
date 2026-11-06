#!/usr/bin/env bash
#!/usr/bin/env python3
"""
calibrate_camera_center.py

Moves the platform to the calibrated level plane pose, holds it steady,
allows the user to place the ball at the physical center of the plate,
and records the ball's exact camera pixel coordinates as the target setpoint.

Results are saved to:
  - ballbot/config/camera.json
  - camera_center_calibrated.jpg (visual inspection)
"""

import sys
import os
import time
import json
from pathlib import Path
import cv2
import numpy as np

# Ensure ballbot/src is on import path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ballbot.runtime.controller import RobotController
from ballbot.runtime.robotKinematics import RobotKinematics
from ballbot.runtime.camera import Camera

CONFIG_PATH = ROOT / "config" / "camera.json"
PREVIEW_PATH = ROOT.parent / "camera_center_calibrated.jpg"

def main():
    print("=" * 65)
    print("      BALLBOT CAMERA CENTER & SETPOINT CALIBRATOR")
    print("=" * 65)

    print("[1/4] Initializing Kinematics and Controller...")
    model = RobotKinematics()
    robot = RobotController(model)
    robot.arm()

    print("[2/4] Moving platform to leveled plane pose and holding...")
    robot.home_servos(hold_s=0.5)

    print("\n" + "*" * 65)
    print(" >>> PLATFORM IS NOW HOLDING LEVEL PLANE POSE <<<")
    print(" Please place the ball in the physical center of the plate.")
    print(" When the ball is stationary in the center, press [ENTER] to record.")
    print(" (Or press Ctrl+C to abort)")
    print("*" * 65 + "\n")

    try:
        input("Press [ENTER] when ready...")
    except (KeyboardInterrupt, EOFError):
        print("\n[INFO] Aborted by user.")
        robot.disarm()
        sys.exit(0)

    print("\n[3/4] Initializing camera and capturing 30 samples...")
    cam = Camera()

    time.sleep(0.5)  # Allow auto-exposure to stabilize

    samples_x = []
    samples_y = []
    samples_r = []
    last_frame = None

    for i in range(30):
        frame = cam.take_picture()
        last_frame = frame.copy()
        x, y, valid = cam.coordinate(frame)
        if valid:
            samples_x.append(x)
            samples_y.append(y)
        time.sleep(0.04)

    cam.terminate()
    robot.disarm()

    if len(samples_x) < 15:
        print(f"\n[ERROR] Only {len(samples_x)}/30 detections succeeded. Insufficient samples.", file=sys.stderr)
        print("Please check lighting and ball visibility.", file=sys.stderr)
        sys.exit(1)

    mean_x = float(np.mean(samples_x))
    mean_y = float(np.mean(samples_y))
    std_x = float(np.std(samples_x))
    std_y = float(np.std(samples_y))

    print("\n[4/4] Calibration Analysis:")
    print(f"  Valid samples : {len(samples_x)} / 30")
    print(f"  Calibrated X  : {mean_x:.2f} px  (std: {std_x:.2f})")
    print(f"  Calibrated Y  : {mean_y:.2f} px  (std: {std_y:.2f})")

    # Save to camera.json
    cam_cfg = {
        "target_x": round(mean_x, 2),
        "target_y": round(mean_y, 2),
        "platform_center_x": round(mean_x, 2),
        "platform_center_y": round(mean_y, 2),
        "samples": len(samples_x),
        "std_x": round(std_x, 2),
        "std_y": round(std_y, 2),
    }

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cam_cfg, indent=2) + "\n")
    print(f"\n[SAVED] Configuration updated in: {CONFIG_PATH}")

    # Generate annotated inspection image
    if last_frame is not None:
        # Convert RGB to BGR for saving
        bgr = cv2.cvtColor(last_frame, cv2.COLOR_RGB2BGR)
        cx, cy = int(round(mean_x)), int(round(mean_y))

        # Draw calibrated target marker
        cv2.drawMarker(bgr, (cx, cy), (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
        cv2.circle(bgr, (cx, cy), 22, (255, 0, 0), 2)
        cv2.putText(
            bgr,
            f"Center: ({mean_x:.1f}, {mean_y:.1f})",
            (max(5, cx - 45), max(20, cy - 28)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )
        cv2.imwrite(str(PREVIEW_PATH), bgr)
        print(f"[SAVED] Verification preview image saved to: {PREVIEW_PATH}")

    print("\n" + "=" * 65)
    print(" Calibration successful! The robot will now target this exact center.")
    print("=" * 65)

if __name__ == "__main__":
    main()
