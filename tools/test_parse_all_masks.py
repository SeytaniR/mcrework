import xml.etree.ElementTree as ET
import os, sys, json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
TEST_DIR = os.path.join(BASE_DIR, "tools", "test_masks_all")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

def parse_swf_masks(xml_path, img_dir):
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

    # If no PlaceObjects found placed instances, but shapes exist:
    if not placed_instances:
        for cid, fills in shapes.items():
            for s_fill in fills:
                placed_instances.append({
                    'bitmap_id': s_fill['bitmapId'],
                    'x': round(s_fill['tx'], 2),
                    'y': round(s_fill['ty'], 2)
                })

    return placed_instances

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    maps = json.load(f)["maps"]

all_parsed = {}
for m in maps:
    mid = m["id"]
    xml_p = os.path.join(TEST_DIR, f"m_{mid}", "mask.xml")
    img_d = os.path.join(TEST_DIR, f"m_{mid}")
    if os.path.exists(xml_p):
        insts = parse_swf_masks(xml_p, img_d)
        all_parsed[mid] = (m["name"], insts)

print(f"Total maps parsed: {len(all_parsed)}")
for mid, (name, insts) in sorted(all_parsed.items()):
    print(f"Map {mid:2d} [{name:<20}]: {len(insts)} masks -> {[ (x['bitmap_id'], x['x'], x['y']) for x in insts[:3] ]}")
