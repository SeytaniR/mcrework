import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
test_out = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\tools\test_wing_out'

for f in sorted(os.listdir(test_out)):
    if f.endswith('.png'):
        p = os.path.join(test_out, f)
        img = Image.open(p)
        bbox = img.getbbox()
        print(f"{f}: size={img.size}, bbox={bbox}")
