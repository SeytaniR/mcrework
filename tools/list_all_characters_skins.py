import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open('web/assets/characters/catalog.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total character visual models in catalog: {len(data['classes'])}")
for idx, c in enumerate(data['classes'], 1):
    print(f"  [{idx:02d}] {c['id']} - {c['name']} (gender: {c.get('gender')}, frames: {c.get('total_frames')})")
