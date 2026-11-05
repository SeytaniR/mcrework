import os, sys, json, hashlib, subprocess, tempfile
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
    maps_catalog = json.load(f)["maps"]

print(f"Loaded {len(maps_catalog)} maps from catalog.")

def parse_swf_placements(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    tags_elem = root.find('tags')
    if tags_elem is None:
        return []
        
    shapes = {} # cid -> list of {'bitmapId': int, 'tx': float, 'ty': float}
    sprites = {} # cid -> list of {'chid': str, 'tx': float, 'ty': float}
    
    for item in tags_elem.findall('item'):
        t_type = item.attrib.get('type', '')
        cid = item.attrib.get('shapeId') or item.attrib.get('characterId') or item.attrib.get('spriteId')
        
        if 'Shape' in t_type and cid:
            for fs in item.iter('item'):
                if fs.attrib.get('type') == 'FILLSTYLE':
                    bmp = fs.attrib.get('bitmapId')
                    if bmp and bmp != '65535':
                        mat = fs.find('bitmapMatrix')
                        tx = float(mat.attrib.get('translateX', 0))/20.0 if mat is not None else 0
                        ty = float(mat.attrib.get('translateY', 0))/20.0 if mat is not None else 0
                        if cid not in shapes:
                            shapes[cid] = []
                        shapes[cid].append({'bitmapId': int(bmp), 'tx': tx, 'ty': ty})
                        
        elif 'DefineSprite' in t_type and cid:
            children = []
            for sub in item.iter('item'):
                if 'PlaceObject' in sub.attrib.get('type', ''):
                    c_chid = sub.attrib.get('characterId')
                    mat = sub.find('matrix')
                    tx = float(mat.attrib.get('translateX', 0))/20.0 if mat is not None else 0
                    ty = float(mat.attrib.get('translateY', 0))/20.0 if mat is not None else 0
                    children.append({'chid': c_chid, 'tx': tx, 'ty': ty})
            sprites[cid] = children

    placed_instances = []
    
    for item in tags_elem.findall('item'):
        t_type = item.attrib.get('type', '')
        if 'PlaceObject' in t_type:
            cid = item.attrib.get('characterId')
            mat = item.find('matrix')
            po_tx = float(mat.attrib.get('translateX', 0))/20.0 if mat is not None else 0
            po_ty = float(mat.attrib.get('translateY', 0))/20.0 if mat is not None else 0
            
            if cid in sprites:
                for child in sprites[cid]:
                    child_cid = child['chid']
                    if child_cid in shapes:
                        for s_fill in shapes[child_cid]:
                            final_x = po_tx + child['tx'] + s_fill['tx']
                            final_y = po_ty + child['ty'] + s_fill['ty']
                            placed_instances.append({
                                'bitmap_id': s_fill['bitmapId'],
                                'x': round(final_x, 2),
                                'y': round(final_y, 2)
                            })
            elif cid in shapes:
                for s_fill in shapes[cid]:
                    final_x = po_tx + s_fill['tx']
                    final_y = po_ty + s_fill['ty']
                    placed_instances.append({
                        'bitmap_id': s_fill['bitmapId'],
                        'x': round(final_x, 2),
                        'y': round(final_y, 2)
                    })

    if not placed_instances:
        for cid, fills in shapes.items():
            for s_fill in fills:
                placed_instances.append({
                    'bitmap_id': s_fill['bitmapId'],
                    'x': round(s_fill['tx'], 2),
                    'y': round(s_fill['ty'], 2)
                })

    return placed_instances

def extract_tight_clusters(image_path, min_area=120):
    im = Image.open(image_path)
    alpha = np.array(im.split()[-1]) > 15
    labeled, num_features = label(alpha)
    objects = find_objects(labeled)
    clusters = []
    for i, obj in enumerate(objects):
        sy, sx = obj
        w = sx.stop - sx.start
        h = sy.stop - sy.start
        area = np.sum(labeled[obj] == (i + 1))
        if area >= min_area and w >= 25 and h >= 25:
            clusters.append({
                'x': sx.start,
                'y': sy.start,
                'w': w,
                'h': h,
                'crop_box': (sx.start, sy.start, sx.stop, sy.stop),
                'area': int(area)
            })
    return im, clusters

# Process all maps
total_masks_generated = 0
maps_with_masks = 0

for m in maps_catalog:
    mid = m["id"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    mask_path = f"{folder}/MAP_MASK.swf"
    mask_h = hashlib.md5(mask_path.encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, mask_h)
    
    if not os.path.exists(swf_p):
        m["has_masks"] = False
        m["masks_count"] = 0
        continue
        
    map_target_dir = os.path.join(WEB_MAPS_DIR, f"map_{mid}")
    mask_out_dir = os.path.join(map_target_dir, "mask")
    os.makedirs(mask_out_dir, exist_ok=True)
    
    # Export images and XML via FFDec into temporary folder
    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.run([FFDEC, "-export", "image", tmpdir, swf_p], capture_output=True)
        xml_p = os.path.join(tmpdir, "mask.xml")
        subprocess.run([FFDEC, "-swf2xml", swf_p, xml_p], capture_output=True)
        
        png_files = [f for f in os.listdir(tmpdir) if f.endswith(".png")]
        if not png_files:
            m["has_masks"] = False
            m["masks_count"] = 0
            continue
            
        placements = parse_swf_placements(xml_p) if os.path.exists(xml_p) else []
        
        # Determine if Case 1 (discrete placed sprites) or Case 2 (large full-stage overlay)
        is_large_overlay = False
        if len(png_files) == 1:
            im_tmp = Image.open(os.path.join(tmpdir, png_files[0]))
            if im_tmp.size[0] >= 1800 or im_tmp.size[1] >= 1400:
                is_large_overlay = True
            im_tmp.close()
            
        map_masks_data = []
        
        if is_large_overlay:
            # Case 2: Extract tight clusters
            im_src, clusters = extract_tight_clusters(os.path.join(tmpdir, png_files[0]))
            for c_idx, c in enumerate(clusters):
                crop_img = im_src.crop(c["crop_box"])
                out_png_name = f"mask_{c_idx+1}.png"
                out_png_path = os.path.join(mask_out_dir, out_png_name)
                crop_img.save(out_png_path, "PNG", optimize=True)
                
                map_masks_data.append({
                    "bitmap_id": c_idx + 1,
                    "file": f"assets/maps/map_{mid}/mask/{out_png_name}",
                    "x": round(float(c["x"]), 2),
                    "y": round(float(c["y"]), 2),
                    "w": c["w"],
                    "h": c["h"]
                })
            im_src.close()
        else:
            # Case 1: Discrete placed sprites
            # Save all raw exported pngs to mask_out_dir
            bmp_sizes = {}
            for png in png_files:
                bmp_id = int(os.path.splitext(png)[0])
                src_p = os.path.join(tmpdir, png)
                dst_p = os.path.join(mask_out_dir, f"mask_{bmp_id}.png")
                with Image.open(src_p) as im_bmp:
                    bmp_sizes[bmp_id] = im_bmp.size
                    im_bmp.save(dst_p, "PNG", optimize=True)
                    
            # Filter and deduplicate placements
            seen = set()
            for p in placements:
                bmp_id = p["bitmap_id"]
                if bmp_id not in bmp_sizes:
                    continue
                # round coordinates to nearest 5px to deduplicate micro-nudges
                key = (bmp_id, round(p["x"] / 6.0), round(p["y"] / 6.0))
                if key in seen:
                    continue
                seen.add(key)
                
                bw, bh = bmp_sizes[bmp_id]
                map_w = m.get("width", 3000)
                map_h = m.get("height", 2000)
                
                # Filter out completely offscreen placements
                if p["x"] + bw < -50 or p["y"] + bh < -50:
                    continue
                if p["x"] > map_w + 50 or p["y"] > map_h + 50:
                    continue
                    
                map_masks_data.append({
                    "bitmap_id": bmp_id,
                    "file": f"assets/maps/map_{mid}/mask/mask_{bmp_id}.png",
                    "x": round(float(p["x"]), 2),
                    "y": round(float(p["y"]), 2),
                    "w": bw,
                    "h": bh
                })
                
        # Write masks.json for this map
        if map_masks_data:
            json_path = os.path.join(map_target_dir, "masks.json")
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(map_masks_data, jf, indent=2)
            m["has_masks"] = True
            m["masks_count"] = len(map_masks_data)
            maps_with_masks += 1
            total_masks_generated += len(map_masks_data)
            print(f"Map {mid:2d} [{m.get('name'):<20}]: Generated {len(map_masks_data)} masks (type={'Overlay-Clusters' if is_large_overlay else 'Placed-Sprites'})")
        else:
            m["has_masks"] = False
            m["masks_count"] = 0

# Special consistency check for Map 1: ensure both web/assets/map1 and web/assets/maps/map_1 exist
map1_dir = os.path.join(BASE_DIR, "web", "assets", "map1")
map1_masks_json = os.path.join(map1_dir, "masks.json")
if os.path.exists(map1_masks_json):
    with open(map1_masks_json, "r", encoding="utf-8") as f:
        m1_data = json.load(f)
    # Also write to web/assets/maps/map_1/masks.json
    m1_target_dir = os.path.join(WEB_MAPS_DIR, "map_1")
    os.makedirs(os.path.join(m1_target_dir, "mask"), exist_ok=True)
    with open(os.path.join(m1_target_dir, "masks.json"), "w", encoding="utf-8") as f:
        json.dump(m1_data, f, indent=2)
    # copy mask pngs
    import shutil
    for i in range(1, 8):
        s = os.path.join(map1_dir, "mask", f"mask_{i}.png")
        d = os.path.join(m1_target_dir, "mask", f"mask_{i}.png")
        if os.path.exists(s):
            shutil.copy2(s, d)

# Save updated catalog.json
with open(MAPS_CAT, "w", encoding="utf-8") as f:
    json.dump({"total_maps": len(maps_catalog), "maps": maps_catalog}, f, indent=2)

print("\n=======================================================")
print(f"BATCH EXTRACTION COMPLETE!")
print(f"Total Maps with Transparency Masks: {maps_with_masks}")
print(f"Total Mask Elements Configured: {total_masks_generated}")
print("=======================================================")
