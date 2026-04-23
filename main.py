import os

# Linux Wayland cannot run this code
# os.environ['DISPLAY'] = ':0'
# os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')
os.environ['XDG_SESSION_TYPE'] = 'x11'
os.environ['MOZ_ENABLE_WAYLAND'] = '0'
os.environ['GTK_MODULES'] = ''

import pyautogui
import subprocess
import time
from PIL import ImageGrab

URL = "https://elgoog.im/dinosaur-game/"


def start_game():
    """ Open the webpage, then start the game"""

    subprocess.Popen(['firefox', '--new-window', URL])
    time.sleep(2)  # increase number if Firefox loads slowly on your machine

    screenWidth, screenHeight = pyautogui.size()

    # click the screen to recognise
    pyautogui.click(screenWidth // 2, screenHeight // 2)
    time.sleep(0.5)

    # let the game start
    pyautogui.press('space')

def check_for_obstruction():

    # define area to monitor 
    bbox = (600, 150)

start_game()
 

# game_on = True

# while game_on:
#     start_game()
#     pass

