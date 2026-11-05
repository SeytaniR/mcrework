import os, sys, json, hashlib, zlib, struct
sys.stdout.reconfigure(encoding='utf-8')

RES_DIR = r"mcgame\frontend\s\res"

for mid in [1, 2, 3, 4, 5, 9, 22]:
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    h = hashlib.md5(f"{folder}/MAP_HIT_NEW.swf".encode("utf-8")).hexdigest()
    p = os.path.join(RES_DIR, h)
    if not os.path.exists(p):
        print(f"Map {mid}: MAP_HIT_NEW.swf NOT FOUND")
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
    if abc_body:
        for i in range(len(abc_body) - 8):
            try:
                d = struct.unpack("<d", abc_body[i:i+8])[0]
                if 100.0 <= d <= 20000.0:
                    doubles.append((i, d))
            except Exception:
                pass
    print(f"Map {mid}: raw_col_len={raw_col_len} bytes (bits={raw_col_len*8}) | doubles={doubles}")
