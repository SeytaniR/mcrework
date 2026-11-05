import os, sys, json, hashlib, zlib, struct
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
FFDEC = os.path.join(BASE_DIR, "tools", "ffdec", "ffdec-cli.exe")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    cat_data = json.load(f)
    maps = cat_data["maps"]

print(f"Calibrating exact collision strides for {len(maps)} maps...")

def get_exact_as3_hit_dims(mid):
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    swf_p = os.path.join(RES_DIR, h)
    if not os.path.exists(swf_p):
        return None, None
        
    with open(swf_p, "rb") as f:
        data = f.read()
    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    abc_body = None
    raw_col_len = 0
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4
        if t_type == 72:
            abc_body = full[pos:pos+t_len]
        elif t_type == 87:
            payload = full[pos+6:pos+t_len]
            try: raw_col_len = len(zlib.decompress(payload))
            except: raw_col_len = len(payload)
        pos += t_len
        
    if not abc_body:
        return None, None

    # Parse AVM2 Constant Pool in ABC body
    # ABC format: major(16), minor(16), cpool
    p = 4
    # constant_int
    def read_u30(buf, offset):
        res = 0
        shift = 0
        while True:
            b = buf[offset]
            offset += 1
            res |= (b & 0x7F) << shift
            if not (b & 0x80): break
            shift += 7
        return res, offset
        
    int_count, p = read_u30(abc_body, p)
    ints = [0]
    for _ in range(1, int_count):
        val, p = read_u30(abc_body, p)
        # convert to signed 32-bit
        if val >= 0x80000000: val -= 0x100000000
        ints.append(val)
        
    uint_count, p = read_u30(abc_body, p)
    uints = [0]
    for _ in range(1, uint_count):
        val, p = read_u30(abc_body, p)
        uints.append(val)
        
    double_count, p = read_u30(abc_body, p)
    doubles = [0.0]
    for _ in range(1, double_count):
        d = struct.unpack("<d", abc_body[p:p+8])[0]
        doubles.append(d)
        p += 8

    # Search for push opcodes followed by setproperty
    # In all MAP_HIT_NEW.swf, width is set first, then height.
    # We can scan for doubles or ints that match the dimensions
    bits = raw_col_len * 8
    
    # Try all pairs of (w, h) from doubles and ints
    candidates = []
    for d in doubles[1:]:
        candidates.append(d)
    for u in ints[1:] + uints[1:]:
        candidates.append(float(u))
        
    # Find candidate w, h such that int(w) * int(h) is close to bits
    best_w, best_h = None, None
    min_diff = 999999999
    
    for w_val in candidates:
        if w_val < 300 or w_val > 15000: continue
        w_uint = int(w_val)
        for h_val in candidates:
            if h_val < 300 or h_val > 15000: continue
            h_uint = int(h_val)
            diff = abs(w_uint * h_uint - bits)
            if diff < min_diff and diff <= 128:
                min_diff = diff
                best_w = w_uint
                best_h = h_uint
                
    if best_w and best_h:
        return best_w, best_h
        
    # If not found via exact pair, test if bits / int(w) == int(h)
    for w_val in candidates:
        if 300 <= w_val <= 15000:
            w_uint = int(w_val)
            calc_h = bits // w_uint
            if abs(w_uint * calc_h - bits) <= 128:
                return w_uint, calc_h
                
    return None, None

fixed_count = 0
for m in maps:
    mid = m["id"]
    bw, bh = m["width"], m["height"]
    old_cw, old_ch = m.get("col_width"), m.get("col_height")
    
    cw, ch = get_exact_as3_hit_dims(mid)
    if cw and ch:
        if cw != old_cw or ch != old_ch:
            print(f"Map {mid:2d} ({m['name']:<18}): Fixed col dims ({old_cw}x{old_ch}) -> ({cw}x{ch})")
            m["col_width"] = cw
            m["col_height"] = ch
            fixed_count += 1
    else:
        # If no SWF, keep existing or map dims
        pass

print(f"\nSuccessfully calibrated exact strides for {fixed_count} maps.")

with open(MAPS_CAT, "w", encoding="utf-8") as f:
    json.dump(cat_data, f, indent=2)

print("Saved updated catalog.json!")
