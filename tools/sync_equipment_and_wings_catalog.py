import os, sys, hashlib, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from inspect_equipment import parse_sql_file, get_url

cols, equipts = parse_sql_file('mcgame/supabase/seeds/data_tbl_equipt_template.sql')
equipt_map = {int(e['id']): e for e in equipts}

with open('web/assets/equipment/catalog.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

weapons_dir = 'web/assets/weapons'
available_weapons = set(os.listdir(weapons_dir))
wings_dir = 'web/assets/wings'
available_wings = set(os.listdir(wings_dir))

print(f"Available weapon models: {len(available_weapons)}")
print(f"Available wing models: {len(available_wings)}")

SUBTYPE_MALE_FALLBACKS = {
    100: "equip_mc1_000001",
    101: "equip_mc1_000001",
    102: "equip_mc2_000001",
    103: "equip_mc4_000000",
    104: "equip_mc5_000001",
    105: "equip_mc6_000001",
}

SUBTYPE_FEMALE_FALLBACKS = {
    100: "equip_fc1_000001",
    101: "equip_fc1_000001",
    102: "equip_fc2_000001",
    103: "equip_fc4_000000",
    104: "equip_fc5_000001",
    105: "equip_fc6_000001",
}

# Load wings catalog
with open('web/assets/wings/catalog.json', 'r', encoding='utf-8') as f:
    wings_catalog = json.load(f)

catalog['wings'] = wings_catalog

mapped_weapons = 0
mapped_wings = 0

for item in catalog.get('items', []):
    eid = item['id']
    raw = equipt_map.get(eid)
    if not raw:
        continue

    # 1. Male & Female Weapon Mapping
    rcm = raw.get('res_code_male')
    rcf = raw.get('res_code_female')
    rc = raw.get('res_code')

    # Male
    val_m = rcm if (rcm and rcm != '0') else (rc if (rc and rc != '0') else None)
    if val_m:
        code_m = int(float(val_m))
        rel_m = get_url(code_m)
        m_name = os.path.splitext(os.path.basename(rel_m))[0].lower()
        if m_name in available_weapons:
            item['active_weapon_model'] = m_name
            mapped_weapons += 1
        elif item.get('category_group') == 'weapons':
            item['active_weapon_model'] = SUBTYPE_MALE_FALLBACKS.get(item.get('subtype'), "equip_mc1_000001")
    elif item.get('category_group') == 'weapons':
        item['active_weapon_model'] = SUBTYPE_MALE_FALLBACKS.get(item.get('subtype'), "equip_mc1_000001")

    # Female
    val_f = rcf if (rcf and rcf != '0') else (rc if (rc and rc != '0') else None)
    if val_f:
        code_f = int(float(val_f))
        rel_f = get_url(code_f)
        f_name = os.path.splitext(os.path.basename(rel_f))[0].lower()
        if f_name in available_weapons:
            item['active_female_weapon_model'] = f_name
        elif item.get('category_group') == 'weapons':
            item['active_female_weapon_model'] = SUBTYPE_FEMALE_FALLBACKS.get(item.get('subtype'), "equip_fc1_000001")
    elif item.get('category_group') == 'weapons':
        item['active_female_weapon_model'] = SUBTYPE_FEMALE_FALLBACKS.get(item.get('subtype'), "equip_fc1_000001")

    # 2. Wings Mapping
    if item.get('position') == 22 or 'cánh' in item.get('name', '').lower():
        item['category_group'] = 'wings'
        v_wing = rc or rcm or rcf
        if v_wing and v_wing != '0':
            c_wing = int(float(v_wing))
            rel_w = get_url(c_wing)
            w_name = os.path.splitext(os.path.basename(rel_w))[0].lower()
            if w_name in available_wings:
                item['active_wing_model'] = w_name
                item['has_converted_model'] = True
                mapped_wings += 1
            else:
                item['active_wing_model'] = 'equip_wing_001001'
        else:
            item['active_wing_model'] = 'equip_wing_001001'

with open('web/assets/equipment/catalog.json', 'w', encoding='utf-8') as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Catalog updated successfully!")
print(f"  * Mapped Weapons: {mapped_weapons}")
print(f"  * Mapped Wings: {mapped_wings}")
print(f"  * Total Wings in catalog: {len(catalog['wings'])}")
