with open("char_main_abc.bin", "rb") as f:
    raw = f.read()

# ABC starts at index 5!
abc = raw[5:]
print("ABC magic:", abc[:4].hex(' '))

p = 4
def read_u30(buf, offset):
    res = 0; shift = 0
    while True:
        b = buf[offset]; offset += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return res, offset

cnt, p = read_u30(abc, p)
ints = [0] + [read_u30(abc, p)[0] for _ in range(1, cnt)]
cnt, p = read_u30(abc, p)
uints = [0] + [read_u30(abc, p)[0] for _ in range(1, cnt)]
cnt, p = read_u30(abc, p)
import struct
doubles = [0.0]
for _ in range(1, cnt):
    doubles.append(struct.unpack('<d', abc[p:p+8])[0])
    p += 8

cnt, p = read_u30(abc, p)
str_map = {}
for i in range(1, cnt):
    l, p = read_u30(abc, p)
    s = abc[p:p+l].decode('utf-8', 'ignore')
    str_map[i] = s
    p += l

print("Ints:", ints)
print("Doubles:", doubles)
target_strings = {"midX", "footY", "headY", "bodyHeight", "totalWidth", "totalHeight", "bodyX", "bodyY", "bodyWidth"}
target_ids = {k: v for k, v in str_map.items() if v in target_strings}
print("Target string IDs:", target_ids)
