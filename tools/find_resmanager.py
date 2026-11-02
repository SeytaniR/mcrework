import os

for root, dirs, fnames in os.walk(r"mcgame\docs\client"):
    for f in fnames:
        if f.endswith('.as'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                txt = fp.read()
            if 'getResUrlNoHash' in txt:
                print("Found getResUrlNoHash in:", p)
                for line in txt.split('\n'):
                    if 'getResUrlNoHash' in line:
                        print(" ", line.strip())
