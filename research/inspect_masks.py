import json
from PIL import Image

with open("C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/map1/masks.json") as f:
    masks = json.load(f)

for m in masks:
    im = Image.open("C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/" + m["file"])
    w, h = im.size
    print(f"{m['file']} ({m['bitmap_id']}): x=[{m['x']:.1f} .. {m['x']+w:.1f}], y=[{m['y']:.1f} .. {m['y']+h:.1f}]")
