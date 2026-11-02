import os, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

files = ['data_tbl_creature_handbook.sql', 'data_tbl_pet_contract.sql', 'data_tbl_sublimation_pet.sql', 'data_tbl_creatureh_contain.sql']
for name in files:
    path = os.path.join('mcgame', 'supabase', 'seeds', name)
    if os.path.exists(path):
        print(f"\n=== {name} ===")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [l.strip() for l in f.readlines() if 'INSERT INTO' in l or (l.strip().startswith('(') and not l.strip().startswith('SET'))]
            for l in lines[:6]:
                print(l[:140])
