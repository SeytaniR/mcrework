with open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\sv\MainClient_decrypted.swf', 'rb') as f:
    data = f.read()

# Let's search for the method body or cinit of AbstractGameRes
# String 'AbstractGameRes' occurs at pos 12134949
# Let's search for references to string index of 'BH_ATTACK'
# In ABC at 11846154:
abc = data[11846154:]
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

str_indices = {}
target_names = {
    b'BH_BREATH_SLOW', b'BH_BREATH_FAST', b'BH_RUN_NORMAL', b'BH_RUN_FAST',
    b'BH_ATTACK', b'BH_MAGIC', b'BH_HURT', b'BH_DEAD', b'BH_DEFENCE',
    b'BH_RUSH', b'BH_SIT', b'BH_DIE', b'BH_BACK', b'BH_TURNBACK'
}

for i in range(1, cnt):
    l, p = read_u30(abc, p)
    s = abc[p:p+l]
    if s in target_names:
        str_indices[s.decode()] = i
    p += l

print('String indices:', str_indices)
