import os, zlib, hashlib, struct

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")

mask_h = hashlib.md5("resource/scene/SCENE_FOLDER_000001/MAP_MASK.swf".encode("utf-8")).hexdigest()
path = os.path.join(RES_DIR, mask_h)

with open(path, "rb") as f:
    data = f.read()

print(f"Header: {data[:3]}, len: {len(data)}")
decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
full = b"FWS\t" + data[4:8] + decomp

# parse RECT
first_byte = full[8]
nbits = first_byte >> 3
rect_bytes = (5 + nbits * 4 + 7) // 8
pos = 8 + rect_bytes + 4

tag_counts = {}
while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    tag_counts[t_type] = tag_counts.get(t_type, 0) + 1
    pos += t_len

print("Tags in MAP_MASK.swf:", tag_counts)
