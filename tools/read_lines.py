import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r"mcgame\docs\client\predef\GamePredef.as", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i in range(8220, 8251):
    print(f"{i}: {lines[i].rstrip()}")
