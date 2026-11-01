import zlib, struct, os

path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\b68e68f7e6ed33ca378b507e60664d2b"
with open(path, "rb") as f:
    data = f.read()

sig = data[:3]
ver = data[3]
length = struct.unpack("<I", data[4:8])[0]
print(f"PC_MALE_000001.swf: Sig={sig}, Ver={ver}, Len={length}")
decomp = zlib.decompress(data[8:]) if sig == b"CWS" else data[8:]
full = b"FWS" + bytes([ver]) + struct.pack("<I", length) + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

tags = []
while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    tags.append((t_type, t_len, pos))
    pos += t_len

tag_counts = {}
for t, l, p in tags:
    tag_counts[t] = tag_counts.get(t, 0) + 1
print("Tag counts:", tag_counts)
# Tag 36: DefineBitsLossless2
# Tag 39: DefineSprite
# Tag 76: SymbolClass
# Tag 82: DoABC
# Tag 20/21/35: DefineBits/DefineBitsJPEG
