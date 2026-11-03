import os, sys, zlib, hashlib, struct, json, re
from PIL import Image

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

OUT_MAPS_DIR = os.path.join(BASE_DIR, "web", "assets", "maps")
OUT_WORLDMAP_DIR = os.path.join(BASE_DIR, "web", "assets", "worldmap")
os.makedirs(OUT_MAPS_DIR, exist_ok=True)
os.makedirs(OUT_WORLDMAP_DIR, exist_ok=True)

existing_res = set(os.listdir(RES_DIR))
print(f"Total files in res directory: {len(existing_res)}")

# -------------------------------------------------------------
# 1. Parse data_tbl_map.sql
# -------------------------------------------------------------
with open(MAP_SQL, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

val_pos = sql.find("VALUES")
values_str = sql[val_pos + 6:]
rows = []
cur_row = []
in_paren = False
in_quote = False
i = 0
while i < len(values_str):
    c = values_str[i]
    if not in_quote:
        if c == "'":
            in_quote = True
            cur_row.append(c)
        elif c == '(':
            in_paren = True
            cur_row = []
        elif c == ')':
            in_paren = False
            rows.append("".join(cur_row))
            cur_row = []
        elif in_paren:
            cur_row.append(c)
    else:
        if c == "'":
            if i + 1 < len(values_str) and values_str[i+1] == "'":
                cur_row.append("''")
                i += 1
            else:
                in_quote = False
                cur_row.append(c)
        else:
            cur_row.append(c)
    i += 1

maps_db = {}
name_to_map_id = {}
for r in rows:
    fields = []
    cur_fld = []
    in_q = False
    j = 0
    while j < len(r):
        ch = r[j]
        if not in_q:
            if ch == "'": in_q = True
            elif ch == ',':
                fields.append("".join(cur_fld).strip())
                cur_fld = []
            else: cur_fld.append(ch)
        else:
            if ch == "'":
                if j + 1 < len(r) and r[j+1] == "'":
                    cur_fld.append("'")
                    j += 1
                else: in_q = False
            else: cur_fld.append(ch)
        j += 1
    fields.append("".join(cur_fld).strip())

    if len(fields) >= 34:
        try:
            mid = int(fields[0])
            name = fields[21]
            height = int(fields[13])
            width = int(fields[33])
            level = int(fields[17])
            info = fields[14]
            safe_x = int(fields[29])
            safe_y = int(fields[30])
            cl = fields[6] # creature list e.g. "|107|154|1|3|"
            creatures = [int(x) for x in cl.split("|") if x.isdigit()]
            
            maps_db[mid] = {
                "id": mid,
                "name": name,
                "info": info,
                "level": level,
                "width": width,
                "height": height,
                "safe_x": safe_x,
                "safe_y": safe_y,
                "creatures": creatures
            }
            name_to_map_id[name] = mid
        except Exception:
            pass

print(f"Loaded {len(maps_db)} maps from SQL.")

# -------------------------------------------------------------
# 2. Parse Portals from data_tbl_sceneitem_instance.sql
# -------------------------------------------------------------
with open(PORTAL_SQL, "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

val_pos = sql.find("VALUES")
values_str = sql[val_pos + 6:]
rows = []
cur_row = []
in_paren = False
in_quote = False
i = 0
while i < len(values_str):
    c = values_str[i]
    if not in_quote:
        if c == "'":
            in_quote = True
            cur_row.append(c)
        elif c == '(':
            in_paren = True
            cur_row = []
        elif c == ')':
            in_paren = False
            rows.append("".join(cur_row))
            cur_row = []
        elif in_paren:
            cur_row.append(c)
    else:
        if c == "'":
            if i + 1 < len(values_str) and values_str[i+1] == "'":
                cur_row.append("''")
                i += 1
            else:
                in_quote = False
                cur_row.append(c)
        else:
            cur_row.append(c)
    i += 1

portals_by_map = {}
for r in rows:
    fields = []
    cur_fld = []
    in_q = False
    j = 0
    while j < len(r):
        ch = r[j]
        if not in_q:
            if ch == "'": in_q = True
            elif ch == ',':
                fields.append("".join(cur_fld).strip())
                cur_fld = []
            else: cur_fld.append(ch)
        else:
            if ch == "'":
                if j + 1 < len(r) and r[j+1] == "'":
                    cur_fld.append("'")
                    j += 1
                else: in_q = False
            else: cur_fld.append(ch)
        j += 1
    fields.append("".join(cur_fld).strip())

    if len(fields) >= 15:
        try:
            item_id = int(fields[0])
            target_name = fields[6]
            pos_map_id = int(fields[10])
            pos_x = int(fields[12])
            pos_y = int(fields[13])
            tid = int(fields[14])
            
            # tid 38 is "Điểm Chuyển Tiếp" (Teleport Portal)
            if tid == 38 or target_name in name_to_map_id:
                t_mid = name_to_map_id.get(target_name)
                # If target map has a safe_x, safe_y, get destination coords
                dst_safe_x, dst_safe_y = None, None
                if t_mid and t_mid in maps_db:
                    dst_safe_x = maps_db[t_mid]["safe_x"]
                    dst_safe_y = maps_db[t_mid]["safe_y"]
                
                portal_entry = {
                    "id": item_id,
                    "target_name": target_name,
                    "target_map_id": t_mid,
                    "x": pos_x,
                    "y": pos_y,
                    "dest_x": dst_safe_x,
                    "dest_y": dst_safe_y
                }
                if pos_map_id not in portals_by_map:
                    portals_by_map[pos_map_id] = []
                portals_by_map[pos_map_id].append(portal_entry)
        except Exception:
            pass

print(f"Loaded portals across {len(portals_by_map)} maps.")

# -------------------------------------------------------------
# 3. Parse WorldMap.as Coordinates
# -------------------------------------------------------------
world_map_pins = {}
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
        world_map_pins[mid] = {
            "continent": continent,
            "world_x": x,
            "world_y": y
        }

print(f"Loaded {len(world_map_pins)} World Map pins.")

# -------------------------------------------------------------
# 4. Copy WorldMap Images (WorldMap1.jpg & WorldMap2.jpg)
# -------------------------------------------------------------
wm1_hash = hashlib.md5("resource/ui/WorldMap1.jpg".encode("utf-8")).hexdigest()
wm2_hash = hashlib.md5("resource/ui/WorldMap2.jpg".encode("utf-8")).hexdigest()

out_wm1_path = os.path.join(OUT_WORLDMAP_DIR, "world_map_1.jpg")
out_wm2_path = os.path.join(OUT_WORLDMAP_DIR, "world_map_2.jpg")

with open(os.path.join(RES_DIR, wm1_hash), "rb") as f_in, open(out_wm1_path, "wb") as f_out:
    f_out.write(f_in.read())

with open(os.path.join(RES_DIR, wm2_hash), "rb") as f_in, open(out_wm2_path, "wb") as f_out:
    f_out.write(f_in.read())

print("World Map 1 and World Map 2 images saved to assets/worldmap/.")

# -------------------------------------------------------------
# 5. Extract Map Images, Collision, and Thumbnails for all Maps
# -------------------------------------------------------------
extracted_maps = []
total_extracted = 0

for mid, m in sorted(maps_db.items()):
    scene_folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    map_jpg_path = f"{scene_folder}/MAP_0_0.jpg"
    map_jpg_hash = hashlib.md5(map_jpg_path.encode("utf-8")).hexdigest()
    
    if map_jpg_hash not in existing_res:
        continue
    
    map_dir = os.path.join(OUT_MAPS_DIR, f"map_{mid}")
    os.makedirs(map_dir, exist_ok=True)
    
    # 5.1 Copy background image (bg.jpg)
    src_jpg = os.path.join(RES_DIR, map_jpg_hash)
    dst_jpg = os.path.join(map_dir, "bg.jpg")
    with open(src_jpg, "rb") as fi, open(dst_jpg, "wb") as fo:
        fo.write(fi.read())
    
    # 5.2 Create crisp thumbnail (thumb.webp)
    dst_thumb = os.path.join(map_dir, "thumb.webp")
    try:
        im = Image.open(src_jpg)
        im.thumbnail((260, 180))
        im.save(dst_thumb, "WEBP", quality=80)
    except Exception as e:
        print(f"Warning generating thumb for map {mid}: {e}")

    # 5.3 Extract collision.bin & dimensions
    hit_path = f"{scene_folder}/MAP_HIT_NEW.swf"
    hit_hash = hashlib.md5(hit_path.encode("utf-8")).hexdigest()
    
    col_width, col_height = m["width"], m["height"]
    has_collision = False
    
    if hit_hash in existing_res:
        try:
            with open(os.path.join(RES_DIR, hit_hash), "rb") as f:
                hdata = f.read()
            decomp = zlib.decompress(hdata[8:]) if hdata[:3] == b"CWS" else hdata[8:]
            full = b"FWS\t" + hdata[4:8] + decomp
            pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
            raw_collision = None
            tag72_data = None
            while pos < len(full):
                hdr = int.from_bytes(full[pos:pos+2], "little")
                t_type = hdr >> 6
                t_len = hdr & 0x3F
                pos += 2
                if t_len == 0x3F:
                    t_len = int.from_bytes(full[pos:pos+4], "little")
                    pos += 4
                tag_data = full[pos:pos+t_len]
                if t_type == 87:
                    payload = tag_data[6:]
                    try: raw_collision = zlib.decompress(payload)
                    except: raw_collision = payload
                elif t_type == 72:
                    tag72_data = tag_data
                pos += t_len
            
            if raw_collision:
                dst_col = os.path.join(map_dir, "collision.bin")
                with open(dst_col, "wb") as fc:
                    fc.write(raw_collision)
                has_collision = True
                
                # Parse exact dimensions from Tag 72 doubles
                if tag72_data:
                    for off in range(4, min(35, len(tag72_data)-16)):
                        try:
                            d1 = struct.unpack("<d", tag72_data[off:off+8])[0]
                            d2 = struct.unpack("<d", tag72_data[off+8:off+16])[0]
                            if 400 <= d1 <= 8000 and 400 <= d2 <= 8000:
                                col_width = round(d1)
                                col_height = round(d2)
                                break
                        except: pass
                
                # Verify w * h / 8 == len(raw_collision)
                r_bits = len(raw_collision) * 8
                if abs(col_width * col_height - r_bits) > 32:
                    # search around dimensions
                    for cw in range(m["width"] - 50, m["width"] + 250):
                        ch = round(r_bits / cw)
                        if abs(cw * ch - r_bits) <= 8 and abs(ch - m["height"]) < 250:
                            col_width, col_height = cw, ch
                            break
        except Exception as e:
            print(f"Warning extracting collision for map {mid}: {e}")

    pin_info = world_map_pins.get(mid)
    continent = pin_info["continent"] if pin_info else (1 if mid <= 54 else 2)
    world_x = pin_info["world_x"] if pin_info else None
    world_y = pin_info["world_y"] if pin_info else None
    
    portals = portals_by_map.get(mid, [])
    
    map_meta = {
        "id": mid,
        "name": m["name"],
        "info": m["info"],
        "level": m["level"],
        "width": m["width"],
        "height": m["height"],
        "col_width": col_width,
        "col_height": col_height,
        "has_collision": has_collision,
        "safe_x": m["safe_x"],
        "safe_y": m["safe_y"],
        "continent": continent,
        "world_x": world_x,
        "world_y": world_y,
        "bg_image": f"assets/maps/map_{mid}/bg.jpg",
        "thumb": f"assets/maps/map_{mid}/thumb.webp",
        "collision_bin": f"assets/maps/map_{mid}/collision.bin" if has_collision else None,
        "portals": portals,
        "creatures_count": len(m["creatures"])
    }
    
    # Save meta.json
    with open(os.path.join(map_dir, "meta.json"), "w", encoding="utf-8") as fm:
        json.dump(map_meta, fm, indent=2, ensure_ascii=False)
        
    extracted_maps.append(map_meta)
    total_extracted += 1

print(f"\n=======================================================")
print(f"EXTRAÇÃO COMPLETA DOS MAPAS DE MAGIC CAMPUS")
print(f"Total de mapas extraídos e catalogados: {total_extracted}")
print(f"Mapas no Continente 1 (Vô Ưu): {sum(1 for m in extracted_maps if m['continent'] == 1)}")
print(f"Mapas no Continente 2 (Thần Thánh): {sum(1 for m in extracted_maps if m['continent'] == 2)}")
print(f"Mapas com Malha de Colisão Binária: {sum(1 for m in extracted_maps if m['has_collision'])}")
print(f"Total de Portais Interligados: {sum(len(m['portals']) for m in extracted_maps)}")
print(f"=======================================================")

# Save catalog.json
catalog_data = {
    "version": "1.3.0",
    "total_maps": len(extracted_maps),
    "continents": [
        {
            "id": 1,
            "name": "Đại Lục Vô Ưu (Continente Principal)",
            "image": "assets/worldmap/world_map_1.jpg",
            "width": 900,
            "height": 570,
            "maps_count": sum(1 for m in extracted_maps if m["continent"] == 1)
        },
        {
            "id": 2,
            "name": "Đại Lục Thần Thánh (Novo Continente)",
            "image": "assets/worldmap/world_map_2.jpg",
            "width": 900,
            "height": 570,
            "maps_count": sum(1 for m in extracted_maps if m["continent"] == 2)
        }
    ],
    "maps": extracted_maps
}

catalog_out = os.path.join(OUT_MAPS_DIR, "catalog.json")
with open(catalog_out, "w", encoding="utf-8") as f:
    json.dump(catalog_data, f, indent=2, ensure_ascii=False)

print(f"Catálogo mestre de mapas salvo com sucesso em: {catalog_out}")
