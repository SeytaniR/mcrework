with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\4081417bc8ccedcb4dadcdacc73615f4", "rb") as f:
    data = f.read()

# Let's search for strings in MAP_HIT_NEW.swf
import re
strings = re.findall(b'[\x20-\x7e]{3,}', data)
for s in strings:
    print(s.decode('ascii', errors='ignore'))
