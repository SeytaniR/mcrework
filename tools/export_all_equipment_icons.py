import sys, os, hashlib, shutil
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')

from inspect_equipment import parse_sql_file, get_url

print("Starting export of all equipment & weapon icons...")

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
print(f"Total equipment items in database: {len(equipts)}")

out_dir = r'web\assets\equipment\icons'
os.makedirs(out_dir, exist_ok=True)

icon_map = {}
copied = 0
skipped = 0
missing = 0

for e in equipts:
    code_str = e.get('icon_code')
    if not code_str or code_str == '0':
        continue
    code = int(float(code_str))
    
    # get relative url
    rel = get_url(code)
    # relative format: equip/EQUIP_NORMAL_050205.png
    # icon_id is typically the number part without leading zeros or with standard identifier
    icon_filename = os.path.basename(rel) # e.g. EQUIP_NORMAL_050205.png
    
    # Compute MD5
    h = hashlib.md5(('icon/' + rel).encode()).hexdigest()
    src = f'mcgame/frontend/s/res/{h}'
    
    dest_name = icon_filename.replace('.png', '').lower() + '.png' # e.g. equip_normal_050205.png
    dest_path = os.path.join(out_dir, dest_name)
    
    # Map code to dest_name
    icon_map[code] = dest_name
    
    if os.path.exists(dest_path):
        skipped += 1
        continue
    
    if os.path.exists(src):
        shutil.copyfile(src, dest_path)
        copied += 1
    else:
        missing += 1

print(f"Icon Export Complete!")
print(f"  Copied new: {copied}")
print(f"  Already existed: {skipped}")
print(f"  Missing: {missing}")
print(f"  Total mapped: {len(icon_map)}")

# Check output dir count
total_files = len(os.listdir(out_dir))
print(f"Total icon files in {out_dir}: {total_files}")
