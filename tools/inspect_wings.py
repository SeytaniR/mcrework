import sys, os, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')

wings = []
for e in equipts:
    if e.get('position') == '22' or 'cánh' in e.get('name', '').lower():
        v = e.get('res_code') or e.get('res_code_male') or e.get('res_code_female')
        if v and v != '0':
            code = int(float(v))
            rel = get_url(code)
            h = hashlib.md5(('resource/' + rel).encode()).hexdigest()
            p = f'mcgame/frontend/s/res/{h}'
            if os.path.exists(p):
                wings.append((code, rel, e['name'], os.path.getsize(p), h))

print(f"Total Wings found with existing SWFs: {len(wings)}")
for w in wings[:16]:
    print(f"  {w[1]} - {w[2]} ({w[3]} bytes, md5={w[4]})")
