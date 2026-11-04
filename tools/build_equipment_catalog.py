import sys, os, json, hashlib, re
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')

from inspect_equipment import parse_sql_file, get_url

print("Building complete equipment and weapons catalog with visual attributes...")

# 1. Load suits
suit_cols, raw_suits = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_suit.sql')
suits_map = {}
for s in raw_suits:
    if s.get('id'):
        suits_map[int(s['id'])] = {
            'id': int(s['id']),
            'name': s.get('name', ''),
            'name_pt': s.get('name', '').replace('Bộ Trang Bị', 'Conjunto').strip(),
            'skill_desc': s.get('skill_description')
        }

# 2. Position mappings
POSITION_MAP = {
    1: {"name": "Elmo / Tiara", "cat": "armor"},
    2: {"name": "Cinto", "cat": "armor"},
    3: {"name": "Arma Principal", "cat": "weapons"},
    4: {"name": "Peitoral / Túnica", "cat": "armor"},
    5: {"name": "Calças / Perneiras", "cat": "armor"},
    6: {"name": "Acessório I", "cat": "jewelry"},
    7: {"name": "Arma Secundária (Offhand)", "cat": "offhand"},
    8: {"name": "Colar / Amuleto", "cat": "jewelry"},
    9: {"name": "Anel", "cat": "jewelry"},
    10: {"name": "Ombreiras", "cat": "armor"},
    11: {"name": "Acessório II", "cat": "jewelry"},
    12: {"name": "Botas", "cat": "armor"},
    13: {"name": "Luvas de Coleta", "cat": "armor"},
    14: {"name": "Montaria Alada / Voo", "cat": "wings_costumes"},
    15: {"name": "Relíquia Divina Principal", "cat": "weapons"},
    16: {"name": "Relíquia Divina II", "cat": "weapons"},
    17: {"name": "Relíquia Divina III", "cat": "weapons"},
    18: {"name": "Relíquia Divina IV", "cat": "weapons"},
    19: {"name": "Relíquia Divina V", "cat": "weapons"},
    20: {"name": "Relíquia Divina VI", "cat": "weapons"},
    21: {"name": "Traje Visual / Costume", "cat": "wings_costumes"},
    22: {"name": "Asas Celestiais", "cat": "wings_costumes"},
    50: {"name": "Selo de Chifre (Pet)", "cat": "pet"},
    51: {"name": "Coleira Protetora (Pet)", "cat": "pet"},
    52: {"name": "Sino de Batalha (Pet)", "cat": "pet"},
    53: {"name": "Asas Protetoras (Pet)", "cat": "pet"},
    54: {"name": "Armadura de Combate (Pet)", "cat": "pet"},
    55: {"name": "Ombreiras de Fera (Pet)", "cat": "pet"},
    56: {"name": "Selo Elemental I (Pet)", "cat": "pet"},
    57: {"name": "Selo Elemental II (Pet)", "cat": "pet"},
}

# Subtype names
TYPE_MAP = {
    100: "Martelo de Guerra / Maça",
    101: "Cajado Mágico",
    102: "Rifle / Mosquete de Disparo",
    103: "Espada Longa",
    104: "Alaúde Encantado",
    105: "Bastão de Combate",
    200: "Escudo de Defesa",
    201: "Grimório Sagrado",
    202: "Braçadeira de Precisão",
    203: "Adaga Veloz",
    204: "Cítara de Ataque",
    205: "Manoplas de Batalha",
    300: "Elmo",
    301: "Peitoral",
    302: "Perneiras",
    303: "Cinto",
    304: "Botas",
    305: "Ombreiras",
    400: "Colar",
    401: "Anel",
    402: "Talismã I",
    403: "Talismã II",
    800: "Thần Khí Principal",
    801: "Thần Khí Secundária",
    900: "Chifre de Fera",
    901: "Coleira de Fera",
    902: "Sino Místico",
    903: "Asas de Pet",
    904: "Armadura de Pet",
    905: "Ombreiras de Pet",
    906: "Selo Espiritual I",
    907: "Selo Espiritual II",
    1000: "Voo Celestial",
    1100: "Traje Especial",
    1200: "Luvas de Coleta",
    1201: "Vara de Pesca",
    1300: "Asas Celestiais",
}

# Quality tiers
QUALITY_MAP = {
    -1: {"name": "Comum", "color": "#e2e8f0"},
    0: {"name": "Comum", "color": "#e2e8f0"},
    1: {"name": "Incomum", "color": "#22c55e"},
    2: {"name": "Raro", "color": "#3b82f6"},
    3: {"name": "Épico", "color": "#a855f7"},
    4: {"name": "Lendário", "color": "#f97316"},
    5: {"name": "Mítico", "color": "#eab308"},
    6: {"name": "Divino", "color": "#ef4444"},
    7: {"name": "Celestial", "color": "#06b6d4"},
    8: {"name": "Supremo", "color": "#f43f5e"},
    9: {"name": "Ancestral", "color": "#ec4899"},
    10: {"name": "Imortal", "color": "#fbbf24"},
}

PROP_NAMES = {
    1: "HP Máximo",
    2: "MP Máximo",
    3: "Energia",
    4: "Ataque Físico",
    5: "Ataque Mágico",
    6: "Defesa Física",
    7: "Defesa Mágica",
    8: "Precisão",
    9: "Evasão",
    10: "Contra-Ataque",
    11: "Velocidade / Agilidade",
    12: "Ataque Duplo (Combo)",
    13: "Acerto Crítico",
    14: "Perfuração de Armadura",
    20: "Força (STR)",
    21: "Agilidade (AGI)",
    22: "Inteligência (INT)",
    23: "Resistência (STA)",
    24: "HP Máximo (%)",
    25: "MP Máximo (%)",
    26: "Taxa de Ressurreição",
    27: "Resistência a Crítico",
    28: "Resistência a Debuff",
    29: "Resistência a Perfuração"
}

# Class decoder
def decode_classes(req_class):
    if not req_class or req_class in ['0', '-1', '|1|2|3|4|5|6|', '|1|2|3|4|6|5|', '|1|2|3|5|6|4|', '|1|2|3|5|4|6|', '|4|6|5|3|2|1|']:
        return ["Todas"]
    classes = []
    if '|1|' in req_class: classes.append("Guerreiro")
    if '|2|' in req_class: classes.append("Bardo")
    if '|3|' in req_class: classes.append("Sacerdote")
    if '|4|' in req_class: classes.append("Atirador")
    if '|5|' in req_class: classes.append("Caçador")
    if '|6|' in req_class: classes.append("Paladino")
    return classes if classes else ["Todas"]

# Helper translations
TRANSLATE_WORDS = [
    (r'\bKiếm\b', 'Espada'),
    (r'\bTrường Đao\b', 'Lâmina Longa'),
    (r'\bĐao\b', 'Sabre'),
    (r'\bTrượng\b', 'Cajado'),
    (r'\bBổng\b', 'Bastão'),
    (r'\bSúng\b', 'Rifle'),
    (r'\bHỏa Súng\b', 'Mosquete'),
    (r'\bChuỳ\b|\bChùy\b', 'Maça'),
    (r'\bCầm\b', 'Alaúde'),
    (r'\bThuẫn\b', 'Escudo'),
    (r'\bSách\b', 'Grimório'),
    (r'\bChủy thủ\b', 'Adaga'),
    (r'\bCung\b', 'Arco'),
    (r'\bHộ uyển\b', 'Braçadeira'),
    (r'\bMũ\b|\bKhôi\b', 'Elmo'),
    (r'\bÁo\b|\bKhải\b', 'Armadura'),
    (r'\bQuần\b|\bKhố\b', 'Perneiras'),
    (r'\bĐai\b', 'Cinto'),
    (r'\bGiày\b|\bOa\b', 'Botas'),
    (r'\bHộ vai\b', 'Ombreiras'),
    (r'\bDây chuyền\b|\bHạng Liên\b', 'Colar'),
    (r'\bNhẫn\b|\bGiới Chỉ\b', 'Anel'),
    (r'\bCánh\b', 'Asas'),
    (r'\bThời Trang\b', 'Traje'),
    (r'\bPhi Long\b', 'Dragão Alado'),
    (r'\bQuy Nguyên Thủ\b', 'Manoplas do Vazio'),
]

def pt_name_hint(orig_name, pos_id, type_id):
    name = orig_name
    for pattern, repl in TRANSLATE_WORDS:
        name = re.sub(pattern, repl, name, flags=re.IGNORECASE)
    return name

# 3. Parse data_tbl_equipt_template.sql
cols, raw_equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
print(f"Total equipment items to process: {len(raw_equipts)}")

catalog_items = []
category_counts = Counter()

for e in raw_equipts:
    eid = int(e['id'])
    name_orig = e.get('name', f'Equipamento #{eid}')
    desc = e.get('description') or ''
    
    pos_id = int(float(e.get('position', 0)))
    pos_info = POSITION_MAP.get(pos_id, {"name": f"Slot {pos_id}", "cat": "armor"})
    cat_group = pos_info["cat"]
    
    kind_id = int(float(e.get('kind', 0)))
    type_id = int(float(e.get('type', 0)))
    type_name = TYPE_MAP.get(type_id, pos_info["name"])
    
    req_lvl = int(float(e.get('req_level', 0))) if e.get('req_level') else 0
    item_lvl = int(float(e.get('item_level', 0))) if e.get('item_level') else req_lvl
    
    req_classes = decode_classes(e.get('req_class'))
    
    color_val = int(float(e.get('color', 0))) if e.get('color') else 0
    q_info = QUALITY_MAP.get(color_val, {"name": "Comum", "color": "#e2e8f0"})
    
    suit_id = int(float(e['suit_id'])) if e.get('suit_id') and e['suit_id'] != '0' else None
    suit_name = suits_map[suit_id]['name_pt'] if suit_id and suit_id in suits_map else None
    
    # icon url
    icon_code_str = e.get('icon_code')
    icon_file = "default.png"
    if icon_code_str and icon_code_str != '0':
        rel = get_url(int(float(icon_code_str)))
        dest_name = os.path.basename(rel).replace('.png', '').lower() + '.png'
        icon_file = dest_name
    
    # check model swf
    res_code_val = e.get('res_code') or e.get('res_code_male') or e.get('res_code_female')
    has_model = False
    model_path = None
    if res_code_val and res_code_val != '0':
        code = int(float(res_code_val))
        rel_swf = get_url(code)
        h = hashlib.md5(('resource/' + rel_swf).encode()).hexdigest()
        if os.path.exists(f'mcgame/frontend/s/res/{h}'):
            has_model = True
            model_path = rel_swf
            
    # parse stats / properties
    stats = []
    for p_type_key, p_num_key in [('main_prop1', 'main_prop_num1'), ('main_prop2', 'main_prop_num2'), ('prop1', 'prop_num1'), ('prop2', 'prop_num2')]:
        ptype_str = e.get(p_type_key)
        pnum_str = e.get(p_num_key)
        if ptype_str and pnum_str and ptype_str != '0' and pnum_str != '0':
            ptype = int(float(ptype_str))
            pnum = int(float(pnum_str))
            label = PROP_NAMES.get(ptype, f'Propriedade #{ptype}')
            prefix = "+" if pnum > 0 else ""
            stats.append({"type": ptype, "label": label, "value": f"{prefix}{pnum}"})

    endure_max = int(float(e.get('endure_max', 0))) if e.get('endure_max') else 0
    hole_num = int(float(e.get('hole_num', 0))) if e.get('hole_num') else 0
    
    name_pt = pt_name_hint(name_orig, pos_id, type_id)
    
    item_obj = {
        "id": eid,
        "name": name_pt,
        "name_orig": name_orig,
        "description": desc,
        "category_group": cat_group,
        "position": pos_id,
        "position_name": pos_info["name"],
        "kind": kind_id,
        "type": type_id,
        "type_name": type_name,
        "req_level": req_lvl,
        "item_level": item_lvl,
        "req_classes": req_classes,
        "quality": q_info["name"],
        "quality_color": q_info["color"],
        "color_code": color_val,
        "suit_id": suit_id,
        "suit_name": suit_name,
        "endure_max": endure_max,
        "holes": hole_num,
        "stats": stats,
        "icon": f"assets/equipment/icons/{icon_file}",
        "has_model": has_model,
        "model_swf": model_path
    }
    
    catalog_items.append(item_obj)
    category_counts[cat_group] += 1

# Sort items by category, then level, then id
catalog_items.sort(key=lambda x: (x['category_group'], x['req_level'], x['id']))

out_json = r'web\assets\equipment\catalog.json'
with open(out_json, 'w', encoding='utf-8') as f:
    json.dump({
        "version": "1.0.0",
        "total": len(catalog_items),
        "categories": {
            "weapons": category_counts["weapons"],
            "offhand": category_counts["offhand"],
            "armor": category_counts["armor"],
            "jewelry": category_counts["jewelry"],
            "wings_costumes": category_counts["wings_costumes"],
            "pet": category_counts["pet"]
        },
        "total_suits": len(suits_map),
        "suits": suits_map,
        "items": catalog_items
    }, f, indent=2, ensure_ascii=False)

file_size_mb = os.path.getsize(out_json) / (1024 * 1024)
print(f"Equipment Catalog successfully built!")
print(f"  Total items: {len(catalog_items)}")
print(f"  Distribution by category group:")
for cat, count in category_counts.items():
    print(f"    - {cat}: {count} items")
print(f"  Total sets (suits): {len(suits_map)}")
print(f"  Output file: {out_json} ({file_size_mb:.2f} MB)")
