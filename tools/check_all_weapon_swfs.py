import os, sys, hashlib, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
res_dir = 'mcgame/frontend/s/res'

weapons = [e for e in equipts if e.get('kind') == '1']
weapon_swfs = {}

for w in weapons:
    wid = int(w['id'])
    wname = w['name']
    
    # Check all res code fields
    for k in ['res_code_male', 'res_code']:
        v = w.get(k)
        if v and v != '0':
            code = int(float(v))
            rel = get_url(code)
            if 'equip/' in rel:
                h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
                p = os.path.join(res_dir, h)
                if os.path.exists(p):
                    if rel not in weapon_swfs:
                        weapon_swfs[rel] = {'rel': rel, 'hash': h, 'items': [], 'size': os.path.getsize(p)}
                    weapon_swfs[rel]['items'].append({'id': wid, 'name': wname})

print(f"Total unique weapon SWFs for weapons: {len(weapon_swfs)}")
for rel, data in sorted(weapon_swfs.items()):
    items_str = ", ".join(f"{it['id']} ({it['name']})" for it in data['items'][:2])
    print(f" - {rel} ({data['size']} bytes) -> {len(data['items'])} items: {items_str}")
