import time
from PIL import Image, ImageDraw, ImageGrab

DEBUG_DIR = "debug_pics"

def save_debug_image(controller, detector):
    ImageGrab.grab().save(f"{DEBUG_DIR}/full_screen.png")
    img = Image.open(f"{DEBUG_DIR}/full_screen.png")
    draw = ImageDraw.Draw(img)

    left, top, right, bottom = controller.best_region

    draw.line([(0, controller.search_top),    (img.width, controller.search_top)],    fill="green",  width=2)
    draw.line([(0, controller.search_bottom), (img.width, controller.search_bottom)], fill="purple", width=2)
    draw.rectangle([left, top, right, bottom], outline="red",  width=3)
    draw.line([(left, bottom - 10), (right, bottom - 10)],     fill="blue", width=2)

    cx1, cy1, cx2, cy2 = detector.cactus_box()
    draw.rectangle([cx1, cy1, cx2, cy2], outline="orange", width=3)
    draw.text((cx1, cy1 - 15), "Cactus box", fill="orange")

    px1, py1, px2, py2 = detector.ptero_box()
    draw.rectangle([px1, py1, px2, py2], outline="cyan", width=3)
    draw.text((px1, py1 - 15), "Ptero box", fill="cyan")

    filename = f"{DEBUG_DIR}/debug_view_{int(time.time())}.png"
    img.save(filename)
    print(f"Debug image saved: {filename}")