import os, sys
from PIL import Image

# Let's inspect Map 1: crop the bridge and a house in debug_col_map_1.jpg
im1 = Image.open('tools/debug_col_map_1.jpg')
# Bridge in map 1 is around x=900..1200, y=700..900
crop1 = im1.crop((900, 700, 1300, 1000))
crop1.save('tools/test_crop_map1_bridge.jpg')
print("Saved tools/test_crop_map1_bridge.jpg")

# Now let's inspect Map 2: crop a recognizable feature in debug_col_map_2.jpg
im2 = Image.open('tools/debug_col_map_2.jpg')
# In Map 2, the road at y=1200..1400: x=200..800
crop2 = im2.crop((100, 1100, 800, 1500))
crop2.save('tools/test_crop_map2_road.jpg')
print("Saved tools/test_crop_map2_road.jpg")
