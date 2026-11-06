#!/usr/bin/env python3
"""
test_vision.py
Captures frames from the camera, runs ball detection, prints detection results,
and saves a snapshot of the camera view to test_camera_view.jpg.
"""

import sys
import time
import cv2
import numpy as np

# Ensure ballbot src is on path
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ballbot.runtime.camera import Camera

def main():
    print("[INFO] Initializing Camera...")
    try:
        cam = Camera()
    except Exception as e:
        print(f"[ERROR] Failed to initialize camera: {e}", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Camera initialized. Capturing 20 frames...")
    cam.debug = True

    try:
        detected_count = 0
        last_frame = None
        last_center = (0, 0)

        for i in range(20):
            frame = cam.take_picture()
            x, y, valid = cam.coordinate(frame)
            last_frame = frame
            last_center = (x, y)
            if valid:
                detected_count += 1
                print(f"  Frame {i+1:2d}: Ball DETECTED at ({x:3d}, {y:3d})")
            else:
                print(f"  Frame {i+1:2d}: No ball detected (last pos: {x:3d}, {y:3d})")
            time.sleep(0.05)

        print(f"\n[SUMMARY] Detected ball in {detected_count}/20 frames.")

        # Save annotated image for inspection
        if last_frame is not None:
            # Draw crosshair
            annotated = last_frame.copy()
            x, y = last_center
            cv2.line(annotated, (x - 10, y), (x + 10, y), (0, 255, 0) if detected_count > 0 else (255, 0, 0), 2)
            cv2.line(annotated, (x, y - 10), (x, y + 10), (0, 255, 0) if detected_count > 0 else (255, 0, 0), 2)
            
            bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
            out_path = "/home/bb/Ball-Balancing-Robot/test_camera_view.jpg"
            cv2.imwrite(out_path, bgr)
            print(f"[INFO] Saved snapshot to: {out_path}")

    finally:
        cam.terminate()

if __name__ == "__main__":
    main()
