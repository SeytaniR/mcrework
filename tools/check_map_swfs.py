import os, hashlib, json

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CATALOG = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CATALOG, "r", encoding="utf-8") as f:
    maps_data = json.load(f)["maps"]

existing_res = set(os.listdir(RES_DIR))
print(f"Total maps in catalog: {len(maps_data)}")

maps_with_mask_swf = []
maps_with_hit_new = []
maps_with_hit_old = []

for m in maps_data:
    mid = m["id"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    
    mask_path = f"{folder}/Mask.swf"
    mask_h = hashlib.md5(mask_path.encode("utf-8")).hexdigest()
    if mask_h in existing_res:
        maps_with_mask_swf.append(mid)
        
    hit_new = f"{folder}/MAP_HIT_NEW.swf"
    hn_h = hashlib.md5(hit_new.encode("utf-8")).hexdigest()
    if hn_h in existing_res:
        maps_with_hit_new.append(mid)
        
    hit_old = f"{folder}/Hit.swf"
    ho_h = hashlib.md5(hit_old.encode("utf-8")).hexdigest()
    if ho_h in existing_res:
        maps_with_hit_old.append(mid)

print(f"Maps with Mask.swf: {len(maps_with_mask_swf)} / {len(maps_data)}")
print(f"Maps with MAP_HIT_NEW.swf: {len(maps_with_hit_new)} / {len(maps_data)}")
print(f"Maps with Hit.swf: {len(maps_with_hit_old)} / {len(maps_data)}")
print("Sample maps with Mask.swf:", maps_with_mask_swf[:20])
