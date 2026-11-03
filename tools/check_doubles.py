import os, sys, zlib, hashlib, struct, json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")

with open(os.path.join(BASE_DIR, "tools", "visual_maps_catalog.json"), "r", encoding="utf-8") as f:
    cat = json.load(f)["maps"]

def get_doubles(mid):
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    hit_hash = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    path = os.path.join(RES_DIR, hit_hash)
    if not os.path.exists(path): return None
    with open(path, "rb") as f: data = f.read()
    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4
        tag_data = full[pos:pos+t_len]
        if t_type == 72:
            for off in range(4, min(35, len(tag_data)-16)):
                try:
                    d1 = struct.unpack("<d", tag_data[off:off+8])[0]
                    d2 = struct.unpack("<d", tag_data[off+8:off+16])[0]
                    if 400 <= d1 <= 8000 and 400 <= d2 <= 8000:
                        return (round(d1), round(d2), off)
                except Exception:
                    pass
        pos += t_len
    return None

found = 0
for m in cat:
    res = get_doubles(m["id"])
    if res:
        found += 1
        m["hit_w"] = res[0]
        m["hit_h"] = res[1]

print(f"Found exact width & height in Tag 72 for: {found}/{len(cat)} maps!")
for m in cat[:20]:
    print(f"Map {m['id']:3d} [{m['name']:<18}]: Img ({m['width']}x{m['height']}) -> Hit ({m.get('hit_w')}x{m.get('hit_h')})")
