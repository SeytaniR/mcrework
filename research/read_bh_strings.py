with open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\sv\MainClient_decrypted.swf', 'rb') as f:
    data = f.read()

idx = 12902765
chunk = data[idx-200:idx+300]
print("Strings chunk:")
# Print all null-terminated or length-prefixed strings
p = 0
while p < len(chunk):
    l = chunk[p]
    if 1 <= l <= 40 and p + 1 + l <= len(chunk):
        try:
            s = chunk[p+1:p+1+l].decode('utf-8')
            if any(c.isalnum() for c in s):
                print(f"  {s}")
                p += 1 + l
                continue
        except:
            pass
    p += 1
