import time
from PIL import Image, ImageDraw, ImageGrab
from config import DEBUG_DIR

def save_debug_image(controller, detector):
    ImageGrab.grab().save(f"{DEBUG_DIR}/full_screen.png")
    img = Image.open(f"{DEBUG_DIR}/full_screen.png")
    draw = ImageDraw.Draw(img)

    left, top, right, bottom = controller.best_region
    draw.line([(0, controller.search_top),    (img.width, controller.search_top)],    fill="green",  width=2)
    draw.line([(0, controller.search_bottom), (img.width, controller.search_bottom)], fill="purple", width=2)
    draw.rectangle([left, top, right, bottom], outline="red", width=3)
    draw.line([(left, bottom - 10), (right, bottom - 10)], fill="blue", width=2)

    x1, y1, x2, y2 = detector.detection_box()
    draw.rectangle([x1, y1, x2, y2], outline="orange", width=3)
    draw.text((x1, y1 - 15), "Detection box", fill="orange")

    filename = f"{DEBUG_DIR}/debug_view_{int(time.time())}.png"
    img.save(filename)
    print(f"Debug image saved: {filename}")

    