with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client\view\view\compGameStage\CreatureView.as", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if ".dir =" in l or "_dir =" in l or "dir:" in l:
        print(f"{i+1}: {l.strip()}")
