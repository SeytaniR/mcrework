import json, sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

with open("web/assets/maps/catalog.json", "r", encoding="utf-8") as f:
    cat = json.load(f)

print("Continents:")
for c in cat["continents"]:
    print(f"  {c['id']}: {c['name']} -> {c['maps_count']} maps")

pinned1 = [m for m in cat["maps"] if m["continent"] == 1 and m["world_x"] is not None]
pinned2 = [m for m in cat["maps"] if m["continent"] == 2 and m["world_x"] is not None]
print(f"Pinned on Cont 1: {len(pinned1)}")
print(f"Pinned on Cont 2: {len(pinned2)}")
for m in pinned1[:10]:
    print(f"  Cont 1: {m['name']} at ({m['world_x']}, {m['world_y']})")
for m in pinned2[:10]:
    print(f"  Cont 2: {m['name']} at ({m['world_x']}, {m['world_y']})")
