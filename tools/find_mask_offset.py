import numpy as np
from PIL import Image

bg2 = np.array(Image.open('web/assets/maps/map_2/bg.jpg').convert('RGB'), dtype=np.float32)
shape2 = Image.open('tools/test_shape_png_2/2.png').convert('RGBA')
shape_arr = np.array(shape2, dtype=np.float32)

sh_h, sh_w, _ = shape_arr.shape
bg_h, bg_w, _ = bg2.shape

print(f"bg: {bg_w}x{bg_h}, shape: {sh_w}x{sh_h}")

# In Map 2, let's find the tree cluster in shape2
alpha = shape_arr[:, :, 3] > 100

# Let's test a slice of 100x100 around an opaque patch in shape2
y_indices, x_indices = np.where(alpha)
print(f"Opaque shape pixels span: x=[{x_indices.min()}..{x_indices.max()}], y=[{y_indices.min()}..{y_indices.max()}]")

# Let's take a 64x64 patch from the center of that opaque region
center_y = int(np.median(y_indices))
center_x = int(np.median(x_indices))
print(f"Center of opaque region in shape2: ({center_x}, {center_y})")

patch = shape_arr[center_y-32:center_y+32, center_x-32:center_x+32, :3]
patch_alpha = shape_arr[center_y-32:center_y+32, center_x-32:center_x+32, 3] > 200

# Now search where this 64x64 patch appears in bg2!
best_diff = 999999
best_pos = None

# Scan bg2
for by in range(0, bg_h - 64, 4):
    for bx in range(0, bg_w - 64, 4):
        bg_patch = bg2[by:by+64, bx:bx+64]
        diff = np.mean(np.abs(bg_patch[patch_alpha] - patch[patch_alpha]))
        if diff < best_diff:
            best_diff = diff
            best_pos = (bx, by)

print(f"Best match in bg2: {best_pos} with mean diff = {best_diff:.2f}")
print(f"Offset from shape2: dx = {best_pos[0] - (center_x - 32)}, dy = {best_pos[1] - (center_y - 32)}")
