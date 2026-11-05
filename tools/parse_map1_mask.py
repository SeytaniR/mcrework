import os, zlib, hashlib, struct

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")

mask_h = hashlib.md5("resource/scene/SCENE_FOLDER_000001/MAP_MASK.swf".encode("utf-8")).hexdigest()
path = os.path.join(RES_DIR, mask_h)

with open(path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
full = b"FWS\t" + data[4:8] + decomp

first_byte = full[8]
nbits = first_byte >> 3
rect_bytes = (5 + nbits * 4 + 7) // 8
pos = 8 + rect_bytes + 4

tags = []
while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    tag_data = full[pos:pos+t_len]
    tags.append((t_type, tag_data))
    pos += t_len

print("Parsed tags:")
for t_type, t_data in tags:
    if t_type == 35:
        cid = int.from_bytes(t_data[:2], "little")
        print(f"Tag 35 (DefineBitsJPEG3): characterId={cid}, len={len(t_data)}")
    elif t_type in (2, 22, 32, 83):
        cid = int.from_bytes(t_data[:2], "little")
        print(f"Shape tag {t_type}: characterId={cid}, len={len(t_data)}")
    elif t_type in (4, 26, 70):
        print(f"PlaceObject tag {t_type}: len={len(t_data)}")
    elif t_type == 39:
        cid = int.from_bytes(t_data[:2], "little")
        frame_cnt = int.from_bytes(t_data[2:4], "little")
        print(f"DefineSprite (Tag 39): characterId={cid}, frameCount={frame_cnt}, len={len(t_data)}")
