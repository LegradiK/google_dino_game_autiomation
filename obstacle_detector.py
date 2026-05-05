import numpy as np
from PIL import ImageGrab, ImageFilter

class ObstacleDetector:
    THRESHOLD = 10

    CACTUS_PROXIMITY      = [450, 480, 100, 27]
    PTERODACTYL_PROXIMITY = [450, 480, 130, 70]

    def __init__(self, best_region):
        self.best_region = best_region
        self.cactus_proximity = self.CACTUS_PROXIMITY[:]
        self.pterodactyl_proximity = self.PTERODACTYL_PROXIMITY[:]
        self.baseline_cactus = None
        self.baseline_ptero = None

    def _box_from_proximity(self, prox):
        left, top, right, bottom = self.best_region
        return (left + prox[0], bottom - prox[2], left + prox[1], bottom - prox[3])

    def cactus_box(self):
        return self._box_from_proximity(self.cactus_proximity)

    def ptero_box(self):
        return self._box_from_proximity(self.pterodactyl_proximity)

    def _grab_edges(self, box):
        return np.array(ImageGrab.grab(bbox=box).convert('L').filter(ImageFilter.FIND_EDGES))

    def capture_baselines(self):
        self.baseline_cactus = self._grab_edges(self.cactus_box())
        self.baseline_ptero  = self._grab_edges(self.ptero_box())

    def reset(self):
        self.cactus_proximity      = self.CACTUS_PROXIMITY[:]
        self.pterodactyl_proximity = self.PTERODACTYL_PROXIMITY[:]
        self.baseline_cactus = None
        self.baseline_ptero  = None
        self.capture_baselines()

    def _is_obstructed(self, current, baseline, name):
        if baseline is None:
            return False
        diff = np.abs(current.astype(int) - baseline.astype(int)).mean()
        print(f"{name} diff={diff:.2f}")
        if diff > self.THRESHOLD:
            print(f"{name} detected")
            return True
        return False

    def check(self):
        frame_cactus = self._grab_edges(self.cactus_box())
        frame_ptero  = self._grab_edges(self.ptero_box())
        cactus_hit = self._is_obstructed(frame_cactus, self.baseline_cactus, "Cactus")
        ptero_hit  = self._is_obstructed(frame_ptero,  self.baseline_ptero,  "Pterodactyl")
        if cactus_hit:
            self.baseline_cactus = frame_cactus
        if ptero_hit:
            self.baseline_ptero = frame_ptero
        return cactus_hit or ptero_hit