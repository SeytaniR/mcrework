import struct, zlib

path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
with open(path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
full = b"FWS\t" + data[4:8] + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

frame_idx = 1
labels = []

while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    if t_type == 1: # ShowFrame
        frame_idx += 1
    elif t_type == 43: # FrameLabel
        null_idx = full.find(b"\x00", pos)
        label = full[pos:null_idx].decode("utf-8", errors="ignore")
        labels.append((frame_idx, label))
    pos += t_len

print(f"Total frame labels found: {len(labels)}")
for f_idx, lbl in labels:
    print(f"Frame {f_idx}: '{lbl}'")
