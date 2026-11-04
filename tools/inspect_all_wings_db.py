import os, sys, hashlib, json, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
res_files = set(os.listdir(res_dir))

wings_db = []
for e in equipts:
    # Position 22 = Wings / Cánh
    pos = e.get('position')
    name = e.get('name', '')
    if pos == '22' or 'cánh' in name.lower() or 'wing' in name.lower():
        v = e.get('res_code') or e.get('res_code_male') or e.get('res_code_female')
        code = int(float(v)) if v and v != '0' else None
        rel = get_url(code) if code else None
        h = hashlib.md5(('resource/' + rel).encode()).hexdigest() if rel else None
        exists = h in res_files if h else False
        
        # Icon
        ic = e.get('icon_code')
        ic_code = int(float(ic)) if ic and ic != '0' else None
        ic_rel = get_url(ic_code) if ic_code else None
        ic_h = hashlib.md5(('icon/' + ic_rel).encode()).hexdigest() if ic_rel else None
        ic_exists = ic_h in res_files if ic_h else False
        
        wings_db.append({
            'id': e.get('id'),
            'name': name,
            'pos': pos,
            'code': code,
            'rel': rel,
            'hash': h,
            'exists': exists,
            'icon_code': ic_code,
            'icon_rel': ic_rel,
            'icon_hash': ic_h,
            'icon_exists': ic_exists,
            'desc': e.get('description', '')
        })

print(f"Total Wings in DB: {len(wings_db)}")
for w in wings_db:
    print(f"ID {w['id']}: {w['name']} | SWF: {w['rel']} (exists? {w['exists']}) | Icon: {w['icon_rel']} (exists? {w['icon_exists']})")

with open('tools/wings_db.json', 'w', encoding='utf-8') as f:
    json.dump(wings_db, f, indent=2, ensure_ascii=False)
