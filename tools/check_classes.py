import sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from inspect_equipment import parse_sql_file

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
print("req_class values:", Counter(e.get('req_class') for e in equipts))
print("req_class_id values:", Counter(e.get('req_class_id') for e in equipts))

# Sample per class
for c in set(e.get('req_class_id') for e in equipts):
    samples = [e['name'] for e in equipts if e.get('req_class_id') == c][:3]
    print(f"req_class_id={c}: {samples}")
