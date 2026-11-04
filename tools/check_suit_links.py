import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')

from inspect_equipment import parse_sql_file

cols, suits = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_suit.sql')
suit_map = {int(s['id']): s['name'] for s in suits if s.get('id')}
print(f"Total suits mapped: {len(suit_map)}")

eq_cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
suits_used = [int(float(e['suit_id'])) for e in equipts if e.get('suit_id') and e['suit_id'] != '0']
print(f"Equipment items with suits: {len(suits_used)}, unique suit IDs: {len(set(suits_used))}")
for sid in list(set(suits_used))[:10]:
    print(f"  Suit {sid}: {suit_map.get(sid, 'Unknown')}")
