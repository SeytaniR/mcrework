with open("char_main_abc.bin", "rb") as f:
    abc = f.read()

# Let's search for the bytes around 'midX' string index
# In ABC:
# Find string table
p = 4
def read_u30(buf, offset):
    res = 0; shift = 0
    while True:
        b = buf[offset]; offset += 1
        res |= (b & 0x7F) << shift
        if not (b & 0x80): break
        shift += 7
    return res, offset

# The ABC in Tag 82 starts with:
# flags (u30) + name (string)
# Let's inspect the first 20 bytes of char_main_abc.bin:
print("First 20 bytes:", abc[:20].hex(' '))
