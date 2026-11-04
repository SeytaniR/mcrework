import os, glob

matches = []
for root, dirs, files in os.walk('mcgame'):
    for f in files:
        if f.endswith('.as'):
            path = os.path.join(root, f)
            name_lower = f.lower()
            if 'skill' in name_lower or 'effect' in name_lower:
                matches.append(path)

print(f'Found {len(matches)} files matching skill or effect:')
for m in matches[:30]:
    print(' ', m)
