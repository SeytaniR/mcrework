import os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
weapons = [e for e in equipts if e.get('kind') == '1']
print(f'Total Main Weapons: {len(weapons)}')

for w in weapons[:15]:
    rc = w.get('res_code')
    rcm = w.get('res_code_male')
    rcf = w.get('res_code_female')
    print(f"ID: {w['id']} | Name: {w['name']} | res_code: {rc} | male: {rcm} | female: {rcf}")
