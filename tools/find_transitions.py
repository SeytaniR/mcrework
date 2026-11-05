from PIL import Image

bg2 = Image.open('web/assets/maps/map_2/bg.jpg')
with open('web/assets/maps/map_2/collision.bin', 'rb') as f:
    col = f.read()

# Let's inspect along y = 600 across the entire map x = 0..2400
# Where does col bit transition from 0 to 1 and 1 to 0?
transitions_2450 = []
last = None
for x in range(2400):
    idx = 600 * 2450 + x
    b = (col[idx >> 3] >> (idx & 7)) & 1
    if b != last:
        transitions_2450.append((x, b))
        last = b

transitions_2400 = []
last = None
for x in range(2400):
    idx = 600 * 2400 + x
    b = (col[idx >> 3] >> (idx & 7)) & 1
    if b != last:
        transitions_2400.append((x, b))
        last = b

print("Transitions at y=600 with stride=2450:", transitions_2450)
print("Transitions at y=600 with stride=2400:", transitions_2400)
