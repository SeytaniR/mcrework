import os, sys, json, hashlib, subprocess, tempfile
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
FFDEC = os.path.join(BASE_DIR, "tools", "ffdec", "ffdec-cli.exe")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    maps = json.load(f)["maps"]

dump_dir = "tools/test_mask_dims_check"
os.makedirs(dump_dir, exist_ok=True)

for m in maps:
    mid = m["id"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    mask_h = hashlib.md5(f"{folder}/MAP_MASK.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, mask_h)
    if not os.path.exists(swf_p):
        continue
    
    out_map_dump = os.path.join(dump_dir, f"map_{mid}")
    if not os.path.exists(out_map_dump):
        os.makedirs(out_map_dump, exist_ok=True)
        subprocess.run([FFDEC, "-export", "image", out_map_dump, swf_p], capture_output=True)
    
    pngs = [f for f in os.listdir(out_map_dump) if f.endswith(".png")]
    png_sizes = []
    for p in pngs:
        with Image.open(os.path.join(out_map_dump, p)) as im:
            png_sizes.append(im.size)
    
    bw, bh = m["width"], m["height"]
    cw, ch = m.get("col_width"), m.get("col_height")
    print(f"Map {mid:2d} ({m['name']:<16}): bg={bw}x{bh}, col={cw}x{ch}, mask_pngs={len(pngs)}, sizes={png_sizes[:3]}")
