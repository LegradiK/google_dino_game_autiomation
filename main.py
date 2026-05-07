import os
os.environ['XDG_SESSION_TYPE'] = 'x11'
os.environ['MOZ_ENABLE_WAYLAND'] = '0'
os.environ["GTK_PATH"] = ""
os.environ['GTK_MODULES'] = ''

import time
from game_controller import GameController
from obstacle_detector import ObstacleDetector
from dino import DinoPlayer
# from debug import save_debug_image  # for debugging purpsoes


MAX_DURATION = 120
JUMP_COOLDOWN = 0.3
BASELINE_DELAY = 0.35
POST_JUMP_THRESHOLD = 15

last_jump_time = 0
baseline_refreshed = False
pending_jump = False
last_debug_save = 0
last_jump_time = 0
pending_jump_time = 0

controller = GameController()
controller.start()
controller.screenshot()
controller.find_game_region()

detector = ObstacleDetector(controller.best_region)
detector.capture_baseline()

player = DinoPlayer(detector)

while True:
    if time.time() - player.start_time > MAX_DURATION:
        print("Time limit reached.")
        break

    ## For checking if detection_box is in the right position when game is ongoing
    # if time.time() - last_debug_save > 5:
    #     save_debug_image(controller, detector)
    #     last_debug_save = time.time()

    if player.is_game_over():
        print("Game Over")
        break

    now = time.time()
    time_since_jump = now - last_jump_time

    # Refresh baseline once dino has landed — no continue, keep detecting
    if time_since_jump >= BASELINE_DELAY and not baseline_refreshed and last_jump_time > 0:
        detector.capture_baseline()
        baseline_refreshed = True

    # Stricter threshold during recovery to suppress landing noise
    if 0 < time_since_jump < JUMP_COOLDOWN:
        detector.THRESHOLD = POST_JUMP_THRESHOLD
    else:
        detector.THRESHOLD = 5

    # Fire pending jump as soon as cooldown allows
    if pending_jump and time_since_jump >= JUMP_COOLDOWN:
        if time.time() - pending_jump_time < 0.5:   # expire after 0.5s
            print("Firing pending jump")
            player.jump()
            last_jump_time = time.time()
            baseline_refreshed = False
        else:
            print("Pending jump expired — obstacle passed")
        pending_jump = False
        continue

    if detector.check():
        if time_since_jump >= JUMP_COOLDOWN:
            player.jump()
            print("Jump")
            last_jump_time = time.time()
            baseline_refreshed = False
        else:
            pending_jump = True
            pending_jump_time = time.time() 
            print("Jump queued (in cooldown)")