with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\4081417bc8ccedcb4dadcdacc73615f4", "rb") as f:
    data = f.read()

# Let's find where 'width' and 'height' are initialized in the ABC bytecode
pos = data.find(b'width')
print("pos of width:", pos)
# Let's inspect bytes around 'width'
print("Context around width:", data[pos-50:pos+100])
