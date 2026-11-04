import json, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open(r'mcgame\docs\database\game_data\TBL_EQUIPT_TEMPLATE.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

records = data.get('records', [])
if isinstance(records, dict):
    records = list(records.values())

print(f"Total records: {len(records)}")

res_stats = defaultdict(lambda: {'count': 0, 'has_res': 0, 'has_male': 0, 'has_female': 0, 'sample': []})

for it in records:
    k = it.get('kind', 0)
    rc = it.get('resCode', 0)
    rcm = it.get('resCodeMale', 0)
    rcf = it.get('resCodeFemale', 0)
    res_stats[k]['count'] += 1
    if rc: res_stats[k]['has_res'] += 1
    if rcm: res_stats[k]['has_male'] += 1
    if rcf: res_stats[k]['has_female'] += 1
    if (rc or rcm or rcf) and len(res_stats[k]['sample']) < 5:
        res_stats[k]['sample'].append((it.get('id'), it.get('name'), rc, rcm, rcf))

print('Kind Breakdown:')
for k, st in sorted(res_stats.items()):
    c = st['count']
    hr = st['has_res']
    hm = st['has_male']
    hf = st['has_female']
    print(f"Kind {k}: total={c}, resCode={hr}, male={hm}, female={hf}")
    for s in st['sample']:
        print(f"   Sample: ID={s[0]}, Name={s[1]}, resCode={s[2]}, male={s[3]}, female={s[4]}")
