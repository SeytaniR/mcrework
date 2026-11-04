import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_JS_PATH = os.path.join(BASE_DIR, "web", "main.js")

with open(MAIN_JS_PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'selectedSkillFilter === "vfx"' in l:
        print(f"Found at line {i+1}")
        for j in range(i, min(len(lines), i+35)):
            print(f"{j+1}: {lines[j]}", end="")
        break
