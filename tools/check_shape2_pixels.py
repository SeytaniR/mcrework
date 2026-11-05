from PIL import Image
import numpy as np

shape2 = Image.open('tools/test_shape_png_2/2.png')
print(f"Shape 2 size: {shape2.size}")

# Let's inspect where opaque pixels are in shape2
alpha = np.array(shape2.split()[-1]) > 50
print("Any opaque in shape2?", np.any(alpha))
y_idx, x_idx = np.where(alpha)
print(f"Opaque region in shape2: x=[{x_idx.min()}..{x_idx.max()}], y=[{y_idx.min()}..{y_idx.max()}]")

# What are the dimensions of Map 2 bg?
bg2 = Image.open('web/assets/maps/map_2/bg.jpg')
print(f"bg2 size: {bg2.size}")
