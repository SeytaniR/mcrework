import zlib, struct

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\map1_collision.bin", "rb") as f:
    decomp = zlib.decompress(f.read())

total_bytes = len(decomp)
total_bits = total_bytes * 8
print(f"Collision total bytes: {total_bytes}, total bits: {total_bits}")

# Let's test potential dimensions (w, h)
# Map 1 image is 2000x1500 = 3,000,000 bits (375,000 bytes)
# Total bytes is 388,683!
# Notice: 388,683 - 375,000 = 13,683 bytes
# Let's check if the first few bytes are width and height, or if width is larger than 2000!
# Or let's check ClassBytes in the SWF:
# In MAP_HIT_NEW.swf, ClassBytes extends ByteArray and sets width and height in its constructor!
