import os, sys, json, hashlib, zlib, struct

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    cat_data = json.load(f)
    maps = cat_data["maps"]

print(f"Loaded {len(maps)} maps for calibration.")

# 1. Build map name lookup
map_lookup = {}
for m in maps:
    mid = m["id"]
    name = m["name"].strip()
    map_lookup[name] = mid
    map_lookup[name.lower()] = mid

map_lookup["cảnh kỹ trường"] = 2000
map_lookup["cạnh kỹ trường"] = 2000

# 2. Extract exact COL_WIDTH & COL_HEIGHT from MAP_HIT_NEW.swf
def get_exact_hit_dims(mid):
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    p = os.path.join(RES_DIR, h)
    if not os.path.exists(p):
        return None, None
    with open(p, "rb") as f:
        data = f.read()
    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    abc_body = None
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4
        if t_type == 72:
            abc_body = full[pos:pos+t_len]
        pos += t_len
        
    if not abc_body:
        return None, None
        
    doubles = []
    for i in range(len(abc_body) - 8):
        try:
            d = struct.unpack("<d", abc_body[i:i+8])[0]
            if 300.0 <= d <= 12000.0 and abs(d - round(d, 2)) < 0.001:
                doubles.append(d)
        except Exception:
            pass
            
    if len(doubles) >= 2:
        return round(doubles[0]), round(doubles[1])
    return None, None

# 3. Process every map
updated_dims = 0
calibrated_portals = 0

for m in maps:
    mid = m["id"]
    w = m["width"]
    h = m["height"]
    
    # Check exact collision dims
    cw, ch = get_exact_hit_dims(mid)
    if cw and ch:
        if m.get("col_width") != cw or m.get("col_height") != ch:
            print(f"Map {mid:2d} [{m['name']:<18}]: Updated col dims from ({m.get('col_width')}x{m.get('col_height')}) -> ({cw}x{ch})")
            m["col_width"] = cw
            m["col_height"] = ch
            updated_dims += 1
            
    # Audit portals
    portals = m.get("portals", [])
    
    # Map 1 special addition: Portal to Map 3 (Vân Đài)
    if mid == 1:
        has_van_dai = any(p.get("target_map_id") == 3 for p in portals)
        if not has_van_dai:
            portals.append({
                "id": 731,
                "target_name": "Vân Đài",
                "target_map_id": 3,
                "x": 220,
                "y": 420,
                "dest_x": 100,
                "dest_y": 1050
            })
            print("Added physical portal on Map 1 to Vân Đài (#3) at (220, 420).")
            
    for p in portals:
        calibrated_portals += 1
        t_name = p.get("target_name", "").strip()
        t_mid = p.get("target_map_id")
        
        if t_mid is None and t_name:
            t_mid = map_lookup.get(t_name) or map_lookup.get(t_name.lower())
            if t_mid:
                p["target_map_id"] = t_mid
                print(f"  Fixed target_map_id for portal {p.get('id')} ({t_name}) -> {t_mid}")
                
        # Clamp portal coordinates to visible walkable margins
        orig_x, orig_y = p.get("x", 0), p.get("y", 0)
        px = max(45, min(w - 45, orig_x))
        py = max(55, min(h - 55, orig_y))
        p["x"] = px
        p["y"] = py
        
        # Ensure dest_x, dest_y are valid
        if (p.get("dest_x") is None or p.get("dest_y") is None) and t_mid:
            dest_map = next((dm for dm in maps if dm["id"] == t_mid), None)
            if dest_map:
                p["dest_x"] = dest_map.get("safe_x") or round(dest_map.get("width", 2000) / 2)
                p["dest_y"] = dest_map.get("safe_y") or round(dest_map.get("height", 1500) / 2)
                
    m["portals"] = portals

print(f"\nCalibrated collision dims for {updated_dims} maps.")
print(f"Audited {calibrated_portals} portals across maps.")

# Save updated catalog.json
with open(MAPS_CAT, "w", encoding="utf-8") as f:
    json.dump(cat_data, f, indent=2)

print("Saved calibrated catalog.json!")
