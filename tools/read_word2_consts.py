import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r"mcgame\docs\client\predef\GamePredef.as", 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = re.findall(r'public static var RES_URL_WORD2_[a-zA-Z0-9_]+:uint\s*=\s*[0-9]+;', text)
for m in matches:
    print(m)
