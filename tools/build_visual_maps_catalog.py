import os, sys, re, json, hashlib

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
MAP_SQL = os.path.join(BASE_DIR, "mcgame", "supabase", "seeds", "data_tbl_map.sql")
PORTAL_SQL = os.path.join(BASE_DIR, "mcgame", "supabase", "seeds", "data_tbl_sceneitem_instance.sql")
WORLD_MAP_AS = os.path.join(BASE_DIR, "mcgame", "docs", "client", "view", "view", "compMain", "WorldMap.as")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")

existing_res = set(os.listdir(RES_DIR))

# Parse maps
with open(MAP_SQL, "r", encoding="utf-8", errors="ignore") as f:
    sql_text = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql_text, re.DOTALL)
maps = {}
for r in rows:
    fields = []
    in_quote = False
    cur = []
    for c in r:
        if c == "'":
            in_quote = not in_quote
            cur.append(c)
        elif c == ',' and not in_quote:
            fields.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    fields.append("".join(cur).strip())

    if len(fields) >= 34:
        try:
            map_id = int(fields[0])
            height = int(fields[13])
            info = fields[14].strip("'")
            level = int(fields[17])
            m_map = int(fields[20])
            name = fields[21].strip("'")
            res_code = fields[25].strip("'")
            s_map = int(fields[27])
            safe_x = int(fields[29])
            safe_y = int(fields[30])
            width = int(fields[33])
            cl = fields[6].strip("'")
            
            maps[map_id] = {
                "id": map_id,
                "name": name,
                "info": info,
                "level": level,
                "width": width,
                "height": height,
                "res_code": res_code,
                "safe_x": safe_x,
                "safe_y": safe_y,
                "m_map": m_map,
                "s_map": s_map,
                "cl": cl
            }
        except Exception:
            pass

# Parse portals
with open(PORTAL_SQL, "r", encoding="utf-8", errors="ignore") as f:
    portal_text = f.read()

portal_rows = re.findall(r"\(([^;]+?)\)[,;]", portal_text, re.DOTALL)
portals_by_map = {}
for r in portal_rows:
    fields = []
    in_quote = False
    cur = []
    for c in r:
        if c == "'":
            in_quote = not in_quote
            cur.append(c)
        elif c == ',' and not in_quote:
            fields.append("".join(cur).strip())
            cur = []
        else:
            cur.append(c)
    fields.append("".join(cur).strip())

    if len(fields) >= 15:
        try:
            item_id = int(fields[0])
            target_name = fields[6].strip("'")
            pos_map_id = int(fields[10])
            pos_x = int(fields[12])
            pos_y = int(fields[13])
            tid = int(fields[14])
            
            if tid == 38 or any(m["name"] == target_name for m in maps.values()):
                target_map = None
                for m_id, m_data in maps.items():
                    if m_data["name"] == target_name:
                        target_map = m_id
                        break
                p_entry = {
                    "id": item_id,
                    "target_name": target_name,
                    "target_map_id": target_map,
                    "x": pos_x,
                    "y": pos_y
                }
                if pos_map_id not in portals_by_map:
                    portals_by_map[pos_map_id] = []
                portals_by_map[pos_map_id].append(p_entry)
        except Exception:
            pass

# Parse WorldMap.as
world_map_icons = {}
if os.path.exists(WORLD_MAP_AS):
    with open(WORLD_MAP_AS, "r", encoding="utf-8", errors="ignore") as f:
        wm_as = f.read()
    wm2_pos = wm_as.find('"id":"worldMap2"')
    pattern = re.compile(r'\"id\"\s*:\s*\"i(\d+)\".*?\"x\"\s*:\s*(\d+).*?\"y\"\s*:\s*(\d+)', re.DOTALL)
    for match in pattern.finditer(wm_as):
        mid = int(match.group(1))
        x = int(match.group(2))
        y = int(match.group(3))
        start_idx = match.start()
        continent = 1 if (wm2_pos == -1 or start_idx < wm2_pos) else 2
        world_map_icons[mid] = {
            "continent": continent,
            "x": x,
            "y": y
        }

catalog = []
for mid, m in sorted(maps.items()):
    scene_folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    map_jpg_path = f"{scene_folder}/MAP_0_0.jpg"
    map_jpg_hash = hashlib.md5(map_jpg_path.encode("utf-8")).hexdigest()
    has_image = map_jpg_hash in existing_res
    
    hit_path = f"{scene_folder}/Hit.swf"
    hit_hash = hashlib.md5(hit_path.encode("utf-8")).hexdigest()
    has_hit = hit_hash in existing_res
    
    mask_path = f"{scene_folder}/Mask.swf"
    mask_hash = hashlib.md5(mask_path.encode("utf-8")).hexdigest()
    has_mask = mask_hash in existing_res
    
    img_size = os.path.getsize(os.path.join(RES_DIR, map_jpg_hash)) if has_image else 0
    hit_size = os.path.getsize(os.path.join(RES_DIR, hit_hash)) if has_hit else 0
    
    if has_image:
        catalog.append({
            "id": mid,
            "name": m["name"],
            "info": m["info"],
            "level": m["level"],
            "width": m["width"],
            "height": m["height"],
            "safe_x": m["safe_x"],
            "safe_y": m["safe_y"],
            "image_hash": map_jpg_hash,
            "image_size_kb": round(img_size / 1024, 1),
            "has_hit": has_hit,
            "hit_hash": hit_hash if has_hit else None,
            "has_mask": has_mask,
            "mask_hash": mask_hash if has_mask else None,
            "world_icon": world_map_icons.get(mid),
            "portals": portals_by_map.get(mid, [])
        })

print(f"Total Maps with Artwork Image: {len(catalog)}")
print(f"Maps on Continent 1: {sum(1 for c in catalog if c['world_icon'] and c['world_icon']['continent'] == 1)}")
print(f"Maps on Continent 2: {sum(1 for c in catalog if c['world_icon'] and c['world_icon']['continent'] == 2)}")
print(f"Maps with Hit.swf collision: {sum(1 for c in catalog if c['has_hit'])}")
print(f"Total Portals on Visual Maps: {sum(len(c['portals']) for c in catalog)}")

with open(os.path.join(BASE_DIR, "tools", "visual_maps_catalog.json"), "w", encoding="utf-8") as f:
    json.dump({
        "total_visual_maps": len(catalog),
        "maps": catalog
    }, f, indent=2, ensure_ascii=False)

print("Catalog saved in tools/visual_maps_catalog.json")
