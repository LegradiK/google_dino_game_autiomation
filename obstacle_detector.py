import numpy as np
import time
from PIL import ImageGrab

class ObstacleDetector:
    THRESHOLD = 5
    PROXIMITY = [420, 580, 140, 8]

    def __init__(self, best_region):
        self.best_region = best_region
        self.proximity = self.PROXIMITY[:]
        self.baseline = None

    def _box_from_proximity(self, prox):
        left, top, right, bottom = self.best_region
        return (left + prox[0], bottom - prox[2], left + prox[1], bottom - prox[3])

    def detection_box(self):
        return self._box_from_proximity(self.proximity)

    def _grab_gray(self, box):
        return np.array(ImageGrab.grab(bbox=box).convert('L'))

    def check(self):
        if self.baseline is None:
            return False
        frame = self._grab_gray(self.detection_box())
        diff = np.abs(frame.astype(int) - self.baseline.astype(int)).mean()
        print(f"Obstacle diff={diff:.4f}")
        if diff > self.THRESHOLD:
            # confirm with second frame
            time.sleep(0.02)
            frame2 = self._grab_gray(self.detection_box())
            diff2 = np.abs(frame2.astype(int) - self.baseline.astype(int)).mean()
            return diff2 > self.THRESHOLD
        return False

    def capture_baseline(self, save=False):
        box = self.detection_box()
        self.baseline = self._grab_gray(box)
        ## for testing/debugging purpose
        ## check if it captures baseline correctly
        # if save:
        #     from PIL import Image, ImageDraw
        #     import os
        #     from config import DEBUG_DIR
        #     os.makedirs(DEBUG_DIR, exist_ok=True)
            
        #     # full screenshot with detection box drawn
        #     screen = ImageGrab.grab()
        #     draw = ImageDraw.Draw(screen)
        #     x1, y1, x2, y2 = box
        #     draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
        #     draw.text((x1, y1 - 15), f"Detection box {box}", fill="red")
            
        #     filename = f"{DEBUG_DIR}/baseline_{int(time.time())}.png"
        #     screen.save(filename)
        #     print(f"Baseline saved: {filename}")

    def reset(self):
        self.proximity = self.PROXIMITY[:]
        self.baseline = None
        time.sleep(0.2)
        self.capture_baseline()