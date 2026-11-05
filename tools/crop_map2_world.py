from PIL import Image

shape2 = Image.open('tools/test_shape_png_2/2.png')

# World bounds: x: 0..2400, y: 0..1600
# In Shape 2: x_shape = world_x - 0 = world_x
# y_shape = world_y - (-1057.6) = world_y + 1057.6
# So for world_y = 0..1600, y_shape = 1058..2658
crop = shape2.crop((0, 1058, 2400, 2658))
crop.save('tools/test_map2_world_mask.png')
print("Saved tools/test_map2_world_mask.png (size:", crop.size, ")")
