from PIL import Image

bg2 = Image.open('web/assets/maps/map_2/bg.jpg')
# Let's inspect the bottom left road: (200, 1300) to (600, 1300)
# What are the RGB colors?
for x in range(200, 600, 50):
    print(f"x={x}, y=1300: RGB={bg2.getpixel((x, 1300))}")
