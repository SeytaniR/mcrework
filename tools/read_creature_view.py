import os, sys, re

path = r"mcgame\docs\client\view\view\compGameStage\CreatureView.as"
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    for m in re.finditer(r'([^\n]*mount[^\n]*)', text, re.IGNORECASE):
        print(m.group(1).strip())
