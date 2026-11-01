import zlib, struct

def get_labels(swf_hash):
    path = f"C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/mcgame/frontend/s/res/{swf_hash}"
    with open(path, "rb") as f:
        data = f.read()

    full = data[:8] + zlib.decompress(data[8:])
    pos = 8
    nbits = full[pos] >> 3
    pos += (5 + nbits * 4 + 7) // 8 + 4

    labels = []
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
            name = tag_data[:null_idx].decode("ascii", errors="replace")
            labels.append(name)
        pos += t_len

    return labels

lbls_11 = get_labels("05a8cd74b99040be44e03b52f6ff1adb")
print("Total labels in PC_MALE_000011:", len(lbls_11))
# Print action IDs present in PC_MALE_000011 for Dir 0:
dir0 = [l for l in lbls_11 if l.startswith("0-")]
print("Dir 0 labels in PC_MALE_000011:", dir0)
