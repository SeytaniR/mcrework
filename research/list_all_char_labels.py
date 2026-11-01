import zlib, struct

path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
with open(path, "rb") as f:
    data = f.read()

full = data[:8] + zlib.decompress(data[8:])

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

labels_timeline = []
frame_num = 1

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
        name = tag_data[:null_idx].decode("utf-8", errors="ignore")
        labels_timeline.append((frame_num, name))
    elif t_type == 1: # ShowFrame
        frame_num += 1

    pos += t_len

print(f"Total frame labels found: {len(labels_timeline)}, total frames in SWF: {frame_num}")
for i, (f_start, name) in enumerate(labels_timeline):
    f_end = labels_timeline[i+1][0] - 1 if i+1 < len(labels_timeline) else frame_num
    frame_count = f_end - f_start + 1
    print(f"  Frame {f_start:3d}..{f_end:3d} ({frame_count:2d} frames): label = '{name}'")
