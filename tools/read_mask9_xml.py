import xml.etree.ElementTree as ET

tree = ET.parse('tools/test_mask_9.xml')
root = tree.getroot()
tags = root.find('tags')
for item in tags.findall('item'):
    t_type = item.attrib.get('type')
    cid = item.attrib.get('shapeId') or item.attrib.get('characterId')
    print(t_type, cid)
    if 'Shape' in t_type:
        # Check edges or bounds
        bounds = item.find('shapeBounds')
        if bounds is not None:
            print("  shapeBounds:", bounds.attrib)
        for fs in item.iter('item'):
            if fs.attrib.get('type') == 'FILLSTYLE':
                mat = fs.find('bitmapMatrix')
                tx = float(mat.attrib.get('translateX', 0))/20.0 if mat is not None else 0
                ty = float(mat.attrib.get('translateY', 0))/20.0 if mat is not None else 0
                print(f"  FILLSTYLE bmp={fs.attrib.get('bitmapId')}, tx={tx}, ty={ty}")
