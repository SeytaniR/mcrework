import sys, re, os, hashlib
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RES_URL_FOLDER = {10: '', 15: 'scene/', 20: 'item/', 30: 'item/', 40: 'tile/', 50: 'creature/', 60: 'creature/', 70: 'equip/', 80: 'effect/', 90: 'sound/', 100: 'bullet/', 110: 'emotion/', 120: 'state/', 130: 'ui/', 140: 'skill/'}
RES_URL_WORD1 = {10: '', 15: 'SCENE_', 20: 'SITEM_', 30: 'ITEM_', 40: 'TILE_', 50: 'PC_', 60: 'NPC_', 70: 'EQUIP_', 80: 'EFF_', 90: 'WAV_', 100: 'BLT_', 110: 'EM_', 120: 'ST_', 130: 'UI_', 140: 'SKILL_'}
RES_URL_WORD2 = {10: '', 15: 'FOLDER_', 16: 'FLOWER_', 20: 'TREE_', 30: 'HOUSE_', 40: 'SPAWN_', 50: 'DESERT_', 60: 'FOREST_', 70: 'MALE_', 80: 'FEMALE_', 90: 'FUNC_', 100: 'CRE_', 110: 'WEAPON_', 120: 'SCENE_', 130: 'PLAYER_', 140: 'SIDE_', 150: 'SCREEN_', 160: 'NPC_', 170: 'UI_', 180: 'EFF_', 190: 'FIRE_', 200: 'NORMAL_', 210: 'LOCAL_', 220: 'GLOBAL_', 230: 'STAGE_', 240: 'BATTLE_', 250: 'LOADING_', 260: 'FC1_', 270: 'FC2_', 280: 'FC3_', 290: 'FC4_', 300: 'FC5_', 310: 'FC6_', 320: 'MC1_', 330: 'MC2_', 340: 'MC3_', 350: 'MC4_', 360: 'MC5_', 370: 'MC6_', 380: 'FLY_', 390: 'WING_'}
RES_URL_EXT = {1: '', 2: '.swf', 3: '.jpg', 4: '.png', 5: '.wav', 6: '.mp3', 7: '.ogg'}

def get_url(code):
    if not code or code <= 0:
        return ''
    ext_id = int(code // 1000000000000)
    rem = code % 1000000000000
    w1_id = int(rem // 1000000000)
    rem = rem % 1000000000
    w2_id = int(rem // 1000000)
    num = str(rem)[-6:].zfill(6)
    folder = RES_URL_FOLDER.get(w1_id, '')
    w1 = RES_URL_WORD1.get(w1_id, '')
    w2 = RES_URL_WORD2.get(w2_id, '')
    ext = RES_URL_EXT.get(ext_id, '')
    return f'{folder}{w1}{w2}{num}{ext}'

def parse_sql_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # extract columns
    col_match = re.search(r'INSERT INTO [^(]+\(([^)]+)\)', text)
    cols = [c.strip().strip('"') for c in col_match.group(1).split(',')]
    
    # parse tuples accurately handling strings with commas
    val_pattern = re.compile(r'\((.*?)\)(?:,\n|\);\n|\Z)', re.DOTALL)
    items = []
    
    # Simple state machine parser for CSV row inside parentheses
    def split_row(s):
        row = []
        in_quotes = False
        cur = []
        for ch in s:
            if ch == "'" and not in_quotes:
                in_quotes = True
            elif ch == "'" and in_quotes:
                in_quotes = False
            elif ch == ',' and not in_quotes:
                row.append(''.join(cur).strip())
                cur = []
                continue
            cur.append(ch)
        row.append(''.join(cur).strip())
        return row

    for m in val_pattern.finditer(text):
        row_str = m.group(1).strip()
        if not row_str:
            continue
        row_vals = split_row(row_str)
        if len(row_vals) == len(cols):
            d = {}
            for c, v in zip(cols, row_vals):
                v_clean = v.strip("'")
                if v == 'NULL':
                    d[c] = None
                else:
                    d[c] = v_clean
            items.append(d)
    return cols, items

print("Parsing data_tbl_equipt_template.sql...")
eq_cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
print(f"Total equipment rows parsed: {len(equipts)}")

positions = Counter(e.get('position') for e in equipts)
print("Equipment by position:", positions)

kinds = Counter(e.get('kind') for e in equipts)
print("Equipment by kind:", kinds)

types = Counter(e.get('type') for e in equipts)
print("Equipment by type:", types)

# Check icon_code
icon_codes = [int(float(e['icon_code'])) for e in equipts if e.get('icon_code') and e['icon_code'] != '0']
print(f"Total valid icon_codes: {len(icon_codes)}, unique: {len(set(icon_codes))}")

# Check res_code (models / swfs)
res_codes = [int(float(e['res_code'])) for e in equipts if e.get('res_code') and e['res_code'] != '0']
print(f"Total valid res_codes: {len(res_codes)}, unique: {len(set(res_codes))}")

res_male = [int(float(e['res_code_male'])) for e in equipts if e.get('res_code_male') and e['res_code_male'] != '0']
print(f"Total valid res_code_male: {len(res_male)}, unique: {len(set(res_male))}")

# Check sample URLs
print("\nSample equipment icon URLs:")
for code in list(set(icon_codes))[:10]:
    rel = get_url(code)
    h = hashlib.md5(('icon/' + rel).encode()).hexdigest()
    exists = os.path.exists(f'mcgame/frontend/s/res/{h}')
    print(f"Code {code} -> {rel} (icon/ -> {h} exists? {exists})")

print("\nSample equipment res_code URLs (models/swfs):")
for code in list(set(res_codes))[:10]:
    rel = get_url(code)
    h = hashlib.md5(('resource/' + rel).encode()).hexdigest()
    exists = os.path.exists(f'mcgame/frontend/s/res/{h}')
    print(f"Code {code} -> {rel} (resource/ -> {h} exists? {exists})")

if res_male:
    print("\nSample equipment res_code_male URLs:")
    for code in list(set(res_male))[:10]:
        rel = get_url(code)
        h = hashlib.md5(('resource/' + rel).encode()).hexdigest()
        exists = os.path.exists(f'mcgame/frontend/s/res/{h}')
        print(f"Code {code} -> {rel} (resource/ -> {h} exists? {exists})")
