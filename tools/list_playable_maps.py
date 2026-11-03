import os, json, sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

with open("tools/maps_analysis.json", "r", encoding="utf-8") as f:
    data = json.load(f)

playable = []
for mid, m in sorted(data["maps"].items(), key=lambda x: int(x[0])):
    if m["tile_count"] > 0 or m["has_mini"]:
        playable.append((int(mid), m))

print(f"Total Playable / Visual Maps: {len(playable)}")
for mid, m in playable:
    p_names = [p["target_name"] for p in m["portals"]]
    icon_info = f"WorldMap (Cont {m['world_icon']['continent']}: {m['world_icon']['world_x']},{m['world_icon']['world_y']})" if m["world_icon"] else "Submap/Dungeon"
    print(f"Map {mid:3d} [{m['name']:<20}] Size: {m['width']}x{m['height']} | Tiles: {m['tile_count']:2d} | Mini: {m['has_mini']} | Hit: {m['has_hit']} | Portais: {len(m['portals'])} -> {p_names[:3]} | {icon_info}")
