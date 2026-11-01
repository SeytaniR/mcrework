import zlib, struct

def inspect_swf_labels(swf_hash, label_prefix=""):
    path = f"C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/mcgame/frontend/s/res/{swf_hash}"
    with open(path, "rb") as f:
        data = f.read()

    full = data[:8] + zlib.decompress(data[8:])
    pos = 8
    nbits = full[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4

    labels = []
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
        if t_type == 43:
            null_idx = tag_data.find(b"\x00")
            name = tag_data[:null_idx].decode("utf-8", errors="ignore")
            labels.append(name)
        pos += t_len

    print(f"[{label_prefix}] Total labels: {len(labels)}, unique: {len(set(labels))}")
    print(f"   Labels: {sorted(list(set(labels)))}")

# Inspect PC_MALE_100001 (Montaria?)
inspect_swf_labels("64a4277d38b4c4f762a45dfdec017e38", "PC_MALE_100001")
# Inspect PC_MALE_000011 (Evolução / Armadura?)
inspect_swf_labels("05a8cd74b99040be44e03b52f6ff1adb", "PC_MALE_000011")
