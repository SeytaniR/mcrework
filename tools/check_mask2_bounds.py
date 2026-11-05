import xml.etree.ElementTree as ET

tree = ET.parse('tools/test_mask_2.xml')
root = tree.getroot()
tags = root.find('tags')
for item in tags.findall('item'):
    t_type = item.attrib.get('type')
    cid = item.attrib.get('shapeId') or item.attrib.get('characterId')
    if 'Shape' in t_type:
        bounds = item.find('shapeBounds')
        if bounds is not None:
            xmin = float(bounds.attrib.get('Xmin', 0)) / 20.0
            ymin = float(bounds.attrib.get('Ymin', 0)) / 20.0
            xmax = float(bounds.attrib.get('Xmax', 0)) / 20.0
            ymax = float(bounds.attrib.get('Ymax', 0)) / 20.0
            print(f"Map 2 Shape {cid} bounds: x=[{xmin}..{xmax}], y=[{ymin}..{ymax}], w={xmax-xmin}, h={ymax-ymin}")
