import struct, zlib, os

swf_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
with open(swf_path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
full = b"FWS\t" + data[4:8] + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

# Parse tags
# We want to trace:
# FrameLabels -> frame number -> PlaceObject2 -> shape_id -> matrix (translate x, y in twips / 20)
frame_idx = 1
current_label = ""
frame_placements = [] # (frame_idx, label, char_id, matrix_tx, matrix_ty)

while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4

    tag_data = full[pos:pos+t_len]

    if t_type == 43: # FrameLabel
        null_idx = tag_data.find(b"\x00")
        current_label = tag_data[:null_idx].decode("utf-8", errors="ignore")
    elif t_type == 1: # ShowFrame
        frame_idx += 1
    elif t_type == 26: # PlaceObject2
        flags = tag_data[0]
        depth = int.from_bytes(tag_data[1:3], "little")
        tpos = 3
        char_id = None
        if flags & 0x02: # HasCharacter
            char_id = int.from_bytes(tag_data[tpos:tpos+2], "little")
            tpos += 2
        tx, ty = 0, 0
        if flags & 0x04: # HasMatrix
            # Parse MATRIX record
            # Bit 0: HasScale
            # Scale info...
            # Bit: HasRotate...
            # Translate info: NTranslateBits (5 bits), TranslateX (N bits), TranslateY (N bits)
            b_stream = ""
            for b in tag_data[tpos:]:
                b_stream += f"{b:08b}"
            
            b_idx = 0
            has_scale = int(b_stream[b_idx])
            b_idx += 1
            if has_scale:
                n_scale_bits = int(b_stream[b_idx:b_idx+5], 2)
                b_idx += 5 + n_scale_bits * 2
            has_rotate = int(b_stream[b_idx])
            b_idx += 1
            if has_rotate:
                n_rotate_bits = int(b_stream[b_idx:b_idx+5], 2)
                b_idx += 5 + n_rotate_bits * 2
            
            n_trans_bits = int(b_stream[b_idx:b_idx+5], 2)
            b_idx += 5
            if n_trans_bits > 0:
                raw_tx = int(b_stream[b_idx:b_idx+n_trans_bits], 2)
                if raw_tx & (1 << (n_trans_bits - 1)): raw_tx -= (1 << n_trans_bits)
                b_idx += n_trans_bits
                raw_ty = int(b_stream[b_idx:b_idx+n_trans_bits], 2)
                if raw_ty & (1 << (n_trans_bits - 1)): raw_ty -= (1 << n_trans_bits)
                tx, ty = raw_tx / 20.0, raw_ty / 20.0

        if char_id is not None or flags & 0x04:
            frame_placements.append((frame_idx, current_label, char_id, tx, ty))

    pos += t_len

print(f"Total placements: {len(frame_placements)}")
for fp in frame_placements[:25]:
    print(f"Frame {fp[0]} (label '{fp[1]}'): char_id={fp[2]}, offset=({fp[3]}, {fp[4]})")
