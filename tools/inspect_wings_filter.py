import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_JS = os.path.join(BASE_DIR, "web", "main.js")

with open(MAIN_JS, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'selectedEquipmentFilter === "wings"' in l:
        print(f"Line {i+1}:")
        for j in range(max(0, i-5), min(len(lines), i+20)):
            print(f"  {j+1}: {lines[j]}", end="")
        break
