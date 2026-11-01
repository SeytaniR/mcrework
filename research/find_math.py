import os

for dp, _, fns in os.walk(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client"):
    for f in fns:
        if "Math" in f or "Dir" in f:
            print(os.path.join(dp, f))
