import os, sys, json, hashlib, zlib, struct, subprocess, tempfile
import xml.etree.ElementTree as ET
from PIL import Image
import numpy as np
from scipy.ndimage import label, find_objects

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
FFDEC = os.path.join(BASE_DIR, "tools", "ffdec", "ffdec-cli.exe")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")
WEB_MAPS_DIR = os.path.join(BASE_DIR, "web", "assets", "maps")

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    cat_data = json.load(f)
    maps = cat_data["maps"]

print(f"Loaded {len(maps)} maps for comprehensive overhaul.")

# -------------------------------------------------------------------------
# 1. Calibrate Exact Collision Strides from AS3 Bytecode
# -------------------------------------------------------------------------
def get_exact_as3_hit_dims(mid):
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, h)
    if not os.path.exists(swf_p):
        return None, None
        
    with open(swf_p, "rb") as f:
        data = f.read()
    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    abc_body = None
    raw_col_len = 0
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
        elif t_type == 87:
            payload = full[pos+6:pos+t_len]
            try: raw_col_len = len(zlib.decompress(payload))
            except: raw_col_len = len(payload)
        pos += t_len
        
    if not abc_body:
        return None, None

    p = 4
    def read_u30(buf, offset):
        res = 0
        shift = 0
        while True:
            b = buf[offset]
            offset += 1
            res |= (b & 0x7F) << shift
            if not (b & 0x80): break
            shift += 7
        return res, offset
        
    int_count, p = read_u30(abc_body, p)
    ints = [0]
    for _ in range(1, int_count):
        val, p = read_u30(abc_body, p)
        if val >= 0x80000000: val -= 0x100000000
        ints.append(val)
        
    uint_count, p = read_u30(abc_body, p)
    uints = [0]
    for _ in range(1, uint_count):
        val, p = read_u30(abc_body, p)
        uints.append(val)
        
    double_count, p = read_u30(abc_body, p)
    doubles = [0.0]
    for _ in range(1, double_count):
        d = struct.unpack("<d", abc_body[p:p+8])[0]
        doubles.append(d)
        p += 8

    bits = raw_col_len * 8
    candidates = [d for d in doubles[1:]] + [float(u) for u in ints[1:] + uints[1:]]
    
    best_w, best_h = None, None
    min_diff = 999999999
    
    for w_val in candidates:
        if w_val < 300 or w_val > 15000: continue
        w_uint = int(w_val)
        for h_val in candidates:
            if h_val < 300 or h_val > 15000: continue
            h_uint = int(h_val)
            diff = abs(w_uint * h_uint - bits)
            if diff < min_diff and diff <= 128:
                min_diff = diff
                best_w = w_uint
                best_h = h_uint
                
    if best_w and best_h:
        return best_w, best_h
        
    for w_val in candidates:
        if 300 <= w_val <= 15000:
            w_uint = int(w_val)
            calc_h = bits // w_uint
            if abs(w_uint * calc_h - bits) <= 128:
                return w_uint, calc_h
                
    return None, None

# Update collision strides for all maps
for m in maps:
    mid = m["id"]
    cw, ch = get_exact_as3_hit_dims(mid)
    if cw and ch:
        m["col_width"] = cw
        m["col_height"] = ch
        m["has_collision"] = True

print("Step 1 Complete: All collision strides calibrated.")

# -------------------------------------------------------------------------
# 2. Universal Foreground Masks from Shape Renders
# -------------------------------------------------------------------------
total_masks_count = 0
maps_with_masks = 0

for m in maps:
    mid = m["id"]
    bw, bh = m["width"], m["height"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_MASK.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, h)
    
    if not os.path.exists(swf_p):
        m["has_masks"] = False
        m["masks_count"] = 0
        continue
        
    map_target_dir = os.path.join(WEB_MAPS_DIR, f"map_{mid}")
    mask_out_dir = os.path.join(map_target_dir, "mask")
    os.makedirs(mask_out_dir, exist_ok=True)
    
    with tempfile.TemporaryDirectory() as tmp:
        # 1. Export shape as PNG
        subprocess.run([FFDEC, "-format", "shape:png", "-export", "shape", tmp, swf_p], capture_output=True)
        # 2. Export XML
        xml_p = os.path.join(tmp, "mask.xml")
        subprocess.run([FFDEC, "-swf2xml", swf_p, xml_p], capture_output=True)
        
        if not os.path.exists(xml_p):
            continue
            
        tree = ET.parse(xml_p)
        root = tree.getroot()
        tags = root.find('tags')
        if tags is None: continue
        
        shape_origins = {}
        for item in tags.findall('item'):
            if 'Shape' in item.attrib.get('type', ''):
                sid = item.attrib.get('shapeId')
                bounds = item.find('shapeBounds')
                if bounds is not None:
                    xmin = float(bounds.attrib.get('Xmin', 0)) / 20.0
                    ymin = float(bounds.attrib.get('Ymin', 0)) / 20.0
                    shape_origins[sid] = (xmin, ymin)
                    
        po_offsets = {}
        for item in tags.findall('item'):
            if 'PlaceObject' in item.attrib.get('type', ''):
                cid = item.attrib.get('characterId')
                mat = item.find('matrix')
                tx = float(mat.attrib.get('translateX', 0)) / 20.0 if mat is not None else 0
                ty = float(mat.attrib.get('translateY', 0)) / 20.0 if mat is not None else 0
                po_offsets[cid] = (tx, ty)
                
        pngs = [f for f in os.listdir(tmp) if f.endswith('.png')]
        map_masks_data = []
        cluster_idx = 1
        
        for png in sorted(pngs, key=lambda x: int(os.path.splitext(x)[0]) if os.path.splitext(x)[0].isdigit() else 0):
            sid = os.path.splitext(png)[0]
            sh_orig = shape_origins.get(sid, (0.0, 0.0))
            po_off = po_offsets.get(sid, (0.0, 0.0))
            world_x0 = sh_orig[0] + po_off[0]
            world_y0 = sh_orig[1] + po_off[1]
            
            im = Image.open(os.path.join(tmp, png))
            arr = np.array(im)
            if arr.shape[2] < 4: continue
            
            # Segment into clusters
            alpha_mask = arr[:, :, 3] > 20
            labeled, num_features = label(alpha_mask)
            objs = find_objects(labeled)
            
            for i, obj in enumerate(objs):
                sy, sx = obj
                w = sx.stop - sx.start
                h = sy.stop - sy.start
                area = np.sum(labeled[obj] == (i + 1))
                if w >= 25 and h >= 25 and (w * h) >= 400:
                    c_world_x = round(world_x0 + sx.start, 2)
                    c_world_y = round(world_y0 + sy.start, 2)
                    
                    # Filter off-map
                    if c_world_x + w <= 0 or c_world_y + h <= 0: continue
                    if c_world_x >= bw or c_world_y >= bh: continue
                    
                    # Crop image cluster with transparency
                    crop_im = im.crop((sx.start, sy.start, sx.stop, sy.stop))
                    out_png_name = f"mask_{cluster_idx}.png"
                    out_png_path = os.path.join(mask_out_dir, out_png_name)
                    crop_im.save(out_png_path, "PNG", optimize=True)
                    
                    map_masks_data.append({
                        "bitmap_id": cluster_idx,
                        "file": f"assets/maps/map_{mid}/mask/{out_png_name}",
                        "x": c_world_x,
                        "y": c_world_y,
                        "w": w,
                        "h": h
                    })
                    cluster_idx += 1
                    
        if map_masks_data:
            json_path = os.path.join(map_target_dir, "masks.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(map_masks_data, jf, indent=2)
            if mid == 1:
                map1_legacy = os.path.join(BASE_DIR, "web", "assets", "map1")
                with open(os.path.join(map1_legacy, "masks.json"), "w", encoding="utf-8") as jf1:
                    json.dump(map_masks_data, jf1, indent=2)
            m["has_masks"] = True
            m["masks_count"] = len(map_masks_data)
            maps_with_masks += 1
            total_masks_count += len(map_masks_data)
            print(f"Map {mid:2d} [{m['name']:<18}]: Generated {len(map_masks_data)} foreground masks.")
        else:
            m["has_masks"] = False
            m["masks_count"] = 0

print(f"Step 2 Complete: Generated {total_masks_count} masks across {maps_with_masks} maps.")

# -------------------------------------------------------------------------
# 3. Calibrate Portals and Safe Positions to Walkable Tiles
# -------------------------------------------------------------------------
calibrated_portals = 0
calibrated_spawns = 0

for m in maps:
    mid = m["id"]
    bw, bh = m["width"], m["height"]
    cw, ch = m.get("col_width"), m.get("col_height")
    col_p = os.path.join("web", m.get("collision_bin", ""))
    
    if not (cw and ch and os.path.exists(col_p)):
        continue
        
    with open(col_p, "rb") as fc:
        col_bytes = fc.read()
        
    def is_walk(x, y):
        ix = int(x)
        iy = int(y)
        if ix < 0 or ix >= bw or iy < 0 or iy >= bh: return False
        if ix >= cw or iy >= ch: return False
        idx = iy * cw + ix
        b_idx = idx >> 3
        if b_idx >= len(col_bytes): return False
        return (col_bytes[b_idx] & (1 << (idx & 7))) != 0

    def find_walkable(tx, ty, max_r=120):
        if is_walk(tx, ty): return tx, ty
        for r in range(2, max_r, 2):
            for ang_step in range(16):
                ang = ang_step * (2 * 3.14159265 / 16)
                nx = round(tx + np.cos(ang) * r)
                ny = round(ty + np.sin(ang) * r)
                if is_walk(nx, ny):
                    return nx, ny
        return tx, ty
        
    # Check safe_x, safe_y
    sx, sy = m.get("safe_x", bw // 2), m.get("safe_y", bh // 2)
    if not is_walk(sx, sy):
        nsx, nsy = find_walkable(sx, sy, 150)
        m["safe_x"] = nsx
        m["safe_y"] = nsy
        calibrated_spawns += 1
        print(f"Map {mid:2d} ({m['name']}): Nudged safe spawn from ({sx}, {sy}) -> ({nsx}, {nsy})")
        
    # Check portals
    for p in m.get("portals", []):
        px, py = p["x"], p["y"]
        if not is_walk(px, py):
            npx, npy = find_walkable(px, py, 120)
            p["x"] = npx
            p["y"] = npy
            calibrated_portals += 1
            print(f"Map {mid:2d} ({m['name']}): Nudged portal '{p.get('target_name')}' from ({px}, {py}) -> ({npx}, {npy})")

print(f"Step 3 Complete: Calibrated {calibrated_spawns} spawns and {calibrated_portals} portals.")

# Save final catalog.json
with open(MAPS_CAT, "w", encoding="utf-8") as f:
    json.dump(cat_data, f, indent=2)

print("\n=== OVERHAUL COMPLETE: catalog.json successfully saved! ===")
