import os, re

pattern = re.compile(r'gotoAnd(Play|Stop)\(', re.IGNORECASE)
found = []
for dp, _, fns in os.walk(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client"):
    for f in fns:
        if any(k in f for k in ["Creature", "Char", "Role", "Avatar", "Sprite", "Actor", "Animate"]):
            p = os.path.join(dp, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                for i, l in enumerate(fp):
                    if pattern.search(l):
                        found.append((f, i+1, l.strip()))

for f, l, text in found[:20]:
    print(f"{f}:{l} -> {text}")
