#!/usr/bin/env python3
"""
detect_servo_point.py

Finds the ball position in captured_frame.jpg, calculates polar angle
relative to the calibrated platform center, and saves an annotated image.
"""

import cv2
import numpy as np
import math
import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cam_cfg_path = ROOT / "config" / "camera.json"

servo_name = sys.argv[1] if len(sys.argv) > 1 else "servo"

if cam_cfg_path.exists():
    with open(cam_cfg_path, "r") as f:
        cfg = json.load(f)
    cx0 = float(cfg.get("target_x", 93.93))
    cy0 = float(cfg.get("target_y", 76.27))
else:
    cx0, cy0 = 93.93, 76.27

img = cv2.imread("captured_frame.jpg")
if img is None:
    print("[ERROR] captured_frame.jpg not found.")
    sys.exit(1)

h, w, _ = img.shape
small = cv2.resize(img, (200, 150))
gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
blurred = cv2.medianBlur(gray, 5)

circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=20,
    param1=50,
    param2=16,
    minRadius=8,
    maxRadius=40
)

if circles is None:
    print("[ERROR] No circles detected in captured_frame.jpg.")
    sys.exit(1)

# Pick circle closest to expected ball radius or farthest from center
c_arr = circles[0]
best_c = None
best_dist = -1

for c in c_arr:
    bx, by, br = float(c[0]), float(c[1]), float(c[2])
    dx = bx - cx0
    dy = by - cy0
    dist = math.hypot(dx, dy)
    if dist > best_dist:
        best_dist = dist
        best_c = (bx, by, br)

bx, by, br = best_c
dx = bx - cx0
dy = by - cy0
dist = math.hypot(dx, dy)
angle = math.degrees(math.atan2(dy, dx))
if angle < 0:
    angle += 360.0

print(f"[FOUND] {servo_name}:")
print(f"  Pixel (200x150): ({bx:.1f}, {by:.1f})")
print(f"  Distance from center: {dist:.1f} px")
print(f"  Angle from center: {angle:.1f} deg")

# Annotate
scale_x = w / 200.0
scale_y = h / 150.0
cx_full = int(round(cx0 * scale_x))
cy_full = int(round(cy0 * scale_y))
bx_full = int(round(bx * scale_x))
by_full = int(round(by * scale_y))
br_full = int(round(br * scale_x))

annotated = img.copy()
cv2.drawMarker(annotated, (cx_full, cy_full), (0, 255, 0), cv2.MARKER_CROSS, 25, 2)
cv2.line(annotated, (cx_full, cy_full), (bx_full, by_full), (0, 255, 255), 2)
cv2.circle(annotated, (bx_full, by_full), br_full, (0, 0, 255), 3)
cv2.putText(annotated, f"{servo_name}: ({bx:.1f}, {by:.1f}) {angle:.1f} deg",
            (max(10, bx_full - 120), max(25, by_full - 15)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

out_file = f"{servo_name}_detected.jpg"
cv2.imwrite(out_file, annotated)
print(f"[SAVED] {out_file}")
