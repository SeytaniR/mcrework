import os, sys, hashlib, json, re, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
res_dir = 'mcgame/frontend/s/res'
all_res = set(os.listdir(res_dir))

out_dir = 'web/assets/items'
icons_out_dir = os.path.join(out_dir, 'icons')
os.makedirs(icons_out_dir, exist_ok=True)

# 1. Discover and extract all 1,695 item icons
extracted_icons = 0
icon_map = {}
for i in range(1, 300000):
    p = f'icon/item/ITEM_NORMAL_{i:06d}.png'
    h = hashlib.md5(p.encode('utf-8')).hexdigest()
    if h in all_res:
        src = os.path.join(res_dir, h)
        dst_name = f'item_normal_{i:06d}.png'
        dst = os.path.join(icons_out_dir, dst_name)
        if not os.path.exists(dst):
            shutil.copyfile(src, dst)
        extracted_icons += 1
        icon_map[i] = f'assets/items/icons/{dst_name}'

print(f"Total de ícones extraídos para {icons_out_dir}: {extracted_icons}")

# 2. Parse data_tbl_item_template.sql
with open('mcgame/supabase/seeds/data_tbl_item_template.sql', 'r', encoding='utf-8', errors='ignore') as f:
    sql = f.read()

val_pos = sql.find("VALUES")
values_str = sql[val_pos + 6:]
rows = []
cur_row = []
in_paren = False
in_quote = False
i = 0
while i < len(values_str):
    c = values_str[i]
    if not in_quote:
        if c == "'":
            in_quote = True
            cur_row.append(c)
        elif c == '(':
            in_paren = True
            cur_row = []
        elif c == ')':
            in_paren = False
            rows.append("".join(cur_row))
            cur_row = []
        elif in_paren:
            cur_row.append(c)
    else:
        if c == "'":
            if i + 1 < len(values_str) and values_str[i+1] == "'":
                cur_row.append("''")
                i += 1
            else:
                in_quote = False
                cur_row.append(c)
        else:
            cur_row.append(c)
    i += 1

print(f"Total de registros lidos do SQL: {len(rows)}")

# Classification rules based on kind, type, and name keywords
categories = {
    'potions': 0,
    'books': 0,
    'materials': 0,
    'gems': 0,
    'scrolls': 0,
    'quest': 0,
    'other': 0
}

items_list = []
rarity_names = {
    -1: 'Comum (Cinza)',
    0: 'Normal (Branco)',
    1: 'Incomum (Verde)',
    2: 'Raro (Azul)',
    3: 'Épico (Roxo)',
    4: 'Lendário (Dourado)',
    5: 'Mítico (Laranja)'
}

for r in rows:
    fields = []
    cur_fld = []
    in_q = False
    j = 0
    while j < len(r):
        ch = r[j]
        if not in_q:
            if ch == "'": in_q = True
            elif ch == ',':
                fields.append("".join(cur_fld).strip())
                cur_fld = []
            else: cur_fld.append(ch)
        else:
            if ch == "'":
                if j + 1 < len(r) and r[j+1] == "'":
                    cur_fld.append("'")
                    j += 1
                else: in_q = False
            else: cur_fld.append(ch)
        j += 1
    fields.append("".join(cur_fld).strip())

    if len(fields) >= 30:
        try:
            item_id = int(fields[0])
            name = fields[20].strip("'")
            desc = fields[4].strip("'")
            info = fields[11].strip("'") if fields[11] != 'NULL' else ""
            color = int(fields[2]) if fields[2].isdigit() or (fields[2].startswith('-') and fields[2][1:].isdigit()) else 0
            kind = int(fields[14]) if fields[14].isdigit() else 0
            level = int(fields[15]) if fields[15].isdigit() else 0
            price = int(fields[22]) if fields[22].isdigit() else 0
            gold = int(fields[5]) if fields[5].isdigit() else 0
            stack_max = int(fields[30]) if fields[30].isdigit() else 1
            type_val = int(fields[33]) if len(fields) > 33 and fields[33].isdigit() else 0
            use_type = int(fields[34]) if len(fields) > 34 and fields[34].isdigit() else 0
            
            icon_code_raw = fields[10].strip()
            icon_num = None
            if icon_code_raw and icon_code_raw != 'NULL':
                try:
                    code_val = int(icon_code_raw)
                    icon_num = code_val % 1000000
                except:
                    pass
            
            has_icon = icon_num in icon_map if icon_num else False
            icon_rel_path = icon_map.get(icon_num)
            
            # Categorize
            cat = 'other'
            lower_name = name.lower()
            lower_desc = desc.lower()
            lower_info = info.lower()
            
            if 'sách' in lower_name or 'bí tịch' in lower_name or 'tịch' in lower_name or 'skill' in lower_name or kind == 505:
                cat = 'books'
            elif 'thuốc' in lower_name or 'đơn' in lower_name or 'hoàn' in lower_name or 'hp' in lower_info or 'mp' in lower_info or 'sinh mệnh' in lower_name or 'ma pháp' in lower_name or kind == 501:
                cat = 'potions'
            elif 'ngọc' in lower_name or 'đá' in lower_name or 'bảo thạch' in lower_name or 'kim cương' in lower_name:
                cat = 'gems'
            elif 'phù' in lower_name or 'cuộn' in lower_name or 'truyền tống' in lower_name or 'lệnh' in lower_name:
                cat = 'scrolls'
            elif 'nhiệm vụ' in lower_desc or 'nhiệm vụ' in lower_name or 'quest' in lower_name:
                cat = 'quest'
            elif 'quặng' in lower_name or 'gỗ' in lower_name or 'da' in lower_name or 'vải' in lower_name or 'thảo' in lower_name or 'hoa' in lower_name or 'tơ' in lower_name or 'mảnh' in lower_name:
                cat = 'materials'
            
            categories[cat] += 1
            
            items_list.append({
                "id": item_id,
                "name": name,
                "description": desc,
                "info": info,
                "color": color,
                "rarity": rarity_names.get(color, f'Raridade {color}'),
                "kind": kind,
                "category": cat,
                "level": level,
                "price": price,
                "gold": gold,
                "stack_max": stack_max,
                "type": type_val,
                "use_type": use_type,
                "icon_id": icon_num,
                "icon_path": icon_rel_path
            })
        except Exception:
            pass

print(f"Total de itens estruturados no catálogo: {len(items_list)}")
print("Distribuição por categoria:")
for k, v in categories.items():
    print(f"  * {k}: {v} itens")

catalog_data = {
    "version": "1.0.0",
    "total_items": len(items_list),
    "total_icons_extracted": extracted_icons,
    "categories_count": categories,
    "items": items_list
}

with open(os.path.join(out_dir, 'items_catalog.json'), 'w', encoding='utf-8') as f_out:
    json.dump(catalog_data, f_out, indent=2, ensure_ascii=False)

print(f"Salvo em {os.path.join(out_dir, 'items_catalog.json')}!")
