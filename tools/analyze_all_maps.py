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
print(f"Total files in res directory: {len(existing_res)}")

# 1. Parse data_tbl_map.sql
with open(MAP_SQL, "r", encoding="utf-8", errors="ignore") as f:
    sql_text = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql_text, re.DOTALL)
print(f"Total map rows in SQL: {len(rows)}")

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
        except Exception as e:
            pass

print(f"Parsed {len(maps)} maps successfully.")

# 2. Parse Portals from data_tbl_sceneitem_instance.sql
# Columns: id, bright_code, color_code, dead_line, layer, maker, name, owner_id, owner_type, pos_dir, pos_map_id, from, pos_x, pos_y, tid
with open(PORTAL_SQL, "r", encoding="utf-8", errors="ignore") as f:
    portal_text = f.read()

portal_rows = re.findall(r"\(([^;]+?)\)[,;]", portal_text, re.DOTALL)
print(f"Total sceneitem rows in SQL: {len(portal_rows)}")

portals_by_map = {}
all_portals = []

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
            
            # tid == 38 is "Điểm Chuyển Tiếp" (Teleport Point / Portal)
            # Other tids may also be portals or interaction points
            if tid == 38 or "chuyển" in target_name.lower() or any(m["name"] == target_name for m in maps.values()):
                portal_obj = {
                    "id": item_id,
                    "from_map_id": pos_map_id,
                    "target_name": target_name,
                    "x": pos_x,
                    "y": pos_y,
                    "tid": tid
                }
                # Try to resolve target_map_id
                target_map = None
                for m_id, m_data in maps.items():
                    if m_data["name"] == target_name:
                        target_map = m_id
                        break
                portal_obj["target_map_id"] = target_map
                
                all_portals.append(portal_obj)
                if pos_map_id not in portals_by_map:
                    portals_by_map[pos_map_id] = []
                portals_by_map[pos_map_id].append(portal_obj)
        except Exception:
            pass

print(f"Total teleport portals found: {len(all_portals)} across {len(portals_by_map)} maps.")

# 3. Parse WorldMap.as coordinates
world_map_icons = {}
if os.path.exists(WORLD_MAP_AS):
    with open(WORLD_MAP_AS, "r", encoding="utf-8", errors="ignore") as f:
        wm_as = f.read()
    
    # Check worldMap1 vs worldMap2
    wm1_pos = wm_as.find('"id":"worldMap1"')
    wm2_pos = wm_as.find('"id":"worldMap2"')
    print(f"WorldMap1 pos: {wm1_pos}, WorldMap2 pos: {wm2_pos}")
    
    # Pattern to find all icon descriptors
    pattern = re.compile(r'\"id\"\s*:\s*\"i(\d+)\".*?\"x\"\s*:\s*(\d+).*?\"y\"\s*:\s*(\d+)', re.DOTALL)
    for match in pattern.finditer(wm_as):
        mid = int(match.group(1))
        x = int(match.group(2))
        y = int(match.group(3))
        start_idx = match.start()
        continent = 1 if (wm2_pos == -1 or start_idx < wm2_pos) else 2
        world_map_icons[mid] = {
            "map_id": mid,
            "continent": continent,
            "world_x": x,
            "world_y": y
        }

print(f"Total World Map icons found: {len(world_map_icons)}")
for mid, icon in sorted(world_map_icons.items())[:15]:
    m_name = maps.get(mid, {}).get("name", "Unknown")
    print(f"  Icon i{mid}: {m_name} -> Continent {icon['continent']} (X:{icon['world_x']}, Y:{icon['world_y']})")

# 4. Check all scene tiles for each map
results = {}
for mid, m in sorted(maps.items()):
    scene_folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    
    tile_count = 0
    max_tx, max_ty = 0, 0
    tile_hashes = {}
    for tx in range(30):
        found_in_row = False
        for ty in range(30):
            tp = f"{scene_folder}/MAP_{tx}_{ty}.jpg"
            th = hashlib.md5(tp.encode("utf-8")).hexdigest()
            if th in existing_res:
                tile_count += 1
                found_in_row = True
                tile_hashes[f"{tx}_{ty}"] = th
                if tx > max_tx: max_tx = tx
                if ty > max_ty: max_ty = ty
            else:
                if ty > 0 and not found_in_row:
                    break
        if not found_in_row and tx > 0:
            break
            
    mini_path = f"{scene_folder}/MiniMap.jpg"
    mini_hash = hashlib.md5(mini_path.encode("utf-8")).hexdigest()
    has_mini = mini_hash in existing_res
    
    hit_path = f"{scene_folder}/Hit.swf"
    hit_hash = hashlib.md5(hit_path.encode("utf-8")).hexdigest()
    has_hit = hit_hash in existing_res
    
    mask_path = f"{scene_folder}/Mask.swf"
    mask_hash = hashlib.md5(mask_path.encode("utf-8")).hexdigest()
    has_mask = mask_hash in existing_res
    
    results[mid] = {
        "id": mid,
        "name": m["name"],
        "info": m["info"],
        "level": m["level"],
        "width": m["width"],
        "height": m["height"],
        "safe_x": m["safe_x"],
        "safe_y": m["safe_y"],
        "tile_count": tile_count,
        "max_tx": max_tx,
        "max_ty": max_ty,
        "has_mini": has_mini,
        "mini_hash": mini_hash if has_mini else None,
        "has_hit": has_hit,
        "hit_hash": hit_hash if has_hit else None,
        "has_mask": has_mask,
        "mask_hash": mask_hash if has_mask else None,
        "portals": portals_by_map.get(mid, []),
        "world_icon": world_map_icons.get(mid, None)
    }

playable_maps = [r for r in results.values() if r["tile_count"] > 0 or r["has_mini"]]
print(f"\n==========================================")
print(f"RESUMO DOS MAPAS DO JOGO:")
print(f"Total de mapas no banco SQL: {len(maps)}")
print(f"Mapas com recursos visuais (tiles/minimap): {len(playable_maps)}")
print(f"Mapas com ícones no Mapa Mundi (WorldMap): {len(world_map_icons)}")
print(f"Total de portais / teleporte identificados: {len(all_portals)}")
print(f"==========================================")

with open(os.path.join(BASE_DIR, "tools", "maps_analysis.json"), "w", encoding="utf-8") as f:
    json.dump({
        "total_maps": len(maps),
        "playable_maps_count": len(playable_maps),
        "world_map_icons_count": len(world_map_icons),
        "total_portals_count": len(all_portals),
        "maps": results
    }, f, indent=2, ensure_ascii=False)

print("Relatório salvo em tools/maps_analysis.json!")
