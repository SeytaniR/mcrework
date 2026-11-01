import json, os
from PIL import Image

base = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web"
with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\char1\char_manifest.json") as f:
    m = json.load(f)

for action_id in range(8):
    key = f"0-{action_id}"
    frames = m.get(key, [])
    print(f"\n================ ACTION {action_id} ('{key}', {len(frames)} frames) ================")
    for idx, fr in enumerate(frames):
        p = os.path.join(base, fr["file"])
        im = Image.open(p)
        bb = im.getbbox()
        print(f"  Frame {idx:2d}: bbox={bb}, w={bb[2]-bb[0]:2d}, h={bb[3]-bb[1]:2d}")
