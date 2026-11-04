import sys, re, os
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from inspect_equipment import parse_sql_file, get_url

print("Parsing data_tbl_item_template.sql...")
item_cols, items = parse_sql_file('mcgame/supabase/seeds/data_tbl_item_template.sql')
print(f"Total item rows: {len(items)}")

kinds = Counter(it.get('kind') for it in items)
print("Item kinds:", kinds)

types = Counter(it.get('type') for it in items)
print("Item types:", types)

# Check icons in item template
icon_codes = [int(float(it['icon_code'])) for it in items if it.get('icon_code') and it['icon_code'] != '0']
print(f"Total valid icon_codes in item template: {len(icon_codes)}, unique: {len(set(icon_codes))}")

# Check how many exist in res
import hashlib
found = 0
for code in set(icon_codes):
    rel = get_url(code)
    h = hashlib.md5(('icon/' + rel).encode()).hexdigest()
    if os.path.exists(f'mcgame/frontend/s/res/{h}'):
        found += 1
print(f"Icon files existing in res: {found} / {len(set(icon_codes))}")
