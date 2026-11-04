import re
import os

files = [
    'mcgame/supabase/seeds/data_tbl_skill.sql',
    'mcgame/supabase/seeds/data_tbl_skill_kind.sql',
    'mcgame/supabase/seeds/data_tbl_skill_type.sql',
    'mcgame/supabase/seeds/data_tbl_creature_skill.sql',
    'mcgame/supabase/seeds/data_tbl_awakening_skill.sql'
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f'File not found: {filepath}')
        continue
    print('='*50)
    print(f'File: {filepath}')
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f_in:
        lines = [f_in.readline() for _ in range(30)]
        for i, l in enumerate(lines):
            if 'INSERT INTO' in l or 'CREATE TABLE' in l:
                print(f'Line {i}: {l.strip()[:160]}')
            elif i < 10:
                print(f'Line {i}: {l.strip()[:160]}')
