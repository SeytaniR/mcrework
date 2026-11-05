import os, json
from PIL import Image

MAPS_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\maps"
for m_name in sorted(os.listdir(MAPS_DIR), key=lambda x: int(x.split('_')[1]) if x.startswith('map_') and x.split('_')[1].isdigit() else 999999)[:25]:
    mp = os.path.join(MAPS_DIR, m_name)
    if not os.path.isdir(mp): continue
    bg_p = os.path.join(mp, "bg.jpg")
    col_p = os.path.join(mp, "collision.bin")
    meta_p = os.path.join(mp, "meta.json")
    bg_size = Image.open(bg_p).size if os.path.exists(bg_p) else None
    col_len = os.path.getsize(col_p) if os.path.exists(col_p) else 0
    meta = json.load(open(meta_p, encoding="utf-8")) if os.path.exists(meta_p) else {}
    print(f"{m_name:<10}: bg={bg_size}, col_bytes={col_len}, meta=({meta.get('width')}x{meta.get('height')}), col_dim=({meta.get('col_width')}x{meta.get('col_height')})")
