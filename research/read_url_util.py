with open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client\utils\UrlUtil.as', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's inspect the getResUrl logic
for line in text.split('\n'):
    if any(k in line for k in ['function', 'return', 'resource', 'folder', 'ext', 'code']):
        print(line.strip()[:100])
