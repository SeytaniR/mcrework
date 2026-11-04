import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from inspect_equipment import parse_sql_file

cols, suits = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_suit.sql')
print("Total equipt suits:", len(suits))
for s in suits[:10]:
    print(s)
