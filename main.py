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
best_region   = None
screenWidth   = None
screenHeight  = None
search_top    = None
search_bottom = None
baseline_cactus = None
baseline_ptero  = None
cactus_proximity      = [450, 480, 100, 27]
pterodactyl_proximity = [450, 480, 130, 70]
THRESHOLD          = 10
jump_count         = 0
last_debug_save = 0
MAX_JUMPS_PER_SHIFT = 5
SHIFT_PER_JUMP     = [30, 30, 0, 0]
MAX_X              = [600, 630]


def get_detection_box_from_proximity(best_region, prox):
    left, top, right, bottom = best_region
    return (left + prox[0], bottom - prox[2], left + prox[1], bottom - prox[3])


def get_cactus_box():
    return get_detection_box_from_proximity(best_region, cactus_proximity)


def get_pterodactyl_box():
    return get_detection_box_from_proximity(best_region, pterodactyl_proximity)


def start_game():
    global screenWidth, screenHeight
    subprocess.Popen(['firefox', '--new-window', URL])
    time.sleep(3)
    screenWidth, screenHeight = pyautogui.size()
    pyautogui.click(screenWidth // 2, screenHeight // 2)
    time.sleep(0.3)
    pyautogui.press('space')
    time.sleep(1.5)


def game_screenshot():
    ImageGrab.grab().save("full_screen.png")


def find_game_screen():
    global best_region, search_top, search_bottom
    img = Image.open("full_screen.png")
    h, w = np.array(img).shape[:2]
    search_top    = int(h * 0.25)
    search_bottom = int(h * 0.75)
    best_region   = (0, search_top, w // 2, search_bottom)


def capture_baseline_cactus():
    global baseline_cactus
    frame = ImageGrab.grab(bbox=get_cactus_box()).convert('L')
    baseline_cactus = np.array(frame.filter(ImageFilter.FIND_EDGES))


def capture_baseline_ptero():
    global baseline_ptero
    frame = ImageGrab.grab(bbox=get_pterodactyl_box()).convert('L')
    baseline_ptero = np.array(frame.filter(ImageFilter.FIND_EDGES))


def get_current_frame(grabbed):
    return np.array(grabbed.convert('L').filter(ImageFilter.FIND_EDGES))


def is_obstructed_cactus(frame_edges):
    global baseline_cactus
    if baseline_cactus is None:
        baseline_cactus = frame_edges
        return False
    diff = np.abs(frame_edges.astype(int) - baseline_cactus.astype(int)).mean()
    print(f"cactus diff={diff:.2f}")
    if diff > THRESHOLD:
        print("Cactus detected")
        baseline_cactus = frame_edges
        return True
    return False


def is_obstructed_ptero(frame_edges):
    global baseline_ptero
    if baseline_ptero is None:
        baseline_ptero = frame_edges
        return False
    diff = np.abs(frame_edges.astype(int) - baseline_ptero.astype(int)).mean()
    print(f"ptero diff={diff:.2f}")
    if diff > THRESHOLD:
        print("Pterodactyl detected")
        baseline_ptero = frame_edges
        return True
    return False


def jump_dino():
    global jump_count, cactus_proximity, pterodactyl_proximity

    pyautogui.press('space')
    jump_count += 1
    print(f"Jump #{jump_count}")

    if jump_count % MAX_JUMPS_PER_SHIFT == 0:
        cactus_proximity[0]      = min(cactus_proximity[0]      + SHIFT_PER_JUMP[0], MAX_X[0])
        cactus_proximity[1]      = min(cactus_proximity[1]      + SHIFT_PER_JUMP[1], MAX_X[1])
        pterodactyl_proximity[0] = min(pterodactyl_proximity[0] + SHIFT_PER_JUMP[0], MAX_X[0])
        pterodactyl_proximity[1] = min(pterodactyl_proximity[1] + SHIFT_PER_JUMP[1], MAX_X[1])
        print(f"Boxes shifted → cactus={get_cactus_box()} ptero={get_pterodactyl_box()}")


def save_debug_image():
    game_screenshot()
    img = Image.open("full_screen.png")
    draw = ImageDraw.Draw(img)
    left, top, right, bottom = best_region

    draw.line([(0, search_top),    (img.width, search_top)],    fill="green",  width=2)
    draw.line([(0, search_bottom), (img.width, search_bottom)], fill="purple", width=2)
    draw.rectangle([left, top, right, bottom], outline="red", width=3)
    draw.line([(left, bottom - 10), (right, bottom - 10)], fill="blue", width=2)

    cx1, cy1, cx2, cy2 = get_cactus_box()
    draw.rectangle([cx1, cy1, cx2, cy2], outline="orange", width=3)
    draw.text((cx1, cy1 - 15), "Cactus Box", fill="orange")

    px1, py1, px2, py2 = get_pterodactyl_box()
    draw.rectangle([px1, py1, px2, py2], outline="cyan", width=3)
    draw.text((px1, py1 - 15), "Ptero Box", fill="cyan")

    filename = f"debug_view_{int(time.time())}.png"
    img.save(filename)
    print(f"Debug image saved: {filename}")


def is_game_over():
    frame1 = np.array(ImageGrab.grab(bbox=get_cactus_box()).convert('L'))
    time.sleep(0.05)
    frame2 = np.array(ImageGrab.grab(bbox=get_cactus_box()).convert('L'))
    diff = np.abs(frame1.astype(int) - frame2.astype(int)).mean()
    print(f"motion diff={diff:.2f}")
    return diff == 0.0 and time.time() - start_time > 5


def reset_game():
    global baseline_cactus, baseline_ptero, start_time, jump_count
    global cactus_proximity, pterodactyl_proximity

    print("Dino died. Resetting.")
    time.sleep(0.5)
    # pyautogui.press('space') 
    # time.sleep(2)

    cactus_proximity      = [460, 480, 100, 27]
    pterodactyl_proximity = [460, 480, 130, 70]
    baseline_cactus = None
    baseline_ptero  = None
    jump_count      = 0
    start_time      = time.time()

    capture_baseline_cactus()
    capture_baseline_ptero()
    print("Reset complete.")


# main

start_time = time.time()
max_duration = 120
dino_alive = True

start_game()
game_screenshot()
find_game_screen()

capture_baseline_cactus()
capture_baseline_ptero()
save_debug_image()

while dino_alive:
    if time.time() - start_time > max_duration:
        dino_alive = False
        print("Time limit reached.")
        break

    if time.time() - last_debug_save > 1:
        save_debug_image()
        last_debug_save = time.time()

    grabbed_cactus     = ImageGrab.grab(bbox=get_cactus_box())
    frame_edges_cactus = get_current_frame(grabbed_cactus)

    grabbed_ptero      = ImageGrab.grab(bbox=get_pterodactyl_box())
    frame_edges_ptero  = get_current_frame(grabbed_ptero)

    if is_game_over():
        reset_game()
        break

    if is_obstructed_cactus(frame_edges_cactus) or is_obstructed_ptero(frame_edges_ptero):
        jump_dino()
        time.sleep(0.1)
        capture_baseline_cactus()
        capture_baseline_ptero()