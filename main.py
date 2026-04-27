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
searchTop = None
searchBottom = None

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
    print("full_screen.pgn is saved")

def find_game_screen():
    time.sleep(2)
    img = Image.open("full_screen.png")
    pixels = np.array(img)
    
    height, width = pixels.shape[:2]
    gray = np.mean(pixels, axis=2)
    
    search_top = int(height * 0.25)
    search_bottom = int(height * 0.75)

    best_region = None
    best_score = 0
    
    top = search_top 
    bottom = search_bottom
    
    strip = gray[top:bottom, :]
    white_ratio = np.sum(strip > 230) / strip.size
    dark_ratio = np.sum(strip < 80) / strip.size
    score = white_ratio * (1 + dark_ratio * 100)
    
    if white_ratio > 0.7 and dark_ratio > 0.001 and score > best_score:
        best_score = score
        
        # Find actual left/right boundaries of white region
        # Look at the middle row of this strip
        mid_row = gray[(top + bottom) // 2, :]
        white_cols = np.where(mid_row > 230)[0]
        if len(white_cols) > 100:  # must be wide enough
            actual_left = int(white_cols[0])
            actual_right = int(white_cols[-1])
            best_region = (actual_left, top, actual_right, bottom)

    if best_region:
        left, top, right, bottom = best_region
        print(f"Game region: left={left}, top={top}, right={right}, bottom={bottom}")

        # Detection box: scan ahead of dino (dino is near left edge of canvas)
        scan_x_start = left + 350
        scan_x_end = left + 450
        scan_y_start = bottom - 60
        scan_y_end = bottom - 10

        detection_box = (scan_x_start, scan_y_start, scan_x_end, scan_y_end)
        return best_region, detection_box, search_top, search_bottom
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

def save_debug_image(best_region, detection_box, search_top, search_bottom):
    img = Image.open("full_screen.png")
    draw = ImageDraw.Draw(img)
    
    left, top, right, bottom = best_region

    # Search boundary lines
    draw.line([(0, search_top), (img.width, search_top)], fill="green", width=2)
    draw.line([(0, search_bottom), (img.width, search_bottom)], fill="purple", width=2)

    # Game region in red
    draw.rectangle([left, top, right, bottom], outline="red", width=3)
    
    # Detection box in green
    dx1, dy1, dx2, dy2 = detection_box
    draw.rectangle([dx1, dy1, dx2, dy2], outline="orange", width=3)
    
    # Ground line in blue
    draw.line([(left, bottom - 10), (right, bottom - 10)], fill="blue", width=2)
    
    draw.text((dx1, dy1 - 15), "Detection Box", fill="orange")
    draw.text((left, top - 15), "Game Region", fill="red")
    draw.text((5, search_top - 15), "Search Top", fill="green")
    draw.text((5, search_bottom - 15), "Search Bottom", fill="purple")
    
    img.save("debug_view.png")
    img.show()


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

best_region, detection_box, search_top, search_bottom = result
# print(result)

pyautogui.click(screenWidth // 2, screenHeight // 2)

time.sleep(2)
capture_baseline(detection_box)
save_debug_image(best_region=best_region, detection_box=detection_box, search_top=search_top, search_bottom=search_bottom)
time.sleep(0.5)

while dino_alive:
    if time.time() - start_time > max_duration:
        print("Time limit reached.")
        break
    if is_obstructed(detection_box, threshold=20):
        jump_dino()
        time.sleep(0.4)
    time.sleep(0.05)
       


