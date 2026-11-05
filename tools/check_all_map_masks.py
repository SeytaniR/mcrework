import os, hashlib, json

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CATALOG = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CATALOG, "r", encoding="utf-8") as f:
    maps_data = json.load(f)["maps"]

existing_res = set(os.listdir(RES_DIR))

maps_with_mask = []
maps_without_mask = []

for m in maps_data:
    mid = m["id"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    mask_path = f"{folder}/MAP_MASK.swf"
    mask_h = hashlib.md5(mask_path.encode("utf-8")).hexdigest()
    if mask_h in existing_res:
        maps_with_mask.append((mid, m["name"], mask_h))
    else:
        maps_without_mask.append((mid, m["name"]))

print(f"Total maps: {len(maps_data)}")
print(f"Maps WITH MAP_MASK.swf: {len(maps_with_mask)}")
print(f"Maps WITHOUT MAP_MASK.swf: {len(maps_without_mask)}")
print("\nSample maps with MAP_MASK.swf:")
for mid, name, h in maps_with_mask[:25]:
    print(f"  Map {mid:2d} ({name}) -> hash: {h}")

if maps_without_mask:
    print("\nMaps without MAP_MASK.swf:")
    for mid, name in maps_without_mask[:10]:
        print(f"  Map {mid:2d} ({name})")
