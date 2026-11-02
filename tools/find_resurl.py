import os

for root, dirs, files in os.walk("mcgame"):
    for f in files:
        if f.endswith('.as'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    c = fp.read()
                    if 'getResUrlNoHash' in c:
                        print(f"Match in {path}")
            except Exception:
                pass
