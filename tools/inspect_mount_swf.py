import os, sys, hashlib, zlib, struct

res_dir = r"mcgame/frontend/s/res"

def inspect_swf_by_rel(rel):
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    path = os.path.join(res_dir, h)
    if not os.path.exists(path):
        print(f"File not found: {rel} ({h})")
        return
    with open(path, "rb") as f:
        data = f.read()
    sig = data[:3]
    print(f"=== {rel} ===")
    print(f"  Length: {len(data)}, Sig: {sig}")
    if sig == b'CWS':
        decompressed = data[:8] + zlib.decompress(data[8:])
    else:
        decompressed = data
    print(f"  Decompressed length: {len(decompressed)}")
    # Scan for tags
    pos = 8
    nbits = decompressed[pos] >> 3
    nbytes = (5 + 4 * nbits + 7) // 8
    pos += nbytes + 4
    tag_counts = {}
    while pos < len(decompressed):
        tag_header = struct.unpack('<H', decompressed[pos:pos+2])[0]
        pos += 2
        tag_type = tag_header >> 6
        tag_len = tag_header & 0x3F
        if tag_len == 0x3F:
            tag_len = struct.unpack('<I', decompressed[pos:pos+4])[0]
            pos += 4
        tag_counts[tag_type] = tag_counts.get(tag_type, 0) + 1
        pos += tag_len
    print(f"  Tag counts: {tag_counts}")

inspect_swf_by_rel("creature/PC_MALE_100001.swf")
inspect_swf_by_rel("creature/PC_FEMALE_010010.swf")
