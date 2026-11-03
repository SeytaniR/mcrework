import json, sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

with open("tools/visual_maps_catalog.json", "r", encoding="utf-8") as f:
    maps = {m["id"]: m for m in json.load(f)["maps"]}

for mid in [1, 2, 3, 5, 6, 7, 8, 9, 10]:
    if mid in maps:
        m = maps[mid]
        print(f"Map {mid} [{m['name']}]: {len(m['portals'])} portals:")
        for p in m["portals"]:
            print(f"  -> ({p['x']}, {p['y']}) leads to '{p['target_name']}' (Map {p['target_map_id']})")
