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
from PIL import ImageGrab, ImageDraw, Image, ImageFilter
import numpy as np

URL = "https://elgoog.im/dinosaur-game/"
detection_box = None
baseline_edges = None
screenWidth = None
screenHeight = None

def start_game():
    global screenWidth, screenHeight
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
    return screenWidth, screenHeight

def game_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("full_screen.png")

def find_game_screen():
    time.sleep(2)
    img = Image.open("full_screen.png")
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
        # print(f"Game region: left={left}, top={top}, right={right}, bottom={bottom}")
        
        # Annotate and save
        img_copy = img.copy()
        draw = ImageDraw.Draw(img_copy)
        draw.rectangle([left, top, right, bottom], outline="red", width=3)
        # img_copy.save("detected_game.png")
        # img_copy.show()
        # Look some pixels ahead of the dino's position
        scan_x_start = left + 350 
        scan_x_end = left + 450
        # Focus on the bottom half of the game area where cacti are
        scan_y_start = top + (bottom - top) // 2 
        scan_y_start = bottom - 60  
        scan_y_end = bottom - 10 

        detection_box = (scan_x_start, scan_y_start, scan_x_end, scan_y_end)
        
        return best_region, detection_box
    else:
        print("Game region not found. Try adjusting thresholds.")
        return None
    
def capture_baseline(detection_box):
    global baseline_edges
    print(detection_box)
    frame = ImageGrab.grab(bbox=detection_box).convert('L')
    edges = np.array(frame.filter(ImageFilter.FIND_EDGES))
    baseline_edges = edges
    # print(baseline_edges)


def is_obstructed(detection_box, threshold=20):
    global baseline_edges
    current_frame = ImageGrab.grab(bbox=detection_box).convert('L')
    edges = np.array(current_frame.filter(ImageFilter.FIND_EDGES))
    
    if baseline_edges is None:
        return False
    
    # Compare current edges to baseline — large diff means obstacle appeared
    diff = np.abs(edges.astype(int) - baseline_edges.astype(int))
    if diff.mean() > threshold:
        print("An obstruction is found.")
        return True
    else:
        return False

def jump_dino():
    pyautogui.click(screenWidth // 2, screenHeight // 2)
    pyautogui.press('space')


# game area

start_time = time.time()
max_duration = 120

dino_alive = True

start_game()
game_screenshot()
result = find_game_screen()

if result is None:
    print("Could not find game screen. Exiting.")
    exit()

best_region, detection_box = result   # ← now actually unpacked
# print(result)

pyautogui.click(screenWidth // 2, screenHeight // 2)

time.sleep(2)
capture_baseline(detection_box)
time.sleep(0.5)

while dino_alive:
    if time.time() - start_time > max_duration:
        print("Time limit reached.")
        break
    if is_obstructed(detection_box, threshold=20):
        jump_dino()
        time.sleep(0.4)
    time.sleep(0.05)
       


