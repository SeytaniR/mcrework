import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

for m in cat['maps']:
    if m['id'] in [1, 2, 3, 4, 9, 22]:
        print(f"Cat Map {m['id']}: name={m['name']}, w={m['width']}, h={m['height']}, col_w={m['col_width']}, col_h={m['col_height']}")
