import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
eq_map = {int(e['id']): e for e in equipts}

# Let's inspect equipt_id from 1960 to 2050 and all position 21
res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
res_files = set(os.listdir(res_dir))

dresses = []
for eid in range(1960, 2060):
    if eid in eq_map:
        e = eq_map[eid]
        rc = e.get('res_code')
        rcm = e.get('res_code_male')
        rcf = e.get('res_code_female')
        
        # Check urls
        def test_rc(val):
            if val and val != '0':
                code = int(float(val))
                rel = get_url(code)
                import hashlib
                h = hashlib.md5(('resource/' + rel).encode()).hexdigest()
                return rel, h in res_files
            return None, False
        
        rel_m, ex_m = test_rc(rcm or rc)
        rel_f, ex_f = test_rc(rcf)
        
        dresses.append({
            'id': eid,
            'name': e.get('name'),
            'rc': rc, 'rcm': rcm, 'rcf': rcf,
            'rel_m': rel_m, 'ex_m': ex_m,
            'rel_f': rel_f, 'ex_f': ex_f
        })

print(f"Total checked: {len(dresses)}")
for d in dresses[:20]:
    print(f"ID {d['id']}: {d['name']} | Male: {d['rel_m']} (exists? {d['ex_m']}) | Female: {d['rel_f']} (exists? {d['ex_f']})")
