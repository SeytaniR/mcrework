import os, sys, json, hashlib, zlib, struct
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
FFDEC = os.path.join(BASE_DIR, "tools", "ffdec", "ffdec-cli.exe")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    maps = json.load(f)["maps"]

# Test on maps 1, 2, 3, 4, 5, 9, 22
for mid in [1, 2, 3, 4, 5, 9, 22]:
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, h)
    if not os.path.exists(swf_p): continue
    
    xml_p = f"tools/test_hit_{mid}.xml"
    if not os.path.exists(xml_p):
        import subprocess
        subprocess.run([FFDEC, "-swf2xml", swf_p, xml_p], capture_output=True)
        
    tree = ET.parse(xml_p)
    root = tree.getroot()
    abc = root.find('.//abc')
    
    # Pool
    c_pool = abc.find('constants')
    ints = [int(it.text) if it.text and not it.attrib.get('isNull') else None for it in c_pool.findall('.//constant_int/item')]
    uints = [int(it.text) if it.text and not it.attrib.get('isNull') else None for it in c_pool.findall('.//constant_uint/item')]
    doubles = [float(it.text) if it.text and not it.attrib.get('isNull') else None for it in c_pool.findall('.//constant_double/item')]
    strings = [it.text if it.text and not it.attrib.get('isNull') else "" for it in c_pool.findall('.//constant_string/item')]
    
    # Method bodies
    bodies = abc.findall('.//bodies/item')
    # Find constructor of ClassBytes
    # It sets width and height
    for b in bodies:
        code_hex = b.attrib.get('codeBytes', '')
        # Let's inspect code bytes
        # Opcode 0x61 is setproperty
        # Opcode 0x2f is pushdouble
        # Opcode 0x2d is pushint
        # Opcode 0x2e is pushuint
        # Opcode 0x24 is pushbyte
        # Opcode 0x25 is pushshort
        b_bytes = bytes.fromhex(code_hex)
        print(f"Map {mid} Body len {len(b_bytes)}: hex={code_hex[:60]}")
