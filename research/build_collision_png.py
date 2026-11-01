import zlib, os
from PIL import Image

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\map1_collision.bin", "rb") as f:
    decomp = zlib.decompress(f.read())

w = 2031
h = 1531

# Generate 1-bit PNG: 0 = obstacle (black), 255 = walkable (white)
# PIL mode '1' packs 8 pixels per byte, exactly matching the bit ordering (MSB or LSB?)
# Let's verify bit ordering:
# In Flash: `bit_idx = idx % 8`, `mask = 1 << bit_idx`
# So bit 0 is LSB!
# In PIL mode 'L' (8-bit grayscale), 1 byte per pixel:
pixels = bytearray(w * h)
for y in range(h):
    y_off = y * w
    for x in range(w):
        idx = y_off + x
        byte_idx = idx // 8
        bit_idx = idx % 8
        if (decomp[byte_idx] & (1 << bit_idx)):
            pixels[idx] = 255
        else:
            pixels[idx] = 0

img = Image.frombytes("L", (w, h), bytes(pixels))
out_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\collision.png"
img.save(out_path, optimize=True)
print(f"Generated collision.png: {out_path} ({os.path.getsize(out_path)} bytes)")
