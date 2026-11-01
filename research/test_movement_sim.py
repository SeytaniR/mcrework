from PIL import Image
import math

col_img = Image.open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\collision.png").convert("L")
w, h = col_img.size

def is_walkable(x, y):
    ix = int(math.floor(x))
    iy = int(math.floor(y))
    if not (0 <= ix < w and 0 <= iy < h): return False
    return col_img.getpixel((ix, iy)) > 128

def try_step(from_x, from_y, step_dx, step_dy):
    next_x = from_x + step_dx
    next_y = from_y + step_dy

    if is_walkable(next_x, next_y):
        return next_x, next_y, False

    # Slide X
    if is_walkable(next_x, from_y):
        return next_x, from_y, True

    # Slide Y
    if is_walkable(from_x, next_y):
        return from_x, next_y, True

    return from_x, from_y, True

# Test walking South from (1000, 1000) for 200 pixels
px, py = 1000.0, 1000.0
print(f"Starting at ({px}, {py}), is_walkable={is_walkable(px, py)}")

for step in range(200):
    px, py, hit = try_step(px, py, 0.0, 3.0)
    if hit:
        print(f"Stopped walking South at step {step}: ({px:.1f}, {py:.1f}), obstacle ahead={not is_walkable(px, py + 3)}")
        break

# Test walking SE from (1000, 1000)
px, py = 1000.0, 1000.0
for step in range(200):
    px, py, hit = try_step(px, py, 2.12, 2.12)
    if hit:
        print(f"Encountered SE obstacle at step {step}: ({px:.1f}, {py:.1f})")
        break
