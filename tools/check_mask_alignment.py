import numpy as np
from PIL import Image

bg2 = np.array(Image.open('web/assets/maps/map_2/bg.jpg').convert('RGB'), dtype=np.float32)
shape2 = Image.open('tools/test_shape_png_2/2.png').convert('RGBA')
crop_shape = shape2.crop((0, 1058, 2400, 1058 + 1600))
crop_arr = np.array(crop_shape, dtype=np.float32)

alpha = crop_arr[:, :, 3] > 200
num_opaque = np.sum(alpha)
print(f"Total opaque pixels in crop_shape: {num_opaque}")

if num_opaque > 0:
    diff = np.abs(bg2[alpha] - crop_arr[:, :, :3][alpha])
    mean_diff = np.mean(diff)
    print(f"Mean pixel color difference between mask and background: {mean_diff:.2f} / 255.0")
