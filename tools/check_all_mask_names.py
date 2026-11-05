import os, hashlib, json, sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CATALOG = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CATALOG, "r", encoding="utf-8") as f:
    maps_data = json.load(f)["maps"]

existing_res = set(os.listdir(RES_DIR))

candidates = [
    "MAP_MASK.swf", "MAP_MASK_NEW.swf", "Mask.swf", "MASK.swf",
    "MAP_COVER.swf", "Cover.swf", "MAP_FORE.swf", "Fore.swf"
]

for m in maps_data:
    mid = m["id"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    found_for_map = []
    for c in candidates:
        h = hashlib.md5(f"{folder}/{c}".encode("utf-8")).hexdigest()
        if h in existing_res:
            found_for_map.append(c)
    if found_for_map:
        print(f"Map {mid:3d} ({m['name']}): {found_for_map}")
    else:
        print(f"Map {mid:3d} ({m['name']}): [SEM MASCARA FOREGROUND]")
