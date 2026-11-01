with open("char_main_abc.bin", "rb") as f:
    raw = f.read()

abc = raw[5:]
p = 4
def read_u30(buf, offset):
    res = 0; shift = 0
    while True:
        b = buf[offset]; offset += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return res, offset

cnt, p = read_u30(abc, p); [read_u30(abc, p) for _ in range(1, cnt)]
cnt, p = read_u30(abc, p); [read_u30(abc, p) for _ in range(1, cnt)]
cnt, p = read_u30(abc, p)
if cnt > 0: p += (cnt - 1) * 8

cnt, p = read_u30(abc, p)
print("Total strings:", cnt)
for i in range(1, min(cnt, 50)):
    l, p = read_u30(abc, p)
    s = abc[p:p+l].decode('utf-8', 'ignore')
    print(f"{i}: {s}")
    p += l
