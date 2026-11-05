import numpy as np
from PIL import Image

bg2 = np.array(Image.open('web/assets/maps/map_2/bg.jpg').convert('RGB'), dtype=np.float32)
mask = np.array(Image.open('tools/test_map2_world_mask.png').convert('RGBA'), dtype=np.float32)

alpha = mask[:, :, 3] > 100
print(f"Opaque pixels in test_map2_world_mask: {np.sum(alpha)}")

diff = np.abs(bg2[alpha] - mask[:, :, :3][alpha])
print(f"Mean pixel color difference: {np.mean(diff):.2f} / 255.0")

# If diff is large, let's find the small shifts (-10 to +10)
for dy in range(-10, 11):
    for dx in range(-10, 11):
        # Shift mask by dx, dy
        shifted_mask = Image.open('tools/test_shape_png_2/2.png').crop((dx, 1058 + dy, 2400 + dx, 2658 + dy))
        s_arr = np.array(shifted_mask, dtype=np.float32)
        s_alpha = s_arr[:, :, 3] > 200
        if np.sum(s_alpha) > 1000:
            d = np.mean(np.abs(bg2[s_alpha] - s_arr[:, :, :3][s_alpha]))
            if d < 20:
                print(f"MATCH FOUND at dx={dx}, dy={dy}: diff={d:.2f}")
