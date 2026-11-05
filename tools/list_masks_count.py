import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

for m in cat['maps']:
    if m.get('has_masks'):
        print(f"Map {m['id']:2d} ({m['name']}): count={m.get('masks_count')}")
