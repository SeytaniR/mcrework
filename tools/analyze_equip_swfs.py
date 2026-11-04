import sys, os, hashlib
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')

from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')

swf_categories = Counter()
swf_details = []

for e in equipts:
    for k in ['res_code', 'res_code_male', 'res_code_female', 'res_code_male2', 'res_code_female2']:
        v = e.get(k)
        if v and v != '0':
            code = int(float(v))
            rel = get_url(code)
            h = hashlib.md5(('resource/' + rel).encode()).hexdigest()
            p = f'mcgame/frontend/s/res/{h}'
            if os.path.exists(p):
                prefix = rel.split('_')[1] if '_' in rel else 'OTHER'
                swf_categories[prefix] += 1
                swf_details.append({
                    'code': code,
                    'rel': rel,
                    'prefix': prefix,
                    'size': os.path.getsize(p),
                    'equip_name': e['name'],
                    'pos': e['position'],
                    'kind': e['kind']
                })

print("SWF count by prefix:", swf_categories)
print(f"Total existing references: {len(swf_details)}, unique SWFs: {len(set(d['rel'] for d in swf_details))}")

# Unique by prefix
for prefix in sorted(swf_categories.keys()):
    sample = [d for d in swf_details if d['prefix'] == prefix]
    unique_rels = set(d['rel'] for d in sample)
    print(f"  Prefix {prefix}: {len(unique_rels)} unique SWFs (e.g. {sample[0]['rel']}, {sample[0]['equip_name']}, pos={sample[0]['pos']})")
