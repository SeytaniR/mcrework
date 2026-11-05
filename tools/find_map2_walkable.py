import os, sys, json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

m2 = next(m for m in cat['maps'] if m['id'] == 2)
col_p = os.path.join('web', m2['collision_bin'])
with open(col_p, 'rb') as f:
    col_bytes = f.read()

cw, ch = m2['col_width'], m2['col_height']

# Find min_x, max_x, min_y, max_y of walkable pixels (bit == 1)
min_x, max_x = 999999, -1
min_y, max_y = 999999, -1

# Let's count walkable pixels per 100x100 block
grid = [[0 for _ in range(cw // 100 + 1)] for _ in range(ch // 100 + 1)]

for y in range(ch):
    y_off = y * cw
    for x in range(cw):
        idx = y_off + x
        if (col_bytes[idx >> 3] >> (idx & 7)) & 1:
            if x < min_x: min_x = x
            if x > max_x: max_x = x
            if y < min_y: min_y = y
            if y > max_y: max_y = y
            grid[y // 100][x // 100] += 1

print(f"Map 2 Walkable Bounding Box: x=[{min_x}..{max_x}], y=[{min_y}..{max_y}]")
print(f"Collision dimensions: {cw} x {ch}")
print("\nWalkable density grid (each cell 100x100, max 10000 pixels):")
for gy in range(len(grid)):
    row_str = "".join([f"{grid[gy][gx]//1000:1x}" if grid[gy][gx] > 0 else "." for gx in range(len(grid[gy]))])
    print(f"y={gy*100:4d}: {row_str}")
