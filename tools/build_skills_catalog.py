import sys, os, re, json, glob

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

CLASS_NAMES = {
    1: 'Chiến Binh (Guerreiro)',
    2: 'Nhạc Công (Bardo)',
    3: 'Y Sư (Clérigo)',
    4: 'Xạ Thủ (Atirador)',
    5: 'Thợ Săn (Caçador)',
    6: 'Hiệp Sĩ (Paladino)'
}

KIND_NAMES = {
    1: 'Ativa',
    2: 'Passiva',
    3: 'Buff / Encantamento',
    4: 'Funcional / Suporte'
}

TYPE_NAMES = {
    1: 'Ataque Físico Corpo-a-Corpo',
    2: 'Ataque Físico à Distância',
    3: 'Magia de Dano Direto',
    4: 'Magia de Projétil',
    5: 'Cura e Restauração',
    6: 'Efeito / Status (Buff/Debuff)',
    7: 'Purificação / Dispel',
    8: 'Habilidade Funcional Ofensiva',
    9: 'Recuperação Funcional',
    10: 'Habilidade Passiva',
    11: 'Guardião / Proteção'
}

TARGET_NAMES = {
    1: 'Próprio',
    2: 'Próprio Jogador',
    3: 'Próprio Pet',
    4: 'Inimigo Único',
    5: 'Jogador Inimigo',
    6: 'Monstro Inimigo',
    7: 'Inimigo (Não Chefe)',
    8: 'Equipe / Aliados',
    9: 'Jogadores da Equipe',
    10: 'Pets da Equipe',
    11: 'Todos (Em Área)',
    12: 'Alvo Único'
}

AREA_NAMES = {
    0: 'Único',
    1: 'Vertical (Coluna)',
    2: 'Horizontal (Linha)',
    3: 'Cruz',
    4: 'Aleatório'
}

def to_int(val, default=0):
    if val is None or val == '' or val == 'NULL':
        return default
    try:
        return int(float(val))
    except Exception:
        return default

# 1. Load available converted effects
available_effects = set()
if os.path.exists('web/assets/effects'):
    for d in os.listdir('web/assets/effects'):
        if os.path.isdir(os.path.join('web/assets/effects', d)):
            try:
                available_effects.add(int(d))
            except ValueError:
                pass
print(f"Available converted effects: {len(available_effects)}")

# 2. Load pet skills mapping
pet_skill_ids = set()
if os.path.exists('mcgame/supabase/seeds/data_tbl_creature_skill.sql'):
    with open('mcgame/supabase/seeds/data_tbl_creature_skill.sql', 'r', encoding='utf-8', errors='ignore') as f:
        sql = f.read()
    rows = re.findall(r'\(([^;]+?)\)[,;]', sql)
    for r in rows:
        parts = [p.strip(" '\"") for p in r.split(',')]
        if len(parts) >= 4:
            try:
                sid = int(parts[3])
                pet_skill_ids.add(sid)
            except Exception:
                pass
print(f"Found {len(pet_skill_ids)} pet skill IDs")

# 3. Parse data_tbl_skill.sql
with open('mcgame/supabase/seeds/data_tbl_skill.sql', 'r', encoding='utf-8', errors='ignore') as f:
    sql = f.read()

m = re.search(r'INSERT INTO "data"\."data_tbl_skill"\s*\((.+?)\)\s*VALUES', sql)
cols = [c.strip(' "') for c in m.group(1).split(',')]

def parse_row(r):
    fields = []
    in_quote = False
    cur = []
    for ch in r:
        if ch == "'":
            in_quote = not in_quote
            cur.append(ch)
        elif ch == ',' and not in_quote:
            fields.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    fields.append(''.join(cur).strip())
    return [f.strip("'") for f in fields]

rows = re.findall(r'\(([^;]+?)\)[,;]', sql, re.DOTALL)
print(f"Total raw skill rows: {len(rows)}")

grouped_skills = {}
for r in rows:
    fields = parse_row(r)
    if len(fields) != len(cols):
        continue
    d = dict(zip(cols, fields))
    
    code_name = d.get('code_name', '').strip()
    name = d.get('name', '').strip()
    if not name or not code_name:
        continue
        
    try:
        skill_id = to_int(d.get('id', '0'))
        lvl = to_int(d.get('level', '1'))
    except Exception:
        continue
        
    key = code_name
    if key not in grouped_skills:
        grouped_skills[key] = []
    grouped_skills[key].append((lvl, skill_id, d))

print(f"Grouped into {len(grouped_skills)} distinct skills")

# Convert to structured catalog
catalog_items = []
sorted_effects = sorted(list(available_effects))

# Effect fallback mapper based on type and class
def get_effect_for_skill(skill_type, req_classes, skill_id):
    if skill_id in available_effects:
        return skill_id
    
    if skill_type == 1: # Physical Melee
        candidates = [10008, 10001, 10005, 301, 402, 410, 416, 422]
    elif skill_type == 2: # Physical Ranged
        candidates = [307, 310, 311, 403, 409, 417, 10002]
    elif skill_type in (3, 4): # Magic
        candidates = [302, 303, 312, 318, 404, 412, 418, 426, 10003]
    elif skill_type in (5, 9): # Heal
        candidates = [314, 315, 320, 405, 413, 424, 430, 10010]
    elif skill_type in (6, 7): # Buff / Debuff
        candidates = [6, 11, 20, 21, 328, 406, 435, 10013, 10014]
    else:
        candidates = [10008, 10001, 6, 301]
        
    for c in candidates:
        if c in available_effects:
            return c
    return sorted_effects[0] if sorted_effects else 10008

for code_name, levels in grouped_skills.items():
    levels.sort(key=lambda x: x[0])
    base_lvl, base_id, base_data = levels[0]
    max_lvl = levels[-1][0]
    
    # Extract icon
    icon_code = base_data.get('icon_code', '')
    icon_num = 0
    if icon_code:
        try:
            c = int(float(icon_code))
            icon_num = (c % 1000000000000 % 1000000000) % 1000000
        except Exception:
            pass
            
    icon_path = f"assets/skills/icons/{icon_num}.png" if icon_num > 0 else ""
    if icon_num > 0 and not os.path.exists(os.path.join('web', icon_path)):
        icon_path = ""
        
    kind = to_int(base_data.get('kind', 1), 1)
    stype = to_int(base_data.get('type', 1), 1)
    target_type = to_int(base_data.get('target_type', 4), 4)
    target_num = to_int(base_data.get('target_num', 1), 1)
    area_attack = to_int(base_data.get('area_attack', 0), 0)
    
    req_class_str = base_data.get('req_class', '') or ''
    req_class_ids = [int(x) for x in re.findall(r'\d+', req_class_str)]
    req_class_names = [CLASS_NAMES.get(cid, f'Classe {cid}') for cid in req_class_ids]
    
    category = "general"
    if any(lvl_sid in pet_skill_ids for _, lvl_sid, _ in levels):
        category = "pet"
    elif req_class_ids:
        category = "class"
    elif kind == 4:
        category = "utility"
    elif kind == 2:
        category = "passive"
        
    eff_id = get_effect_for_skill(stype, req_class_ids, base_id)
    
    desc = base_data.get('description', '') or ''
    desc = desc.replace(r'\n', '\n').replace("''", "'")
    desc = re.sub(r'<font[^>]*>', '', desc).replace('</font>', '')
    
    item = {
        "id": base_id,
        "code_name": code_name,
        "name": base_data.get('name', ''),
        "max_level": max_lvl,
        "category": category,
        "kind": kind,
        "kind_name": KIND_NAMES.get(kind, 'Especial'),
        "type": stype,
        "type_name": TYPE_NAMES.get(stype, 'Geral'),
        "target_type": target_type,
        "target_name": TARGET_NAMES.get(target_type, 'Alvo'),
        "target_num": target_num,
        "area_attack": area_attack,
        "area_name": AREA_NAMES.get(area_attack, 'Único'),
        "req_class_ids": req_class_ids,
        "req_classes": req_class_names,
        "req_level": to_int(base_data.get('req_level', 1), 1),
        "use_mp": to_int(base_data.get('use_mp', 0), 0),
        "use_sp": to_int(base_data.get('use_sp', 0), 0),
        "use_hp": to_int(base_data.get('use_hp', 0), 0),
        "description": desc,
        "icon_num": icon_num,
        "icon": icon_path,
        "effect_id": eff_id
    }
    catalog_items.append(item)

# Sort by Category, then Req Level, then Name
catalog_items.sort(key=lambda x: (x["category"], x["req_level"], x["name"]))

OUT_CATALOG = 'web/assets/skills/catalog.json'
os.makedirs(os.path.dirname(OUT_CATALOG), exist_ok=True)
with open(OUT_CATALOG, 'w', encoding='utf-8') as f_out:
    json.dump(catalog_items, f_out, indent=2, ensure_ascii=False)

print(f"\nGenerated skill catalog with {len(catalog_items)} unique skills at {OUT_CATALOG}!")
print("Sample entries:")
for s in catalog_items[:8]:
    print(f"  [{s['category'].upper():<7}] {s['name']:<20} | Type: {s['type_name']:<26} | Icon: {s['icon_num']:<4} | Effect: {s['effect_id']}")
