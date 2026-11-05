import numpy as np
from PIL import Image

bg9 = np.array(Image.open('web/assets/maps/map_9/bg.jpg').convert('RGB'), dtype=np.float32)
shape9 = Image.open('tools/test_shape_png_9/2.png').convert('RGBA')
shape_arr = np.array(shape9, dtype=np.float32)

sh_h, sh_w, _ = shape_arr.shape
bg_h, bg_w, _ = bg9.shape

alpha = shape_arr[:, :, 3] == 255
y_indices, x_indices = np.where(alpha)
print(f"Opaque shape pixels: {len(y_indices)}")

# Pick an index
idx = len(y_indices) // 2
cy = y_indices[idx]
cx = x_indices[idx]
print(f"Selected point in shape9: cx={cx}, cy={cy}")

patch = shape_arr[cy-16:cy+16, cx-16:cx+16, :3]
patch_alpha = shape_arr[cy-16:cy+16, cx-16:cx+16, 3] == 255

best_diff = 999999
best_pos = None

for by in range(0, bg_h - 32, 4):
    for bx in range(0, bg_w - 32, 4):
        bg_patch = bg9[by:by+32, bx:bx+32]
        m = bg_patch[patch_alpha] - patch[patch_alpha]
        if len(m) > 0:
            diff = np.mean(np.abs(m))
            if diff < best_diff:
                best_diff = diff
                best_pos = (bx, by)

print(f"Best match in bg9: {best_pos} with mean diff = {best_diff:.2f}")
print(f"Offset from shape9: dx = {best_pos[0] - (cx - 16)}, dy = {best_pos[1] - (cy - 16)}")
