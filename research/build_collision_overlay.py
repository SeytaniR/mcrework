import os
from PIL import Image

col_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\collision.png"
out_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\collision_overlay.png"

col = Image.open(col_path).convert("L")
w, h = col.size

raw_col = col.tobytes()
raw_out = bytearray(w * h * 4)

for i in range(w * h):
    if raw_col[i] == 0:  # obstacle
        idx = i * 4
        raw_out[idx] = 235     # R
        raw_out[idx+1] = 40    # G
        raw_out[idx+2] = 40    # B
        raw_out[idx+3] = 95    # Alpha (~37%)

img = Image.frombytes("RGBA", (w, h), bytes(raw_out))
img.save(out_path, optimize=True)
print(f"Saved {out_path} ({os.path.getsize(out_path)} bytes)")
