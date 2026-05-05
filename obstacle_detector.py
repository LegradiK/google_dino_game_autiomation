import numpy as np
import time
from PIL import ImageGrab, ImageFilter, Image
from config import DEBUG_DIR

class ObstacleDetector:
    THRESHOLD = 0.3
    PROXIMITY = [420, 500, 130, 27]  # wide enough for both cactus and ptero

    def __init__(self, best_region):
        self.best_region = best_region
        self.proximity = self.PROXIMITY[:]
        self.baseline = None

    def _box_from_proximity(self, prox):
        left, top, right, bottom = self.best_region
        return (left + prox[0], bottom - prox[2], left + prox[1], bottom - prox[3])

    def detection_box(self):
        return self._box_from_proximity(self.proximity)

    def _grab_edges(self, box):
        return np.array(ImageGrab.grab(bbox=box).convert('L').filter(ImageFilter.FIND_EDGES))

    def capture_baseline(self):
        box = self.detection_box()
        print(f"Detection box: {box}")

        ImageGrab.grab(bbox=box).save(f"{DEBUG_DIR}/baseline_raw.png")
        self.baseline = self._grab_edges(box)
        Image.fromarray(self.baseline).save(f"{DEBUG_DIR}/baseline_edges.png")

        print(f"Best region: {self.best_region}")
        print(f"Detection box: {self.detection_box()}")

    def reset(self):
        self.proximity = self.PROXIMITY[:]
        self.baseline = None
        self.capture_baseline()

    def check(self):
        if self.baseline is None:
            return False
        frame = self._grab_edges(self.detection_box())
        diff = np.abs(frame.astype(int) - self.baseline.astype(int)).mean()
        print(f"Obstacle diff={diff:.2f}")
        if diff > self.THRESHOLD:
            print("Obstacle detected")
            return True
        self.baseline = frame 
        return False
    
    def wait_for_landing(self):
        prev = self._grab_edges(self.detection_box())
        while True:
            time.sleep(0.05)
            curr = self._grab_edges(self.detection_box())
            diff = np.abs(curr.astype(int) - prev.astype(int)).mean()
            if diff < 1.0:  # stable — dino has landed
                break
            prev = curr
        self.baseline = curr
