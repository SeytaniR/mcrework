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

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    maps = json.load(f)["maps"]

def test_map_mask_pipeline(mid):
    m = next(m for m in maps if m["id"] == mid)
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_MASK.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, h)
    if not os.path.exists(swf_p):
        print(f"Map {mid}: No MAP_MASK.swf")
        return
        
    bw, bh = m["width"], m["height"]
    print(f"\n=== Testing Pipeline for Map {mid} ({m['name']}) [Dim: {bw}x{bh}] ===")
    
    with tempfile.TemporaryDirectory() as tmp:
        # 1. Export shape as PNG
        subprocess.run([FFDEC, "-format", "shape:png", "-export", "shape", tmp, swf_p], capture_output=True)
        # 2. Export XML
        xml_p = os.path.join(tmp, "mask.xml")
        subprocess.run([FFDEC, "-swf2xml", swf_p, xml_p], capture_output=True)
        
        tree = ET.parse(xml_p)
        root = tree.getroot()
        tags = root.find('tags')
        
        # Map shapeId -> (Xmin, Ymin)
        shape_origins = {}
        for item in tags.findall('item'):
            if 'Shape' in item.attrib.get('type', ''):
                sid = item.attrib.get('shapeId')
                bounds = item.find('shapeBounds')
                if bounds is not None:
                    xmin = float(bounds.attrib.get('Xmin', 0)) / 20.0
                    ymin = float(bounds.attrib.get('Ymin', 0)) / 20.0
                    shape_origins[sid] = (xmin, ymin)
                    
        # Check PlaceObjects
        po_offsets = {}
        for item in tags.findall('item'):
            if 'PlaceObject' in item.attrib.get('type', ''):
                cid = item.attrib.get('characterId')
                mat = item.find('matrix')
                tx = float(mat.attrib.get('translateX', 0)) / 20.0 if mat is not None else 0
                ty = float(mat.attrib.get('translateY', 0)) / 20.0 if mat is not None else 0
                po_offsets[cid] = (tx, ty)
                
        # For each exported shape PNG
        pngs = [f for f in os.listdir(tmp) if f.endswith('.png')]
        print(f"Exported {len(pngs)} shape PNGs: {pngs}")
        
        clusters = []
        for png in pngs:
            sid = os.path.splitext(png)[0]
            sh_orig = shape_origins.get(sid, (0.0, 0.0))
            po_off = po_offsets.get(sid, (0.0, 0.0))
            world_x0 = sh_orig[0] + po_off[0]
            world_y0 = sh_orig[1] + po_off[1]
            
            im = Image.open(os.path.join(tmp, png))
            print(f"  Shape {sid}: size={im.size}, origin=({world_x0}, {world_y0})")
            
            # Segment into clusters
            arr = np.array(im)
            if arr.shape[2] < 4: continue
            alpha_mask = arr[:, :, 3] > 20
            labeled, num_features = label(alpha_mask)
            objs = find_objects(labeled)
            
            for i, obj in enumerate(objs):
                sy, sx = obj
                w = sx.stop - sx.start
                h = sy.stop - sy.start
                area = np.sum(labeled[obj] == (i + 1))
                if area >= 120 and w >= 25 and h >= 25:
                    c_world_x = round(world_x0 + sx.start, 2)
                    c_world_y = round(world_y0 + sy.start, 2)
                    # Filter off-map
                    if c_world_x + w < 0 or c_world_y + h < 0: continue
                    if c_world_x >= bw or c_world_y >= bh: continue
                    clusters.append({
                        "sid": sid,
                        "x": c_world_x,
                        "y": c_world_y,
                        "w": w,
                        "h": h,
                        "area": int(area)
                    })
                    
        print(f"Generated {len(clusters)} valid on-map clusters:")
        for c in clusters[:8]:
            print(f"  x={c['x']:<8} y={c['y']:<8} w={c['w']:<5} h={c['h']:<5} area={c['area']}")
            
        # Verify alignment with background image!
        bg_p = os.path.join("web", m["bg_image"])
        bg_img = Image.open(bg_p).convert("RGB")
        bg_arr = np.array(bg_img, dtype=np.float32)
        
        diffs = []
        for c in clusters:
            # Check cluster slice
            # World coords on bg
            bx1 = max(0, int(c['x']))
            by1 = max(0, int(c['y']))
            bx2 = min(bw, bx1 + c['w'])
            by2 = min(bh, by1 + c['h'])
            if bx2 <= bx1 or by2 <= by1: continue
            
            # Crop from shape
            # In shape coords:
            sh_x1 = int(bx1 - world_x0)
            sh_y1 = int(by1 - world_y0)
            sh_x2 = sh_x1 + (bx2 - bx1)
            sh_y2 = sh_y1 + (by2 - by1)
            if sh_x1 < 0 or sh_y1 < 0 or sh_x2 > im.size[0] or sh_y2 > im.size[1]: continue
            
            patch_sh = arr[sh_y1:sh_y2, sh_x1:sh_x2]
            patch_bg = bg_arr[by1:by2, bx1:bx2]
            op_mask = patch_sh[:, :, 3] > 200
            if np.sum(op_mask) > 100:
                diff = np.mean(np.abs(patch_bg[op_mask] - patch_sh[:, :, :3][op_mask]))
                diffs.append(diff)
                
        if diffs:
            print(f"--> Average pixel color difference with bg across {len(diffs)} clusters: {np.mean(diffs):.2f} / 255.0")
        else:
            print("--> No high-opacity overlap to measure diff.")

test_map_mask_pipeline(2)
test_map_mask_pipeline(9)
test_map_mask_pipeline(22)
