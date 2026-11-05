import os, sys, json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

for m in cat['maps']:
    mid = m['id']
    bg_p = os.path.join('web', m.get('bg_image', ''))
    if os.path.exists(bg_p):
        with Image.open(bg_p) as im:
            bw, bh = im.size
            if bw != m['width'] or bh != m['height']:
                print(f"MISMATCH Map {mid}: cat={m['width']}x{m['height']} vs actual_bg={bw}x{bh}")
print("Done checking all bg images against catalog width/height.")
