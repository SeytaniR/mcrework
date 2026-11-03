import os, sys, json, hashlib, zlib, struct

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
MAPS_DIR = os.path.join(BASE_DIR, "web", "assets", "maps")
CATALOG_PATH = os.path.join(MAPS_DIR, "catalog.json")
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")

def read_u30(data, pos):
    result = 0
    shift = 0
    while True:
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, pos

def parse_abc(data):
    pos = 4
    int_count, pos = read_u30(data, pos)
    ints = [0]
    for _ in range(int_count - 1 if int_count > 0 else 0):
        val, pos = read_u30(data, pos)
        ints.append(val)
        
    uint_count, pos = read_u30(data, pos)
    uints = [0]
    for _ in range(uint_count - 1 if uint_count > 0 else 0):
        val, pos = read_u30(data, pos)
        uints.append(val)
        
    double_count, pos = read_u30(data, pos)
    doubles = [0.0]
    for _ in range(double_count - 1 if double_count > 0 else 0):
        val = struct.unpack("<d", data[pos:pos+8])[0]
        pos += 8
        doubles.append(val)
        
    string_count, pos = read_u30(data, pos)
    strings = [""]
    for _ in range(string_count - 1 if string_count > 0 else 0):
        slen, pos = read_u30(data, pos)
        sval = data[pos:pos+slen].decode('utf-8', errors='replace')
        pos += slen
        strings.append(sval)
        
    ns_count, pos = read_u30(data, pos)
    namespaces = [None]
    for _ in range(ns_count - 1 if ns_count > 0 else 0):
        kind = data[pos]; pos += 1
        name_idx, pos = read_u30(data, pos)
        namespaces.append((kind, name_idx))
        
    ns_set_count, pos = read_u30(data, pos)
    ns_sets = [None]
    for _ in range(ns_set_count - 1 if ns_set_count > 0 else 0):
        count, pos = read_u30(data, pos)
        s = []
        for _ in range(count):
            ns_idx, pos = read_u30(data, pos)
            s.append(ns_idx)
        ns_sets.append(s)
        
    multiname_count, pos = read_u30(data, pos)
    multinames = [None]
    for _ in range(multiname_count - 1 if multiname_count > 0 else 0):
        kind = data[pos]; pos += 1
        if kind in (0x07, 0x0D):
            ns, pos = read_u30(data, pos)
            name_idx, pos = read_u30(data, pos)
            multinames.append((kind, ns, name_idx))
        elif kind in (0x09, 0x0E):
            name_idx, pos = read_u30(data, pos)
            ns_set, pos = read_u30(data, pos)
            multinames.append((kind, name_idx, ns_set))
        else:
            multinames.append((kind,))
            
    return {
        "ints": ints,
        "uints": uints,
        "doubles": doubles,
        "strings": strings,
        "multinames": multinames,
        "pos": pos,
        "raw": data
    }

def extract_col_dimensions_from_abc(tag72_data):
    abc = parse_abc(tag72_data)
    width_str_idx = None
    height_str_idx = None
    for idx, s in enumerate(abc["strings"]):
        if s == "width": width_str_idx = idx
        if s == "height": height_str_idx = idx
        
    width_m_idx = None
    height_m_idx = None
    for midx, m in enumerate(abc["multinames"]):
        if m and len(m) >= 3:
            if m[2] == width_str_idx: width_m_idx = midx
            if m[2] == height_str_idx: height_m_idx = midx
            
    raw = abc["raw"]
    
    def get_val_before(pos_61):
        for back in range(1, 6):
            p = pos_61 - back
            op = raw[p]
            if op == 0x2f: # pushdouble
                idx, _ = read_u30(raw, p+1)
                return round(abc["doubles"][idx])
            elif op == 0x2d: # pushint
                idx, _ = read_u30(raw, p+1)
                return abc["ints"][idx]
            elif op == 0x2e: # pushuint
                idx, _ = read_u30(raw, p+1)
                return abc["uints"][idx]
            elif op == 0x25: # pushshort
                idx, _ = read_u30(raw, p+1)
                return idx
            elif op == 0x24: # pushbyte
                return raw[p+1]
        return None

    cw = None
    ch = None
    for i in range(abc["pos"], len(raw)-3):
        if raw[i] == 0x61:
            m_idx, _ = read_u30(raw, i+1)
            if m_idx == width_m_idx:
                cw = get_val_before(i)
            elif m_idx == height_m_idx:
                ch = get_val_before(i)
                
    return cw, ch

# Load catalog
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    cat = json.load(f)

updated_count = 0

for m in cat["maps"]:
    mid = m["id"]
    scene_folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    hit_path = f"{scene_folder}/MAP_HIT_NEW.swf"
    hit_hash = hashlib.md5(hit_path.encode("utf-8")).hexdigest()
    res_p = os.path.join(RES_DIR, hit_hash)
    if not os.path.exists(res_p):
        print(f"PULANDO Map {mid}: SWF não encontrado em res")
        continue
        
    with open(res_p, "rb") as f:
        hdata = f.read()
    decomp = zlib.decompress(hdata[8:]) if hdata[:3] == b"CWS" else hdata[8:]
    full = b"FWS\t" + hdata[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    tag72 = None
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
            tag72 = tag_data
            break
        pos += t_len
        
    if not tag72:
        print(f"PULANDO Map {mid}: Tag 72 não encontrada")
        continue
        
    cw, ch = extract_col_dimensions_from_abc(tag72)
    if not (cw and ch and cw > 0 and ch > 0):
        print(f"ERRO Map {mid}: Dimensões inválidas ({cw}, {ch})")
        continue
        
    # Update catalog entry
    old_cw = m.get("col_width")
    old_ch = m.get("col_height")
    m["col_width"] = cw
    m["col_height"] = ch
    
    # Update individual map meta.json
    meta_p = os.path.join(MAPS_DIR, f"map_{mid}", "meta.json")
    if os.path.exists(meta_p):
        with open(meta_p, "r", encoding="utf-8") as f:
            ind_meta = json.load(f)
        ind_meta["col_width"] = cw
        ind_meta["col_height"] = ch
        with open(meta_p, "w", encoding="utf-8") as f:
            json.dump(ind_meta, f, indent=2, ensure_ascii=False)
            
    updated_count += 1
    if old_cw != cw or old_ch != ch:
        print(f"Map {mid:3d} ({m['name']}): col ({old_cw}x{old_ch}) -> ({cw}x{ch})")

# Save updated catalog
with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(cat, f, indent=2, ensure_ascii=False)

print(f"\nSucesso total: {updated_count} / {len(cat['maps'])} mapas atualizados com col_width e col_height exatos do AVM2!")
