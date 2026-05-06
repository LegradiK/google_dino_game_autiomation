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
        self.last_game_over_check = time.time()

    def jump(self):
        pyautogui.press('space')
        print("Jump")

    def is_game_over(self):
        # only check every 2 seconds
        if time.time() - self.last_game_over_check < 2.0:
            return False
        self.last_game_over_check = time.time()
        
        box = self.detector.detection_box()
        frame1 = np.array(ImageGrab.grab(bbox=box).convert('L'))
        time.sleep(0.3)  # short diff window is enough
        frame2 = np.array(ImageGrab.grab(bbox=box).convert('L'))
        diff = np.abs(frame1.astype(int) - frame2.astype(int)).mean()
        return diff == 0.0 and time.time() - self.start_time > 5

    def reset(self):
        print("Dino died. Resetting.")
        time.sleep(0.5)
        self.jump_count = 0
        self.start_time = time.time()
        self.detector.reset()
        print("Reset complete.")