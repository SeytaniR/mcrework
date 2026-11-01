with open("char_main_abc.bin", "rb") as f:
    abc = f.read()

# Let's find the multiname index for midX, footY, headY
# String midX is at 231
# Let's inspect bytes in method bodies
# pushbyte is 0x24 <byte>
# pushshort is 0x25 <u30>
# find all occurrences of 'midX' multiname
# Let's print all pushbyte/pushshort instructions in the file that set properties
import re
# Look for pattern: pushbyte/pushshort followed by initproperty/setproperty
# Let's find the string table to know string IDs
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
str_map = {}
for i in range(1, cnt):
    l, p = read_u30(abc, p)
    s = abc[p:p+l].decode('utf-8', 'ignore')
    str_map[i] = s
    p += l

target_strings = {"midX", "footY", "headY", "bodyHeight", "totalWidth", "totalHeight", "bodyX", "bodyY", "bodyWidth"}
target_ids = {k: v for k, v in str_map.items() if v in target_strings}
print("Target string IDs:", target_ids)

# Find multinames referencing these strings
cnt, p = read_u30(abc, p) # namespaces
# skip namespaces
# Let's just search for the strings in any method body:
# In AVM2, initproperty (0x68) or setproperty (0x61) takes a multiname index.
# Let's find where GameRes constructor is:
# Search for string "GameRes"
gameres_id = [k for k, v in str_map.items() if v == "GameRes"]
print("GameRes string ID:", gameres_id)
