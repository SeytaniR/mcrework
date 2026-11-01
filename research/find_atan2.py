import os, re

pattern = re.compile(r'atan2', re.IGNORECASE)
found = []
for dp, _, fns in os.walk(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client"):
    for f in fns:
        if f.endswith(".as"):
            p = os.path.join(dp, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                for i, l in enumerate(fp):
                    if pattern.search(l):
                        found.append((f, i+1, l.strip()))

for f, l, text in found:
    print(f"{f}:{l} -> {text}")
