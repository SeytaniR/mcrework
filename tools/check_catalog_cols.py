import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

print(f"Total maps in catalog: {len(cat['maps'])}")
for m in cat['maps'][:25]:
    mid = m['id']
    w, h = m.get('width'), m.get('height')
    cw, ch = m.get('col_width'), m.get('col_height')
    has_col = m.get('has_collision')
    col_path = m.get('collision_bin')
    fsize = os.path.getsize(os.path.join('web', col_path)) if col_path and os.path.exists(os.path.join('web', col_path)) else 0
    bits = fsize * 8
    calc_stride = round(bits / ch) if ch else 0
    print(f"Map {mid:2d} ({m['name']}): Dim={w}x{h}, ColDim={cw}x{ch}, bin_size={fsize}, bits={bits}, bits/col_h={bits/ch if ch else 0:.2f}, bits/h={bits/h if h else 0:.2f}")
