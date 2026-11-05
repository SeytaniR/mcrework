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
bw, bh = m2['width'], m2['height']

# Count total 1s vs 0s in col_bytes
total_bits = len(col_bytes) * 8
ones = 0
for b in col_bytes:
    ones += bin(b).count('1')
print(f"Map 2 total bits: {total_bits}, ones (walkable): {ones} ({ones/total_bits*100:.1f}%)")

# Let's inspect rows around safe pos (2000, 900)
print("\nSlice around (2000, 900) [x: 1980..2020, y: 880..920]:")
for y in range(890, 910, 2):
    row_chars = []
    for x in range(1980, 2020, 2):
        idx = y * cw + x
        bit = (col_bytes[idx >> 3] >> (idx & 7)) & 1
        row_chars.append('.' if bit else '#')
    print(f"y={y}: " + "".join(row_chars))

# Now let's test if cw is DIFFERENT!
# What if the stride is NOT 2450?
# What if the stride is 2400 (bw)? Or 3000?
print("\nTesting different strides around (2000, 900):")
for test_stride in [2400, 2450, 2451, 2452, 2500, 3000]:
    row_chars = []
    for x in range(1980, 2020, 2):
        idx = 900 * test_stride + x
        if idx >> 3 < len(col_bytes):
            bit = (col_bytes[idx >> 3] >> (idx & 7)) & 1
            row_chars.append('.' if bit else '#')
        else:
            row_chars.append('X')
    print(f"stride={test_stride}: " + "".join(row_chars))
