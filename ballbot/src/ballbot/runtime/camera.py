import time
import os
import cv2
import numpy as np
from collections import deque
import threading

try:
    from picamera2 import Picamera2, Preview
    HAS_PICAMERA2 = True
except ImportError:
    HAS_PICAMERA2 = False


class Camera:
    def __init__(self, resolution=(640, 480), backend="auto", device=0):
        self.lower_black = np.array([0, 0, 0])
        self.upper_black = np.array([179, 255, 50])
        self.gray_threshold = 60

        self.queue = deque(maxlen=16)
        self.queue.append((100, 75))

        self.center_x = 100
        self.center_y = 75
        self.platform_radius = 75

        try:
            import json
            from pathlib import Path
            cfg_path = os.getenv("BALLBOT_CAM", str(Path(__file__).resolve().parents[3] / "config" / "camera.json"))
            if os.path.exists(cfg_path):
                data = json.loads(Path(cfg_path).read_text())
                if "target_x" in data and "target_y" in data:
                    self.center_x = int(round(float(data["target_x"])))
                    self.center_y = int(round(float(data["target_y"])))
                    self.queue.clear()
                    self.queue.append((self.center_x, self.center_y))
        except Exception:
            pass

        self.debug = False
        self.debug_mask = False
        self._last_debug_time = 0.0

        # Backend determination
        env_backend = os.getenv("BALLBOT_CAMERA_BACKEND", "").lower().strip()
        if env_backend:
            backend = env_backend

        self.backend = backend
        self.cap = None
        self.picam2 = None

        if self.backend == "auto":
            # Prefer USB camera if /dev/video0 exists or if picam2 fails
            if os.path.exists(f"/dev/video{device}"):
                self.backend = "usb"
            elif HAS_PICAMERA2:
                self.backend = "picam2"
            else:
                self.backend = "usb"

        if self.backend == "usb":
            print(f"[CAMERA] Initializing USB Camera (/dev/video{device})...", flush=True)
            self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, 30)

            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open USB camera on /dev/video{device}")
            print(f"[CAMERA] USB Camera opened: {resolution[0]}x{resolution[1]} @ 30 FPS", flush=True)

        elif self.backend == "picam2":
            if not HAS_PICAMERA2:
                raise RuntimeError("Picamera2 requested but not installed/available")
            print("[CAMERA] Initializing Picamera2 CSI Camera...", flush=True)
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": resolution, "format": "RGB888"},
                controls={"FrameDurationLimits": (8333, 8333)},
            )
            self.picam2.configure(config)
            self.picam2.start()
            print("[CAMERA] Picamera2 initialized successfully", flush=True)
        else:
            raise ValueError(f"Unknown camera backend: {self.backend}")

    def take_picture(self):
        if self.backend == "usb":
            ret, frame = self.cap.read()
            if not ret or frame is None:
                # Return empty frame matching expected dimension
                return np.zeros((150, 200, 3), dtype=np.uint8)
            # OpenCV captures BGR; convert to RGB for downstream coordinate tracking
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            scale = 200.0 / image.shape[1]
            frame_resized = cv2.resize(image, (200, int(image.shape[0] * scale)))
            return frame_resized
        else:
            image = self.picam2.capture_array()
            scale = 200.0 / image.shape[1]
            frame_resized = cv2.resize(image, (200, int(image.shape[0] * scale)))
            return frame_resized

    def display(self, image, window_name="Camera Output"):
        # Convert RGB to BGR for OpenCV display
        bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow(window_name, bgr)
        cv2.waitKey(1)

    def display_draw(self, image, center, window_name="Tracked Output"):
        x, y = center
        cv2.line(image, (x - 10, y), (x + 10, y), (0, 0, 255), 2)
        cv2.line(image, (x, y - 10), (x, y + 10), (0, 0, 255), 2)

    def terminate(self):
        if self.backend == "usb":
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        elif self.picam2 is not None:
            self.picam2.stop()
            self.picam2.close()
            self.picam2 = None
        cv2.destroyAllWindows()

    def coordinate(self, image):
        # 1. Primary Detector: Robust Hough Circle Detection
        frame_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.medianBlur(frame_gray, 5)

        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=20,
            param1=50,
            param2=20,
            minRadius=10,
            maxRadius=35,
        )

        if circles is not None:
            c_arr = np.uint16(np.around(circles))[0]
            valid_circles = []
            for c in c_arr:
                cx, cy, r = int(c[0]), int(c[1]), int(c[2])
                dist = np.hypot(cx - self.center_x, cy - self.center_y)
                # Keep detections within the platform bounds (~75px radius)
                if dist <= self.platform_radius:
                    valid_circles.append((dist, (cx, cy)))

            if valid_circles:
                # Pick the circle closest to the platform center / expected trajectory
                valid_circles.sort(key=lambda item: item[0])
                best_center = valid_circles[0][1]
                self.queue.append(best_center)
                return best_center[0], best_center[1], True

        # 2. Secondary Fallback: Platform-Masked Color / Threshold Contour Detection
        frame_blurred = cv2.GaussianBlur(image, (3, 3), 0)
        frame_hsv = cv2.cvtColor(frame_blurred, cv2.COLOR_RGB2HSV)

        mask_hsv = cv2.inRange(frame_hsv, self.lower_black, self.upper_black)
        mask_gray = cv2.threshold(frame_gray, self.gray_threshold, 255, cv2.THRESH_BINARY_INV)[1]
        mask_combined = cv2.bitwise_or(mask_hsv, mask_gray)

        # Restrict search strictly to inside the circular platform
        h_img, w_img = frame_gray.shape
        roi_mask = np.zeros((h_img, w_img), dtype=np.uint8)
        cv2.circle(roi_mask, (self.center_x, self.center_y), self.platform_radius, 255, -1)
        mask_combined = cv2.bitwise_and(mask_combined, mask_combined, mask=roi_mask)

        mask_eroded = cv2.erode(mask_combined, None, iterations=1)
        mask_dilated = cv2.dilate(mask_eroded, None, iterations=1)

        if getattr(self, "debug_mask", False):
            self._dbg_mask = mask_dilated
            self._dbg_gray = frame_gray

        valid_detections = []
        contours, _ = cv2.findContours(mask_dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)
            if radius < 8 or radius > 45:
                continue

            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            if perimeter == 0:
                continue

            circularity = (4 * np.pi * area) / (perimeter ** 2)
            if circularity < 0.5:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            valid_detections.append((area, (int(x + w / 2), int(y + h / 2))))

        if valid_detections:
            best_center = max(valid_detections, key=lambda item: item[0])[1]
            self.queue.append(best_center)
            return best_center[0], best_center[1], True
        else:
            now = time.time()
            last = getattr(self, "_last_debug_time", 0.0)
            if getattr(self, "debug", False) and now - last > 0.5:
                print(f"{now:.3f}  NO DETECTION  contours={len(contours)}", flush=True)
                self._last_debug_time = now

        # Keep queue stable for drawing, but report invalid to control
        last_center = self.queue[-1]
        self.queue.append(last_center)
        return last_center[0], last_center[1], False


if __name__ == "__main__":
    cam = Camera()
    cam.debug = True
    cam.debug_mask = False

    try:
        for _ in range(50):
            img = cam.take_picture()
            x, y, valid = cam.coordinate(img)
            cam.display_draw(img, (x, y))
            if time.time() - getattr(cam, "_tprint", 0) > 0.5:
                print("center:", (x, y), "valid:", valid, flush=True)
                cam._tprint = time.time()
            time.sleep(0.033)
    finally:
        cam.terminate()
