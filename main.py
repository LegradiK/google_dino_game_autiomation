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
    
    ## For checking if detection_box is in the right position when game is ongoing
    # if time.time() - last_debug_save > 5:
    #     save_debug_image(controller, detector)
    #     last_debug_save = time.time()

    if player.is_game_over():
        print("Game Over")
        break

    if detector.check():
        player.jump()
        time.sleep(0.15)     
        detector.capture_baseline(save=True) 
        time.sleep(0.3) 