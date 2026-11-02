with open(r"mcgame\docs\client\predef\GamePredef.as", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

import re
matches = re.findall(r'(?:public|private|static|const|var|function)[^\n;{}]*mount[^\n;{}]*', text, re.I)
for m in matches[:30]:
    print(m.strip())
