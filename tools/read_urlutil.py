import os, sys

with open(r"mcgame\docs\client\utils\UrlUtil.as", 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "getResUrl" in l:
        print(f"Line {i}: {l.strip()}")
        for j in range(i, min(i+60, len(lines))):
            print(f"  {lines[j].rstrip()}")
        break
