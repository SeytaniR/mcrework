with open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client\utils\UrlUtil.as', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

idx = text.find('function getUrl')
print(text[idx:idx+1500])
