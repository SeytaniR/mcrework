import os, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')

mc1_items = []
res_dir = 'mcgame/frontend/s/res'

for e in equipts:
    for k in ['res_code', 'res_code_male', 'res_code_female']:
        v = e.get(k)
        if v and v != '0':
            code = int(float(v))
            rel = get_url(code)
            if 'MC1' in rel:
                h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
                path = os.path.join(res_dir, h)
                if os.path.exists(path):
                    mc1_items.append({
                        'id': int(e['id']),
                        'name': e['name'],
                        'code': code,
                        'rel': rel,
                        'hash': h,
                        'size': os.path.getsize(path),
                        'field': k
                    })

print(f"Total MC1 item references found: {len(mc1_items)}")
unique_rels = set(x['rel'] for x in mc1_items)
print(f"Unique MC1 SWF files: {len(unique_rels)}")
for rel in sorted(unique_rels):
    items = [x for x in mc1_items if x['rel'] == rel]
    print(f" - {rel} ({items[0]['size']} bytes): used by {len(items)} items: {', '.join(x['name'] for x in items[:3])}")
