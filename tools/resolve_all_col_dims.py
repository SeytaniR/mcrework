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

def get_col_data(mid):
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    hit_hash = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    path = os.path.join(RES_DIR, hit_hash)
    if not os.path.exists(path):
        return None, 0, []
    with open(path, "rb") as f:
        data = f.read()
    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    raw = None
    abc_body = None
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4
        tag_data = full[pos:pos+t_len]
        if t_type == 87:
            payload = tag_data[6:]
            try: raw = zlib.decompress(payload)
            except: raw = payload
        elif t_type == 72:
            abc_body = tag_data
        pos += t_len
    
    # parse numbers from abc_body
    numbers = []
    if abc_body:
        p = 4
        def read_u30():
            nonlocal p
            res, shift = 0, 0
            while p < len(abc_body):
                b = abc_body[p]
                p += 1
                res |= (b & 0x7F) << shift
                shift += 7
                if not (b & 0x80): break
            return res
        try:
            n_ints = read_u30()
            for _ in range(1, min(n_ints, 20)):
                v = read_u30()
                if 400 <= v <= 10000: numbers.append(v)
            n_uints = read_u30()
            for _ in range(1, min(n_uints, 20)):
                v = read_u30()
                if 400 <= v <= 10000: numbers.append(v)
            n_doubles = read_u30()
            for _ in range(1, min(n_doubles, 20)):
                if p + 8 <= len(abc_body):
                    dv = struct.unpack("<d", abc_body[p:p+8])[0]
                    p += 8
                    if 400 <= dv <= 10000:
                        numbers.append(round(dv))
        except Exception:
            pass

    return raw, len(raw) if raw else 0, numbers

resolved = 0
for m in cat:
    mid = m["id"]
    w, h = m["width"], m["height"]
    raw, r_len, numbers = get_col_data(mid)
    if not raw: continue
    
    total_bits = r_len * 8
    best_w, best_h = None, None
    
    # Check pairs from numbers
    for n1 in numbers:
        for n2 in numbers:
            if abs(n1 * n2 - total_bits) <= 8:
                if abs(n1 - w) < 200 and abs(n2 - h) < 200:
                    best_w, best_h = n1, n2
                    break
        if best_w: break
        
    # Fallback to search around image dimensions
    if not best_w:
        for cw in range(w - 50, w + 200):
            ch = round(total_bits / cw)
            if abs(cw * ch - total_bits) <= 8 and abs(ch - h) < 200:
                best_w, best_h = cw, ch
                break
                
    if best_w and best_h:
        resolved += 1
        m["col_width"] = best_w
        m["col_height"] = best_h

print(f"Total maps with exact collision mesh dimensions resolved: {resolved}/{len(cat)}")
for m in cat[:15]:
    print(f"Map {m['id']:2d} [{m['name']:<18}]: Img ({m['width']}x{m['height']}) -> Col ({m.get('col_width')}x{m.get('col_height')})")
