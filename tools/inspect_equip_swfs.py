import sys, os, hashlib
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')

all_swfs = set()
for e in equipts:
    for k in ['res_code', 'res_code_male', 'res_code_female', 'res_code_male2', 'res_code_female2']:
        v = e.get(k)
        if v and v != '0':
            all_swfs.add(int(float(v)))

print(f"Total unique SWF codes across all equip rows: {len(all_swfs)}")

found = 0
swf_urls = []
for code in all_swfs:
    rel = get_url(code)
    h = hashlib.md5(('resource/' + rel).encode()).hexdigest()
    path = f'mcgame/frontend/s/res/{h}'
    if os.path.exists(path):
        found += 1
        swf_urls.append((code, rel, path, os.path.getsize(path)))

print(f"Existing SWF files: {found} / {len(all_swfs)}")
print("\nSample SWFs found:")
for s in swf_urls[:20]:
    print(f"  Code {s[0]} -> {s[1]} ({s[3]} bytes)")
