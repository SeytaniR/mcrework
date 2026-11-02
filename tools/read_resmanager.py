import os, sys

for root, dirs, files in os.walk("mcgame"):
    for f in files:
        if f == "ResManager.as":
            path = os.path.join(root, f)
            print("Found ResManager at:", path)
            with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                lines = fp.readlines()
                for i, l in enumerate(lines):
                    if "getResUrl" in l or "getResUrlNoHash" in l:
                        print(f"Line {i+1}: {l.strip()}")
                        for j in range(i, min(i+40, len(lines))):
                            print(f"  {lines[j].rstrip()}")
                        break
