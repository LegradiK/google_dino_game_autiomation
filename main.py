import os

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
time_set = [15, 23, 29, 33, 35]
default_proximity = [450, 500, 150, 5]
THRESHOLD = 8
still_frames = 0
jump_count = 0
MAX_JUMPS_PER_SHIFT = 5  # shift box every 3 jumps
SHIFT_PER_JUMP = [30, 30, 0, 0]  # how much to shift each time
MAX_PROXIMITY = [600, 650, 150, 5]  # don't shift beyond this


def get_detection_box_from_proximity(best_region, prox):
    """prox = [x_start, x_end, height_above_ground, bottom_margin]"""
    left, top, right, bottom = best_region
    x1 = left + prox[0]
    x2 = left + prox[1]
    y1 = bottom - prox[2]
    y2 = bottom - prox[3]
    return (x1, y1, x2, y2)


def start_game():
    global screenWidth, screenHeight
    subprocess.Popen(['firefox', '--new-window', URL])
    time.sleep(3)
    screenWidth, screenHeight = pyautogui.size()
    pyautogui.click(screenWidth // 2, screenHeight // 2)
    time.sleep(0.3)
    pyautogui.press('space')
    time.sleep(2)
    return screenWidth, screenHeight


def game_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("full_screen.png")


def find_game_screen():
    global best_region
    img = Image.open("full_screen.png")
    pixels = np.array(img)
    height, width = pixels.shape[:2]

    search_top = int(height * 0.25)
    search_bottom = int(height * 0.75)
    best_region = (0, search_top, width // 2, search_bottom)

    if best_region:
        detection_box = get_detection_box_from_proximity(best_region, default_proximity)
        return best_region, detection_box, search_top, search_bottom
    else:
        print("Game region not found.")
        return None
    
def move_detection_box(detection_box):
    global add_proximity
    start_x, end_x, top, bottom = detection_box
    add_start_x, add_end_x, add_top, add_bottom = add_proximity
    new_start_x = start_x + add_start_x
    new_end_x = end_x + add_end_x
    new_top = top + add_top
    new_bottom = bottom + add_bottom
    detection_box = new_start_x, new_end_x, new_top, new_bottom

def capture_baseline(detection_box):
    global baseline_edges
    frame = ImageGrab.grab(bbox=detection_box).convert('L')
    edges = np.array(frame.filter(ImageFilter.FIND_EDGES))
    baseline_edges = edges


def get_current_frame(grabbed_frame):
    gray = grabbed_frame.convert('L')
    return np.array(gray.filter(ImageFilter.FIND_EDGES))


def is_obstructed(frame_edges):
    global baseline_edges
    if baseline_edges is None:
        baseline_edges = frame_edges
        return False
    diff = np.abs(frame_edges.astype(int) - baseline_edges.astype(int))
    print(f"diff.mean() = {diff.mean():.2f}")
    if diff.mean() > THRESHOLD:
        print("Obstruction detected")
        baseline_edges = frame_edges
        return True
    return False


def jump_dino():
    global jump_count, detection_box, baseline_edges

    pyautogui.press('space')
    jump_count += 1
    print(f"Jump #{jump_count}")

    # shift detection box every MAX_JUMPS_PER_SHIFT jumps
    if jump_count % MAX_JUMPS_PER_SHIFT == 0:
        x1, y1, x2, y2 = detection_box
        new_x1 = min(x1 + SHIFT_PER_JUMP[0], MAX_PROXIMITY[0])
        new_x2 = min(x2 + SHIFT_PER_JUMP[1], MAX_PROXIMITY[1])
        new_box = (new_x1, y1, new_x2, y2)

        if new_box != detection_box:
            detection_box = new_box
            baseline_edges = None
            capture_baseline(detection_box)
            print(f"Detection box shifted → {detection_box}")


def save_debug_image(best_region, detection_box, search_top, search_bottom):
    img = Image.open("full_screen.png")
    draw = ImageDraw.Draw(img)
    left, top, right, bottom = best_region

    draw.line([(0, search_top), (img.width, search_top)], fill="green", width=2)
    draw.line([(0, search_bottom), (img.width, search_bottom)], fill="purple", width=2)
    draw.rectangle([left, top, right, bottom], outline="red", width=3)

    dx1, dy1, dx2, dy2 = detection_box
    draw.rectangle([dx1, dy1, dx2, dy2], outline="orange", width=3)
    draw.line([(left, bottom - 10), (right, bottom - 10)], fill="blue", width=2)

    draw.text((dx1, dy1 - 15), "Detection Box", fill="orange")
    draw.text((left, top - 15), "Game Region", fill="red")
    draw.text((5, search_top - 15), "Search Top", fill="green")
    draw.text((5, search_bottom - 15), "Search Bottom", fill="purple")

    filename = f"debug_view_{int(time.time())}.png"
    img.save(filename)
    print(f"Debug image saved: {filename}")


def is_game_over(frame_edges):
    global still_frames
    if time.time() - start_time < 4:
        still_frames = 0
        return False
    if baseline_edges is None:
        return False

    diff = np.abs(frame_edges.astype(int) - baseline_edges.astype(int)).mean()

    if diff == 0.0:
        still_frames += 1
    else:
        still_frames = 0

    return still_frames > 20

def reset_game():
    global detection_box, baseline_edges, start_time, still_frames, jump_count

    print("Dino died. Resetting.")
    time.sleep(0.5)
    # pyautogui.press('space')
    # time.sleep(2)

    detection_box  = get_detection_box_from_proximity(best_region, default_proximity)
    baseline_edges = None
    still_frames   = 0
    jump_count     = 0
    start_time     = time.time()

    capture_baseline(detection_box)
    print("Reset complete.")


# main

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

capture_baseline(detection_box)


while dino_alive:
    if time.time() - start_time > max_duration:
        dino_alive = False
        print("Time limit reached.")
        break

    grabbed = ImageGrab.grab(bbox=detection_box)
    frame_edges = get_current_frame(grabbed)

    if is_game_over(frame_edges):
        reset_game()
        break

    if is_obstructed(frame_edges):
        save_debug_image(best_region, detection_box, search_top, search_bottom)
        jump_dino()
        # save_debug_image(best_region, detection_box, search_top, search_bottom)
        time.sleep(0.1)
        capture_baseline(detection_box)

