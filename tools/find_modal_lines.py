import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('web/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="modal-' in l:
        print(f"{i+1}: {l.strip()[:100]}")
