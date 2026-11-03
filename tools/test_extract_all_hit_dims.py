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

def extract_hit_dims(mid):
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    hit_hash = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    path = os.path.join(RES_DIR, hit_hash)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
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
        if t_type == 72: # DoABC
            name_end = tag_data.find(b"\x00", 4)
            p = name_end + 1 + 4 # after minor (2), major (2)
            def read_u30():
                nonlocal p
                res, shift = 0, 0
                while True:
                    b = tag_data[p]
                    p += 1
                    res |= (b & 0x7F) << shift
                    shift += 7
                    if not (b & 0x80): break
                return res
            n_ints = read_u30()
            for _ in range(1, n_ints): read_u30()
            n_uints = read_u30()
            for _ in range(1, n_uints): read_u30()
            n_doubles = read_u30()
            doubles = []
            for _ in range(1, n_doubles):
                doubles.append(struct.unpack("<d", tag_data[p:p+8])[0])
                p += 8
            if len(doubles) >= 2:
                return (round(doubles[0]), round(doubles[1]))
        pos += t_len
    return None

results = []
success = 0
for m in cat:
    mid = m["id"]
    dims = extract_hit_dims(mid)
    if dims:
        success += 1
        results.append((mid, m["name"], m["width"], m["height"], dims[0], dims[1]))

print(f"Extracted collision dimensions: {success}/{len(cat)} maps!")
for r in results[:20]:
    print(f"Map {r[0]:3d} [{r[1]:<20}]: Image=({r[2]}x{r[3]}) -> Col=({r[4]}x{r[5]})")
