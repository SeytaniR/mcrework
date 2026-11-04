import os, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
res_dir = 'mcgame/frontend/s/res'

class_weapons = {}
for c in ['MC1', 'MC2', 'MC3', 'MC4', 'MC5', 'MC6']:
    class_weapons[c] = set()

for e in equipts:
    for k in ['res_code', 'res_code_male']:
        v = e.get(k)
        if v and v != '0':
            code = int(float(v))
            rel = get_url(code)
            for c in class_weapons:
                if c in rel:
                    h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
                    path = os.path.join(res_dir, h)
                    if os.path.exists(path):
                        class_weapons[c].add((rel, h, e['id'], e['name']))

for c, items in sorted(class_weapons.items()):
    unique_swfs = set(x[0] for x in items)
    print(f"Class {c}: {len(unique_swfs)} unique SWFs, {len(items)} item mappings")
