import os

# Linux Wayland cannot run this code
# os.environ['DISPLAY'] = ':0'
# os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')
os.environ['XDG_SESSION_TYPE'] = 'x11'
os.environ['MOZ_ENABLE_WAYLAND'] = '0'
os.environ["GTK_PATH"] = ""
os.environ['GTK_MODULES'] = ''

import pyautogui
import subprocess
import time
from PIL import ImageGrab, ImageDraw
import numpy as np

URL = "https://elgoog.im/dinosaur-game/"


def start_game():
    """ Open the webpage, then start the game"""

    subprocess.Popen(['firefox', '--new-window', URL])
    time.sleep(3)  # increase number if Firefox loads slowly on your machine

    screenWidth, screenHeight = pyautogui.size()

    # click the screen to recognise
    pyautogui.click(screenWidth // 2, screenHeight // 2)
    time.sleep(0.5)

    # let the game start
    pyautogui.press('space')
    time.sleep(2)

def game_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("full_screen.png")

def find_game_screen():
    img = open("full_screen.png")
    pixels = np.array(img)
    
    height, width = pixels.shape[:2]
    gray = np.mean(pixels, axis=2)
    
    # Scan horizontally for a wide white band
    best_region = None
    best_score = 0
    
    step = 10
    for top in range(0, height - 100, step):
        for h in range(100, 300, step):
            bottom = top + h
            if bottom >= height:
                break
            
            strip = gray[top:bottom, :]
            
            # Score: high white pixel % but also has some dark pixels (dino/obstacles)
            white_ratio = np.sum(strip > 230) / strip.size
            dark_ratio = np.sum(strip < 80) / strip.size
            
            score = white_ratio * (1 + dark_ratio * 100)
            
            if white_ratio > 0.7 and dark_ratio > 0.001 and score > best_score:
                best_score = score
                best_region = (0, top, width, bottom)
    
    if best_region:
        left, top, right, bottom = best_region
        print(f"Game region: left={left}, top={top}, right={right}, bottom={bottom}")
        
        # Annotate and save
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        img_copy.save("detected_game.png")
        img_copy.show()
        
        return best_region
    else:
        print("Game region not found. Try adjusting thresholds.")
        return None
    


def check_for_obstruction():

    # define area to monitor 
    bbox = (600, 150)

start_game()
game_screenshot()
find_game_screen()


# game_on = True 

# while game_on:
#     start_game()
#     pass

