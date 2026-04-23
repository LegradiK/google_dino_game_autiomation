import os
os.environ['DISPLAY'] = ':0'
os.environ['XAUTHORITY'] = os.path.expanduser('~/.Xauthority')
os.environ['XDG_SESSION_TYPE'] = 'x11'
os.environ['MOZ_ENABLE_WAYLAND'] = '0'
os.environ['GTK_MODULES'] = ''

import pyautogui
import subprocess
import time
from PIL import ImageGrab

URL = "https://elgoog.im/dinosaur-game/"

subprocess.Popen(['firefox', '--new-window', URL])
time.sleep(5)  # increase to 6-7 if Firefox loads slowly on your machine

screenWidth, screenHeight = pyautogui.size()
pyautogui.click(screenWidth // 2, screenHeight // 2)
time.sleep(0.5)
pyautogui.press('space')