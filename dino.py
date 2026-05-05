import time
import pyautogui
import numpy as np
from PIL import ImageGrab

MAX_JUMPS_PER_SHIFT = 5
SHIFT_PER_JUMP = [30, 30, 0, 0]
MAX_X = [600, 630]

class DinoPlayer:
    def __init__(self, detector):
        self.detector = detector
        self.jump_count = 0
        self.start_time = time.time()

    def jump(self):
        pyautogui.press('space')
        self.jump_count += 1
        print(f"Jump #{self.jump_count}")

        if self.jump_count % MAX_JUMPS_PER_SHIFT == 0:
            d = self.detector
            for prox in (d.cactus_proximity, d.pterodactyl_proximity):
                prox[0] = min(prox[0] + SHIFT_PER_JUMP[0], MAX_X[0])
                prox[1] = min(prox[1] + SHIFT_PER_JUMP[1], MAX_X[1])

    def is_game_over(self):
        box = self.detector.cactus_box()
        frame1 = np.array(ImageGrab.grab(bbox=box).convert('L'))
        time.sleep(1)
        frame2 = np.array(ImageGrab.grab(bbox=box).convert('L'))
        diff = np.abs(frame1.astype(int) - frame2.astype(int)).mean()
        print(f"motion diff={diff:.2f}")
        return diff == 0.0 and time.time() - self.start_time > 5

    def reset(self):
        print("Dino died. Resetting.")
        time.sleep(0.5)
        self.jump_count = 0
        self.start_time = time.time()
        self.detector.reset()
        print("Reset complete.")