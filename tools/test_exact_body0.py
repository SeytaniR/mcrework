import os, sys, json, hashlib, zlib, struct
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
FFDEC = os.path.join(BASE_DIR, "tools", "ffdec", "ffdec-cli.exe")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

def parse_body0_dims(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    abc = root.find('.//abc')
    if abc is None: return None, None
    c_pool = abc.find('constants')
    
    ints = [None] + [int(it.text) if it.text and not it.attrib.get('isNull') else 0 for it in c_pool.findall('.//constant_int/item') if not it.attrib.get('isNull')]
    uints = [None] + [int(it.text) if it.text and not it.attrib.get('isNull') else 0 for it in c_pool.findall('.//constant_uint/item') if not it.attrib.get('isNull')]
    doubles = [None] + [float(it.text) if it.text and not it.attrib.get('isNull') else 0.0 for it in c_pool.findall('.//constant_double/item') if not it.attrib.get('isNull')]
    
    body0 = abc.find('.//bodies/item')
    if body0 is None: return None, None
    code = bytes.fromhex(body0.attrib.get('codeBytes', ''))
    
    # We look for:
    # <push_op> <idx> followed within a few bytes by 0x61 (setproperty)
    # The first setproperty is width, the second is height!
    values = []
    i = 0
    while i < len(code):
        op = code[i]
        if op == 0x2f: # pushdouble
            idx = code[i+1] # u30
            val = doubles[idx] if idx < len(doubles) else None
            values.append(val)
            i += 2
        elif op == 0x2d: # pushint
            idx = code[i+1]
            val = ints[idx] if idx < len(ints) else None
            values.append(val)
            i += 2
        elif op == 0x2e: # pushuint
            idx = code[i+1]
            val = uints[idx] if idx < len(uints) else None
            values.append(val)
            i += 2
        elif op == 0x25: # pushshort
            val = int.from_bytes(code[i+1:i+3], 'little')
            values.append(val)
            i += 3
        elif op == 0x24: # pushbyte
            val = code[i+1]
            values.append(val)
            i += 2
        else:
            i += 1
            
    if len(values) >= 2:
        return values[0], values[1]
    return None, None

for mid in [1, 2, 3, 4, 5, 9, 22]:
    xml_p = f"tools/test_hit_{mid}.xml"
    w, h = parse_body0_dims(xml_p)
    print(f"Map {mid}: Exact Constructor W={w}, H={h} (uint: W={int(w) if w else 0}, H={int(h) if h else 0})")
