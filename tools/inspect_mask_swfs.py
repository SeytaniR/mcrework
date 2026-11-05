import subprocess, hashlib, os
import xml.etree.ElementTree as ET

FFDEC = r"tools\ffdec\ffdec-cli.exe"
RES_DIR = r"mcgame\frontend\s\res"

for mid in [1, 2, 3, 4, 9, 22]:
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_MASK.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, h)
    if not os.path.exists(swf_p): continue
    
    xml_p = f"tools/test_mask_{mid}.xml"
    if not os.path.exists(xml_p):
        subprocess.run([FFDEC, "-swf2xml", swf_p, xml_p], capture_output=True)
        
    tree = ET.parse(xml_p)
    root = tree.getroot()
    rect = root.find('displayRect')
    tags = root.find('tags')
    
    # Check PlaceObjects
    pos = []
    shapes = []
    for item in tags.findall('item'):
        t_type = item.attrib.get('type', '')
        if 'PlaceObject' in t_type:
            mat = item.find('matrix')
            tx = float(mat.attrib.get('translateX', 0))/20.0 if mat is not None else 0
            ty = float(mat.attrib.get('translateY', 0))/20.0 if mat is not None else 0
            scaleX = float(mat.attrib.get('scaleX', 1)) if mat is not None and 'scaleX' in mat.attrib else 1
            scaleY = float(mat.attrib.get('scaleY', 1)) if mat is not None and 'scaleY' in mat.attrib else 1
            pos.append((item.attrib.get('characterId'), tx, ty, scaleX, scaleY))
        elif 'Shape' in t_type:
            cid = item.attrib.get('shapeId')
            for fs in item.iter('item'):
                if fs.attrib.get('type') == 'FILLSTYLE':
                    mat = fs.find('bitmapMatrix')
                    tx = float(mat.attrib.get('translateX', 0))/20.0 if mat is not None else 0
                    ty = float(mat.attrib.get('translateY', 0))/20.0 if mat is not None else 0
                    scaleX = float(mat.attrib.get('scaleX', 1)) if mat is not None and 'scaleX' in mat.attrib else 1
                    scaleY = float(mat.attrib.get('scaleY', 1)) if mat is not None and 'scaleY' in mat.attrib else 1
                    shapes.append((cid, fs.attrib.get('bitmapId'), tx, ty, scaleX, scaleY))
                    
    print(f"\n--- MAP {mid} MASK SWF ---")
    print(f"displayRect: Xmax={rect.attrib.get('Xmax')}, Ymax={rect.attrib.get('Ymax')}")
    print(f"PlaceObjects: {pos[:5]}")
    print(f"Shapes/Fills: {shapes[:5]}")
