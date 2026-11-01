import struct

with open("char_main_abc.bin", "rb") as f:
    abc = f.read()

# Let's search for setproperty or initproperty opcodes (0x61, 0x68)
# In AVM2:
# find where 'midX', 'footY', 'headY', 'bodyHeight' are assigned
for prop in [b"midX", b"footY", b"headY", b"bodyHeight", b"totalWidth", b"totalHeight"]:
    idx = 0
    while True:
        pos = abc.find(prop, idx)
        if pos == -1: break
        print(f"Prop {prop.decode()} at string offset {pos}")
        idx = pos + 1

# Let's search for pushint/pushshort/pushbyte/pushdouble before setproperty
# Or let's decompile the constructor method
# In GameRes or PC_MALE class constructor:
