import zlib, struct, os

def inspect_swf(name, file_hash):
    res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
    path = os.path.join(res_dir, file_hash)
    with open(path, "rb") as f:
        data = f.read()
    sig = data[:3]
    ver = data[3]
    length = struct.unpack("<I", data[4:8])[0]
    print(f"--- {name} ({file_hash}) ---")
    print(f"Sig: {sig}, Ver: {ver}, Uncompressed Len: {length}")
    if sig == b"CWS":
        decomp = zlib.decompress(data[8:])
        full = b"FWS" + bytes([ver]) + struct.pack("<I", length) + decomp
    else:
        full = data

    pos = 8
    nbits = full[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4

    tags = []
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4
        tags.append((t_type, t_len, pos))
        pos += t_len

    tag_types = {}
    for t, l, p in tags:
        tag_types[t] = tag_types.get(t, 0) + 1
    print(f"Total tags: {len(tags)}, Tag types: {tag_types}")

inspect_swf("MAP_MASK.swf", "c3f43ddd342956b8d22490808a5cc3c7")
inspect_swf("MAP_HIT_NEW.swf", "4081417bc8ccedcb4dadcdacc73615f4")
