with open(r"mcgame\docs\client\object\Creature.as", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'mount', text, re.I)]
for m in matches[:10]:
    start = max(0, m - 100)
    end = min(len(text), m + 200)
    print("--- MATCH ---")
    print(text[start:end])
