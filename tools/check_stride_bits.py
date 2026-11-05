import os
from PIL import Image

with open('web/assets/maps/map_2/collision.bin', 'rb') as f:
    col = f.read()

for stride in [2400, 2450]:
    bits = []
    for x in range(200, 600, 50):
        idx = 1300 * stride + x
        b = (col[idx >> 3] >> (idx & 7)) & 1
        bits.append(b)
    print(f"Stride {stride}: bits={bits}")
