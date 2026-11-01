import json, os
from PIL import Image

base = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web"
with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\char1\char_manifest.json") as f:
    m = json.load(f)

# Create an overview image: 8 rows (actions 0..7), 5 columns (sample frames)
cell_w, cell_h = 110, 130
cols = 5
rows = 8
sheet = Image.new("RGBA", (cols * cell_w, rows * cell_h), (20, 24, 33, 255))

for action_id in range(8):
    key = f"0-{action_id}"
    frames = m.get(key, [])
    if not frames: continue
    
    # Pick 5 evenly spaced frames
    indices = [int(i * (len(frames) - 1) / (cols - 1)) for i in range(cols)]
    for c_idx, fr_idx in enumerate(indices):
        fr = frames[fr_idx]
        p = os.path.join(base, fr["file"])
        im = Image.open(p).convert("RGBA")
        crop = im.crop((50, 0, 160, 130))
        sheet.paste(crop, (c_idx * cell_w, action_id * cell_h), crop)

out_sheet = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\actions_overview.png"
sheet.save(out_sheet)
print(f"Saved {out_sheet}")
