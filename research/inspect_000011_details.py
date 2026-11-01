import zlib

path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\05a8cd74b99040be44e03b52f6ff1adb"
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
        try:
            name = tag_data[:null_idx].decode("gbk")
        except:
            name = tag_data[:null_idx].decode("utf-8", errors="ignore")
        labels.append(name)
    pos += t_len

# Group by direction
actions_per_dir = {}
for l in labels:
    if "-" in l:
        parts = l.split("-")
        actions_per_dir.setdefault(parts[0], []).append(parts[1])

for d, acts in sorted(actions_per_dir.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 99):
    print(f"Dir {d}: {acts}")

# Check any other non standard labels
for l in labels:
    if "-" not in l:
        print("Other label:", [c for c in l], "escaped:", l.encode('unicode_escape').decode())
