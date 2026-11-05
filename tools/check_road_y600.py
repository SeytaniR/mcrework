from PIL import Image

bg2 = Image.open('web/assets/maps/map_2/bg.jpg')
# Check colors at y=600 around x=1900..2300
for x in range(1850, 2350, 50):
    print(f"x={x}, y=600: RGB={bg2.getpixel((x, 600))}")
