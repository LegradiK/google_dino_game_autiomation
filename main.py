import os
os.environ['XDG_SESSION_TYPE'] = 'x11'
os.environ['MOZ_ENABLE_WAYLAND'] = '0'
os.environ["GTK_PATH"] = ""
os.environ['GTK_MODULES'] = ''

import time
from game_controller import GameController
from obstacle_detector import ObstacleDetector
from dino import DinoPlayer
from debug import save_debug_image  # optional, see below

MAX_DURATION = 120

controller = GameController()
controller.start()
controller.screenshot()
controller.find_game_region()

detector = ObstacleDetector(controller.best_region)
detector.capture_baseline()

player = DinoPlayer(detector)

last_debug_save = 0

while True:
    if time.time() - player.start_time > MAX_DURATION:
        print("Time limit reached.")
        break

    if time.time() - last_debug_save > 5:
        save_debug_image(controller, detector)
        last_debug_save = time.time()

    if player.is_game_over():
        player.reset()
        break

    if detector.check():
        player.jump()
        detector.wait_for_landing()
        detector.capture_baseline()