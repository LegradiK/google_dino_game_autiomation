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
best_region = None
frame_edges = None
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
    # print("full_screen.pgn is saved")

def find_game_screen():
    global best_region
    time.sleep(2)
    img = Image.open("full_screen.png")
    pixels = np.array(img)
    
    height, width = pixels.shape[:2]
    
    search_top = int(height * 0.25)
    search_bottom = int(height * 0.75)
    
    top = search_top 
    bottom = search_bottom
    left = 0
    right = width // 2
    
    best_region = (left, top, right, bottom)

    if best_region:
        left, top, right, bottom = best_region
        # print(f"Game region: left={left}, top={top}, right={right}, bottom={bottom}")

        # Detection box: scan ahead of dino (dino is near left edge of canvas)
        scan_x_start = left + 400
        scan_x_end = left + 450
        scan_y_start = bottom - 150
        scan_y_end = bottom - 10

        detection_box = (scan_x_start, scan_y_start, scan_x_end, scan_y_end)
        return best_region, detection_box, search_top, search_bottom
    else: 
        print("Game region not found. Try adjusting thresholds.")
        return None
    
def capture_baseline(detection_box):
    global baseline_edges
    # print(detection_box) 
    frame = ImageGrab.grab(bbox=detection_box).convert('L')
    edges = np.array(frame.filter(ImageFilter.FIND_EDGES))
    baseline_edges = edges
    # print(baseline_edges) 

def get_current_frame(detection_box):
    current_frame = ImageGrab.grab(bbox=detection_box).convert('L')
    frame_edges = np.array(current_frame.filter(ImageFilter.FIND_EDGES))
    return frame_edges

def is_obstructed(frame_edges, threshold=10):
    global baseline_edges
    
    if baseline_edges is None:
        baseline_edges = frame_edges  # auto-init if not set
        return False
    
    diff = np.abs(frame_edges.astype(int) - baseline_edges.astype(int))
    print(f"diff.mean() = {diff.mean():.2f}")
    
    if diff.mean() > threshold:
        print("Obstruction detected")
        baseline_edges = frame_edges  # update baseline so it doesn't re-trigger
        return True
    else:
        baseline_edges = frame_edges  # keep baseline rolling/fresh
        return False
    

def jump_dino():
    pyautogui.press('space')
    print("Jump")

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


# GAME AREA 

start_time = time.time()
max_duration = 60

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

time.sleep(0.5)

capture_baseline(detection_box)
# save_debug_image(best_region=best_region, detection_box=detection_box, search_top=search_top, search_bottom=search_bottom)

time.sleep(0.5)


while dino_alive:
    frame_edges = get_current_frame(detection_box=detection_box)
    if time.time() - start_time > max_duration:
        dino_alive = False
        print("Time limit reached.")
        break
    if is_obstructed(frame_edges=frame_edges, threshold=10):
        jump_dino()
        capture_baseline(detection_box)
       


