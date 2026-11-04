import os

with open('mcgame/supabase/seeds/data_tbl_equipt_template.sql', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'INSERT INTO' in line:
            start = line.find('(')
            end = line.find(')')
            cols = [c.strip().strip('"') for c in line[start+1:end].split(',')]
            print(f'Total cols: {len(cols)}')
            print('res cols:', [c for c in cols if 'res' in c])
            break
