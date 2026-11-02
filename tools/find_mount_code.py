import os, sys, re

mc_dir = r"mcgame"
found = []
for root, dirs, files in os.walk(mc_dir):
    for f in files:
        if f.endswith(('.as', '.txt', '.xml', '.json', '.sql')):
            # search for mount url patterns
            full = os.path.join(root, f)
            try:
                with open(full, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    if 'getMount' in content or 'mount/' in content or 'MOUNT_' in content or 'mount_dress' in content or '20500800' in content:
                        found.append(full)
            except Exception:
                pass

print(f"Found {len(found)} relevant files:")
for f in found[:20]:
    print(" ", f)
