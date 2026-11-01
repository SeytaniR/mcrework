import struct, zlib

swf_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
with open(swf_path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
full = b"FWS\t" + data[4:8] + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

shapes = {}

while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4

    tag_data = full[pos:pos+t_len]

    if t_type == 2: # DefineShape
        shape_id = int.from_bytes(tag_data[:2], "little")
        b_stream = "".join(f"{b:08b}" for b in tag_data[2:15])
        n_bits = int(b_stream[:5], 2)
        idx = 5
        vals = []
        for _ in range(4):
            v = int(b_stream[idx:idx+n_bits], 2)
            if v & (1 << (n_bits - 1)): v -= (1 << n_bits)
            idx += n_bits
            vals.append(v / 20.0)
        shapes[shape_id] = tuple(vals)

    pos += t_len

print("Parsed shapes:", len(shapes))
for s_id in sorted(shapes.keys())[:10]:
    b = shapes[s_id]
    w = b[1] - b[0]
    h = b[3] - b[2]
    print(f"Shape {s_id}: bounds=({b[0]}, {b[2]}) to ({b[1]}, {b[3]}), size={w}x{h}, pivot_offset=({-b[0]}, {-b[2]})")
