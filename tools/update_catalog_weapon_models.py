import os, sys, hashlib, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
equipt_map = {int(e['id']): e for e in equipts}

with open('web/assets/equipment/catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

weapons_dir = 'web/assets/weapons'
available_models = set(os.listdir(weapons_dir))
print(f"Available extracted weapon models on disk: {len(available_models)}")

# Subtype fallback models if specific model is not yet extracted:
# 100/101: Hammer/Club/Axe -> equip_mc1_000001
# 102: Staff/Cajado -> equip_mc2_000001
# 103: Sword/Espada -> equip_mc4_000000
# 104: Gun/Rifle -> equip_mc5_000001
# 105: Instrument/Alaúde -> equip_mc6_000001
# other: equip_mc3_000001
SUBTYPE_FALLBACKS = {
    100: "equip_mc1_000001",
    101: "equip_mc1_000001",
    102: "equip_mc2_000001",
    103: "equip_mc4_000000",
    104: "equip_mc5_000001",
    105: "equip_mc6_000001",
}

mapped_count = 0
for item in catalog.get('items', []):
    eid = item['id']
    raw = equipt_map.get(eid)
    if not raw:
        continue
    
    # Check weapon models
    rc = raw.get('res_code')
    rcm = raw.get('res_code_male')
    rcf = raw.get('res_code_female')
    
    val = rcm if (rcm and rcm != '0') else (rc if (rc and rc != '0') else (rcf if (rcf and rcf != '0') else None))
    if val:
        code = int(float(val))
        rel = get_url(code)
        model_name = os.path.splitext(os.path.basename(rel))[0].lower()
        item['model_id'] = model_name
        item['model_rel'] = rel
        
        if model_name in available_models:
            item['has_converted_model'] = True
            item['active_weapon_model'] = model_name
            mapped_count += 1
        elif item.get('category_group') == 'weapons':
            # Use appropriate class fallback
            fb = SUBTYPE_FALLBACKS.get(item.get('subtype'), "equip_mc1_000001")
            item['has_converted_model'] = True
            item['active_weapon_model'] = fb
            item['is_fallback_model'] = True
            mapped_count += 1
    elif item.get('category_group') == 'weapons':
        fb = SUBTYPE_FALLBACKS.get(item.get('subtype'), "equip_mc1_000001")
        item['model_id'] = fb
        item['has_converted_model'] = True
        item['active_weapon_model'] = fb
        item['is_fallback_model'] = True
        mapped_count += 1

print(f"Weapons configured with live weapon models: {mapped_count}")

with open('web/assets/equipment/catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print("catalog.json updated successfully!")
