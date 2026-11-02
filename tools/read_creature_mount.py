import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r"mcgame\docs\client\object\Creature.as", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "mountResCode" in l or "mountDress" in l or "mountState" in l:
        print(f"Line {i}: {l.strip()}")
        for j in range(max(0, i-2), min(i+10, len(lines))):
            print(f"  {lines[j].rstrip()}")
        print("---")
