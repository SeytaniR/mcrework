import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

# Let's read masks.json of Map 9!
with open('web/assets/maps/map_9/masks.json', 'r', encoding='utf-8') as f:
    m9 = json.load(f)

print(f"Map 9 masks count: {len(m9)}")
for item in m9:
    print(item)
