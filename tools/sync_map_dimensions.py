import sys, json, os
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
MAPS_DIR = os.path.join(BASE_DIR, "web", "assets", "maps")
CAT_P = os.path.join(MAPS_DIR, "catalog.json")

with open(CAT_P, "r", encoding="utf-8") as f:
    cat = json.load(f)

fixed = 0
for m in cat["maps"]:
    mid = m["id"]
    bg_p = os.path.join(MAPS_DIR, f"map_{mid}", "bg.jpg")
    meta_p = os.path.join(MAPS_DIR, f"map_{mid}", "meta.json")
    if os.path.exists(bg_p):
        im = Image.open(bg_p)
        bw, bh = im.size
        w = m.get("width")
        h = m.get("height")
        if bw != w or bh != h:
            print(f"Map {mid:3d} ({m['name']}): SQL was {w}x{h}, actual bg.jpg is {bw}x{bh}! Corrigindo...")
            m["width"] = bw
            m["height"] = bh
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    ind = json.load(mf)
                ind["width"] = bw
                ind["height"] = bh
                with open(meta_p, "w", encoding="utf-8") as mf:
                    json.dump(ind, mf, indent=2, ensure_ascii=False)
            fixed += 1

if fixed > 0:
    with open(CAT_P, "w", encoding="utf-8") as f:
        json.dump(cat, f, indent=2, ensure_ascii=False)
    print(f"\n{fixed} mapas corrigidos com as dimensões reais de suas texturas de fundo!")
else:
    print("\nTodos os mapas já correspondem perfeitamente às suas imagens de fundo.")
