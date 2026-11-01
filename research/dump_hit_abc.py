with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\4081417bc8ccedcb4dadcdacc73615f4", "rb") as f:
    full = f.read()

# Let's search for pushint or pushshort or pushbyte before 'width' or 'height'
# In ABC bytecode:
# find all occurrences of 25 (pushshort) or 24 (pushbyte) or 2d (pushint)
# In Tag 72 (DoABC):
pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    if t_type == 72: # DoABC
        abc = full[pos:pos+t_len]
        print(f"DoABC length: {len(abc)}")
        # Let's inspect the entire ABC bytes in hex
        for i in range(0, len(abc), 32):
            chunk = abc[i:i+32]
            ascii_chunk = "".join(chr(c) if 32 <= c <= 126 else "." for c in chunk)
            print(f"{i:04x}: {chunk.hex(' ')}  |  {ascii_chunk}")
    pos += t_len
