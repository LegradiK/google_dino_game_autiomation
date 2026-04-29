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
search_top = None
search_bottom = None
time_set = [10, 18, 24, 28, 30]
default_proximity = [400, 450, 150, 10]
add_proximity = [30, 30, 0, 0]
prev_frame = None
estimated_speed = 1.0
last_speed_check = 0
BASE_THRESHOLD = 10.0

def estimate_game_speed(detection_box):
    """
    Measures how much the screen changes between two frames.
    More pixel movement = faster game speed.
    Returns a float: low ~0.5 (slow), high ~3.0+ (fast)
    """
    global prev_frame

    frame = np.array(ImageGrab.grab(bbox=detection_box).convert('L'))

    if prev_frame is None or prev_frame.shape != frame.shape:
        prev_frame = frame
        return 1.0

    diff = np.abs(frame.astype(int) - prev_frame.astype(int)).mean()
    prev_frame = frame
    return diff  # higher = more movement = faster

def get_detection_box_from_proximity(best_region, prox):
    """
    Convert a proximity config [x_offset_start, x_offset_end, scan_height, margin]
    into an absolute screen bbox (x1, y1, x2, y2).
    
    prox = [x_start, x_end, height_above_ground, bottom_margin]
    """
    left, top, right, bottom = best_region
    x1 = left + prox[0]
    x2 = left + prox[1]
    y1 = bottom - prox[2]   # height_above_ground pixels above ground
    y2 = bottom - prox[3]   # bottom_margin pixels above ground
    return (x1, y1, x2, y2)

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
        # Detection box: scan ahead of dino (dino is near left edge of canvas)
        detection_box = get_detection_box_from_proximity(best_region, default_proximity)
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
        return False
    

def jump_dino():
    pyautogui.press('space')
    print("Jump")


def get_proximity_for_elapsed(elapsed):
    """
    Starts at default_proximity, adds add_proximity once per passed time threshold.
    """
    current_prox = list(default_proximity)  # copy so we don't mutate the original
    for i, t in enumerate(time_set):
        if elapsed >= t:
            current_prox = [current_prox[j] + add_proximity[j] for j in range(4)]
    print(current_prox)
    return current_prox

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
    
    filename = f"debug_view_{int(time.time())}.png"
    img.show()
    print(f"Debug image saved: {filename}")


# GAME AREA 

start_time = time.time()
max_duration = 120

dino_alive = True

start_game()
result = find_game_screen()

if result is None:
    print("Could not find game screen. Exiting.")
    exit()

best_region, detection_box, search_top, search_bottom = result
# print(result)

pyautogui.click(screenWidth // 2, screenHeight // 2)

time.sleep(0.5)

capture_baseline(detection_box)

time.sleep(0.5)

alerted = set()


while dino_alive:
    elapsed = time.time() - start_time

    if elapsed > max_duration:
        dino_alive = False
        print("Time limit reached.")
        break

    current_prox = get_proximity_for_elapsed(elapsed)
    new_box = get_detection_box_from_proximity(best_region, current_prox)

    if new_box != detection_box:
        detection_box = new_box
        prev_frame = None  # reset speed tracking when box changes
        capture_baseline(detection_box)
        print(f"[t={elapsed:.1f}s] Detection box updated → {detection_box}")
        # game_screenshot()
        # save_debug_image(best_region=best_region, detection_box=detection_box, search_top=search_top, search_bottom=search_bottom)
    
    estimated_speed = estimate_game_speed(detection_box)

    dynamic_threshold = max(5.0, min(15.0, BASE_THRESHOLD - (estimated_speed * 0.3)))
    print(f"speed={estimated_speed:.2f}  threshold={dynamic_threshold:.2f}")


    frame_edges = get_current_frame(detection_box=detection_box)
    if is_obstructed(frame_edges=frame_edges, threshold=dynamic_threshold):
        jump_dino()
        capture_baseline(detection_box)

        


