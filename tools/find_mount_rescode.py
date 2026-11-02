import os

for root, dirs, files in os.walk("mcgame"):
    for f in files:
        if f.endswith('.as'):
            p = os.path.join(root, f)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                    c = fp.read()
                    if "mountResCode" in c:
                        print(f"Found in {p}")
            except Exception:
                pass
