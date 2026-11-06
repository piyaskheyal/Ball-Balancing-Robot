#!/usr/bin/env python3
"""
capture_frame.py
Captures a single snapshot from the USB camera (/dev/video0)
to inspect ambient lighting and camera alignment.

Usage:
    python3 ballbot/scripts/capture_frame.py
"""

import sys
import time
import cv2
import numpy as np

def main():
    device = 0
    output_path = "/home/bb/Ball-Balancing-Robot/captured_frame.jpg"

    print(f"[INFO] Opening camera on /dev/video{device}...")
    cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera on /dev/video{device}", file=sys.stderr)
        sys.exit(1)

    print("[INFO] Warming up camera sensor (auto-exposure settling)...")
    # Discard first few frames to allow sensor AGC and AWB to adapt
    for _ in range(8):
        cap.read()
        time.sleep(0.05)

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        print("[ERROR] Failed to capture frame from camera.", file=sys.stderr)
        sys.exit(1)

    # Compute brightness metrics
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mean_brightness = float(np.mean(gray))

    # Save full resolution 640x480 frame
    cv2.imwrite(output_path, frame)

    print("=" * 50)
    print(f"[SUCCESS] Frame captured successfully!")
    print(f"  File location   : {output_path}")
    print(f"  Resolution      : {frame.shape[1]} x {frame.shape[0]}")
    print(f"  Mean Brightness : {mean_brightness:.1f} / 255.0")
    print("=" * 50)
    print("You can view 'captured_frame.jpg'. Adjust your lights and run again anytime!")

if __name__ == "__main__":
    main()
