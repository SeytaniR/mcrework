import json, os, sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

for mid in [1, 2, 3, 4, 9]:
    m = next(m for m in cat['maps'] if m['id'] == mid)
    col_p = os.path.join('web', m.get('collision_bin', ''))
    with open(col_p, 'rb') as f_col:
        col_bytes = f_col.read()
    cw, ch = m['col_width'], m['col_height']
    bw, bh = m['width'], m['height']
    
    def is_walk(x, y):
        if x < 0 or x >= bw or y < 0 or y >= bh: return False
        if x >= cw or y >= ch: return False
        idx = y * cw + x
        b_idx = idx >> 3
        if b_idx >= len(col_bytes): return False
        return (col_bytes[b_idx] & (1 << (idx & 7))) != 0
        
    sx, sy = m.get('safe_x', 0), m.get('safe_y', 0)
    print(f"Map {mid} ({m['name']}): Safe pos ({sx}, {sy}) is_walkable={is_walk(sx, sy)}")
    
    for p in m.get('portals', []):
        px, py = p['x'], p['y']
        print(f"  Portal {p.get('target_name')} at ({px}, {py}) is_walkable={is_walk(px, py)}")
