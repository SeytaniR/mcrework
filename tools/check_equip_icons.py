import sys, os, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
unique_icons = set()
for e in equipts:
    code = e.get('icon_code')
    if code and code != '0':
        unique_icons.add(int(float(code)))

print(f"Total unique equipment icon codes: {len(unique_icons)}")

found = 0
missing = 0
for code in unique_icons:
    rel = get_url(code)
    h = hashlib.md5(('icon/' + rel).encode()).hexdigest()
    if os.path.exists(f'mcgame/frontend/s/res/{h}'):
        found += 1
    else:
        missing += 1

print(f"Equipment icons found: {found} / {len(unique_icons)} (missing: {missing})")
