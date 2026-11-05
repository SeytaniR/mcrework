import os
from PIL import Image

bg2 = Image.open('web/assets/maps/map_2/bg.jpg').convert('RGBA')
shape2 = Image.open('tools/test_shape_png_2/2.png').convert('RGBA')

print(f"bg2 size: {bg2.size}, shape2 size: {shape2.size}")

# shape2 starts at x=0, y=-1057.6
# So y=0 in world coords corresponds to y=1058 in shape2!
# Let's crop from y=1058 to y=1058+1600 (2658):
crop_shape = shape2.crop((0, 1058, 2400, 1058 + 1600))
print(f"crop_shape size: {crop_shape.size}")

# Composite onto bg2
comp = Image.alpha_composite(bg2, crop_shape)
comp.convert('RGB').save('tools/test_map2_perfect_overlay.jpg', 'JPEG', quality=85)
print("Saved tools/test_map2_perfect_overlay.jpg!")
