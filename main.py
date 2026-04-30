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
default_proximity = [400, 450, 150, 5]
add_proximity = [30, 30, 0, 0]
THRESHOLD = 10


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
    time.sleep(0.5)
    pyautogui.press('space')
    time.sleep(2)
    return screenWidth, screenHeight


def game_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("full_screen.png")


def find_game_screen():
    global best_region
    time.sleep(2)
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


def capture_baseline(detection_box):
    global baseline_edges
    frame = ImageGrab.grab(bbox=detection_box).convert('L')
    edges = np.array(frame.filter(ImageFilter.FIND_EDGES))
    baseline_edges = edges


def get_current_frame(detection_box):
    current_frame = ImageGrab.grab(bbox=detection_box).convert('L')
    return np.array(current_frame.filter(ImageFilter.FIND_EDGES))


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
    pyautogui.press('space')
    print("Jump")


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


def is_game_over():
    global baseline_edges
    if time.time() - start_time < 4:
        return False
    # if screen is completely static (diff = 0), dino has died
    frame = np.array(ImageGrab.grab(bbox=detection_box).convert('L'))
    if baseline_edges is None:
        return False
    frame_edges = np.array(Image.fromarray(frame).filter(ImageFilter.FIND_EDGES))
    diff = np.abs(frame_edges.astype(int) - baseline_edges.astype(int)).mean()
    return diff == 0.0


def reset_game():
    global detection_box, baseline_edges, start_time

    print("Dino died. Resetting.")
    time.sleep(0.5)
    pyautogui.press('space')
    time.sleep(2)

    detection_box  = get_detection_box_from_proximity(best_region, default_proximity)
    baseline_edges = None
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

time.sleep(0.5)


while dino_alive:
    if time.time() - start_time > max_duration:
        dino_alive = False
        print("Time limit reached.")
        break

    if is_game_over():
        reset_game()
        continue

    frame_edges = get_current_frame(detection_box=detection_box)
    if is_obstructed(frame_edges):
        save_debug_image(best_region=best_region, detection_box=detection_box,
                 search_top=search_top, search_bottom=search_bottom)
        jump_dino()
        time.sleep(0.2)
        capture_baseline(detection_box)