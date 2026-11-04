import sys, os, zlib, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('tools/found_effects.json', 'r', encoding='utf-8') as f:
    effects = json.load(f)

print(f"Total effects to inspect: {len(effects)}")

def inspect_swf(h):
    p = os.path.join('mcgame/frontend/s/res', h)
    with open(p, 'rb') as f:
        data = f.read()

    decomp = zlib.decompress(data[8:]) if data[:3] == b'CWS' else data[8:]
    full = b'FWS\t' + data[4:8] + decomp

    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    tags = {}
    symbols = []
    bitmaps = []
    shapes = []
    sprites = []
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], 'little')
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], 'little')
            pos += 4
        tag_data = full[pos:pos+t_len]
        tags[t_type] = tags.get(t_type, 0) + 1

        if t_type in (36, 35, 20, 21): # Bitmaps
            cid = int.from_bytes(tag_data[:2], 'little')
            bitmaps.append((cid, t_type, t_len))
        elif t_type in (2, 22, 32, 83): # Shapes
            cid = int.from_bytes(tag_data[:2], 'little')
            shapes.append((cid, t_type, t_len))
        elif t_type == 39: # DefineSprite
            sid = int.from_bytes(tag_data[:2], 'little')
            fc = int.from_bytes(tag_data[2:4], 'little')
            sprites.append((sid, fc, t_len))
        elif t_type == 76: # SymbolClass
            num_sym = int.from_bytes(tag_data[:2], 'little')
            spos = 2
            for _ in range(num_sym):
                cid = int.from_bytes(tag_data[spos:spos+2], 'little')
                null_idx = tag_data.find(b'\x00', spos+2)
                name = tag_data[spos+2:null_idx].decode('utf-8', errors='ignore')
                symbols.append((cid, name))
                spos = null_idx + 1

        pos += t_len
    return {
        'bitmaps': len(bitmaps),
        'shapes': len(shapes),
        'sprites': len(sprites),
        'symbols': symbols,
        'tag_counts': tags,
        'sprite_frames': [s[1] for s in sprites]
    }

bmp_effects = 0
shape_effects = 0
for path, h in sorted(effects.items())[:25]:
    info = inspect_swf(h)
    if info['bitmaps'] > 0:
        bmp_effects += 1
    if info['shapes'] > 0:
        shape_effects += 1
    print(f"{os.path.basename(path)} ({h[:8]}): bmps={info['bitmaps']}, shapes={info['shapes']}, sprites={info['sprites']}, frames={info['sprite_frames']}, symbols={info['symbols']}")

# Overall statistics
all_with_bmps = 0
all_with_shapes = 0
for path, h in effects.items():
    info = inspect_swf(h)
    if info['bitmaps'] > 0:
        all_with_bmps += 1
    if info['shapes'] > 0:
        all_with_shapes += 1

print(f"\nAcross all {len(effects)} effects:")
print(f"  Effects with bitmaps (Lossless/JPEG): {all_with_bmps}")
print(f"  Effects with vector shapes (DefineShape): {all_with_shapes}")
