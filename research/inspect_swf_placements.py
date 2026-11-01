import zlib, struct

path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
with open(path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
full = b"FWS\t" + data[4:8] + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

def parse_matrix(data_bytes):
    b_stream = "".join(f"{b:08b}" for b in data_bytes)
    idx = 0
    has_scale = int(b_stream[idx]); idx += 1
    sx, sy = 1.0, 1.0
    if has_scale:
        nb = int(b_stream[idx:idx+5], 2); idx += 5
        raw_sx = int(b_stream[idx:idx+nb], 2); idx += nb
        raw_sy = int(b_stream[idx:idx+nb], 2); idx += nb
        sx = raw_sx / 65536.0
        sy = raw_sy / 65536.0
    has_rot = int(b_stream[idx]); idx += 1
    if has_rot:
        nb = int(b_stream[idx:idx+5], 2); idx += 5
        idx += nb * 2
    nb_trans = int(b_stream[idx:idx+5], 2); idx += 5
    tx, ty = 0, 0
    if nb_trans > 0:
        raw_tx = int(b_stream[idx:idx+nb_trans], 2); idx += nb_trans
        if raw_tx & (1 << (nb_trans - 1)): raw_tx -= (1 << nb_trans)
        raw_ty = int(b_stream[idx:idx+nb_trans], 2); idx += nb_trans
        if raw_ty & (1 << (nb_trans - 1)): raw_ty -= (1 << nb_trans)
        tx = raw_tx / 20.0
        ty = raw_ty / 20.0
    return sx, sy, tx, ty

count = 0
while pos < len(full) and count < 30:
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4

    tag_data = full[pos:pos+t_len]
    if t_type == 26: # PlaceObject2
        flags = tag_data[0]
        depth = int.from_bytes(tag_data[1:3], "little")
        offset = 3
        cid = None
        if flags & 0x02:
            cid = int.from_bytes(tag_data[offset:offset+2], "little")
            offset += 2
        matrix = None
        if flags & 0x04:
            matrix = parse_matrix(tag_data[offset:offset+16])
        print(f"PlaceObject2 #{count}: flags=0x{flags:02x}, depth={depth}, cid={cid}, matrix={matrix}")
        count += 1
    elif t_type == 2: # DefineShape
        sid = int.from_bytes(tag_data[:2], "little")
        # Let's inspect shape fill matrix
        # Find 0x40/0x41/0x42
        for i in range(len(tag_data) - 10):
            if tag_data[i] in (0x40, 0x41, 0x42, 0x43):
                bmp_id = int.from_bytes(tag_data[i+1:i+3], "little")
                m = parse_matrix(tag_data[i+3:i+19])
                print(f"Shape {sid}: bitmap={bmp_id}, fill matrix={m}")
                break

    pos += t_len
