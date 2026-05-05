import subprocess
import time
import os
import pyautogui
from PIL import ImageGrab
import numpy as np
from config import DEBUG_DIR



class GameController:
    URL = "https://elgoog.im/dinosaur-game/"

    def __init__(self):
        self.screen_width = None
        self.screen_height = None
        self.best_region = None
        self.search_top = None
        self.search_bottom = None

    def start(self):
        subprocess.Popen(['firefox', '--new-window', self.URL])
        time.sleep(3)
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.click(self.screen_width // 2, self.screen_height // 2)
        time.sleep(0.3)
        pyautogui.press('space')
        time.sleep(2)

    def screenshot(self):
        os.makedirs(DEBUG_DIR, exist_ok=True)
        ImageGrab.grab().save(f"{DEBUG_DIR}/full_screen.png")

    def find_game_region(self):
        from PIL import Image
        img = Image.open(f"{DEBUG_DIR}/full_screen.png")
        h, w = np.array(img).shape[:2]
        self.search_top = int(h * 0.25)
        self.search_bottom = int(h * 0.75)
        self.best_region = (0, self.search_top, w // 2, self.search_bottom)