import numpy as np
from PIL import Image

bg9 = np.array(Image.open('web/assets/maps/map_9/bg.jpg').convert('RGB'), dtype=np.float32)
shape9 = Image.open('tools/test_shape_png_9/2.png').convert('RGBA')
shape_arr = np.array(shape9, dtype=np.float32)

sh_h, sh_w, _ = shape_arr.shape
bg_h, bg_w, _ = bg9.shape

print(f"Map 9 bg: {bg_w}x{bg_h}, shape: {sh_w}x{sh_h}")

alpha = shape_arr[:, :, 3] > 100
y_indices, x_indices = np.where(alpha)
print(f"Opaque shape pixels span: x=[{x_indices.min()}..{x_indices.max()}], y=[{y_indices.min()}..{y_indices.max()}]")

center_y = int(np.median(y_indices))
center_x = int(np.median(x_indices))
print(f"Center of opaque region in shape9: ({center_x}, {center_y})")

patch = shape_arr[center_y-32:center_y+32, center_x-32:center_x+32, :3]
patch_alpha = shape_arr[center_y-32:center_y+32, center_x-32:center_x+32, 3] > 200

best_diff = 999999
best_pos = None

for by in range(0, bg_h - 64, 8):
    for bx in range(0, bg_w - 64, 8):
        bg_patch = bg9[by:by+64, bx:bx+64]
        diff = np.mean(np.abs(bg_patch[patch_alpha] - patch[patch_alpha]))
        if diff < best_diff:
            best_diff = diff
            best_pos = (bx, by)

print(f"Best match in bg9: {best_pos} with mean diff = {best_diff:.2f}")
print(f"Offset from shape9: dx = {best_pos[0] - (center_x - 32)}, dy = {best_pos[1] - (center_y - 32)}")
