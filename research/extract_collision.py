import struct, zlib

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\4081417bc8ccedcb4dadcdacc73615f4", "rb") as f:
    full = f.read()

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    if t_type == 87: # DefineBinaryData
        tag_data = full[pos:pos+t_len]
        tag_id = int.from_bytes(tag_data[:2], "little")
        reserved = int.from_bytes(tag_data[2:6], "little")
        binary_payload = tag_data[6:]
        print(f"DefineBinaryData tag id: {tag_id}, payload len: {len(binary_payload)}")
        with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\map1_collision.bin", "wb") as out:
            out.write(binary_payload)
        print("Saved map1_collision.bin!")
        print("Payload prefix (hex):", binary_payload[:32].hex(" "))
    pos += t_len
