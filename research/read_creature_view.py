with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client\view\view\compGameStage\CreatureView.as", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ["direction", "Direction", "action", "Action", "gotoAnd", "play", "stand"]):
        if any(w in l for w in ["function", "var ", "_dir", "set", "play", "="]):
            print(f"{i+1}: {l.strip()}")
