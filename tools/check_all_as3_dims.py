import os, sys, json, hashlib, zlib, struct
sys.stdout.reconfigure(encoding='utf-8')

RES_DIR = r"mcgame\frontend\s\res"
MAPS_CAT = r"web\assets\maps\catalog.json"

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    maps = json.load(f)["maps"]

print(f"{'MID':<4} {'Name':<20} {'Cat ColDim':<14} {'Raw Bits':<12} {'Exact W (uint)':<14} {'Exact H (uint)':<14} {'Bits/H':<10} {'Mismatch?'}")
print("-" * 105)

for m in maps:
    mid = m["id"]
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    p = os.path.join(RES_DIR, h)
    if not os.path.exists(p):
        continue
    with open(p, "rb") as f:
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
        
    doubles = []
    ints = []
    if abc_body:
        # Also parse integers from constant_int if present
        # Or look for double values
        for i in range(len(abc_body) - 8):
            try:
                d = struct.unpack("<d", abc_body[i:i+8])[0]
                if 200.0 <= d <= 20000.0:
                    doubles.append(d)
            except Exception:
                pass
                
    bits = raw_col_len * 8
    
    # In ActionScript 3, uint conversion truncates! int(d)
    w_as3 = int(doubles[0]) if doubles else None
    h_as3 = int(doubles[1]) if len(doubles) > 1 else None
    
    cat_cw = m.get("col_width")
    cat_ch = m.get("col_height")
    
    # Check if bits / w_as3 == h_as3 or bits / cat_ch == cat_cw
    bits_over_h = (bits / h_as3) if h_as3 else (bits / cat_ch if cat_ch else 0)
    
    mismatch = ""
    if w_as3 and cat_cw != w_as3:
        mismatch += f"W: cat={cat_cw} vs as3={w_as3} "
    if h_as3 and cat_ch != h_as3:
        mismatch += f"H: cat={cat_ch} vs as3={h_as3} "
    if abs(bits_over_h - round(bits_over_h)) > 0.01:
        mismatch += f"Bits non-integer! ({bits_over_h:.2f}) "
        
    print(f"{mid:<4} {m['name']:<20} {str(cat_cw)+'x'+str(cat_ch):<14} {bits:<12} {str(w_as3):<14} {str(h_as3):<14} {bits_over_h:<10.2f} {mismatch}")
