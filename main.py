import pyautogui
from PIL import ImageGrab

# Google Dinosaur Game website
URL = "https://elgoog.im/dinosaur-game/"

# Get the size of the primary monitor.
screenWidth, screenHeight = pyautogui.size() 

print(screenHeight, screenWidth)