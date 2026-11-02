import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r"mcgame\docs\client\predef\GamePredef.as", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "RES_URL" in l:
        print(f"Line {i}: {l.strip()}")
        for j in range(i, min(i+25, len(lines))):
            print(f"  {lines[j].rstrip()}")
        break
