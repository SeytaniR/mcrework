import os, sys, re, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 1. Load data_tbl_creature.sql
with open(r"mcgame/supabase/seeds/data_tbl_creature.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

# 2. Load data_tbl_creature_handbook.sql
handbook_names = {}
handbook_relate = set()
with open(r"mcgame/supabase/seeds/data_tbl_creature_handbook.sql", "r", encoding="utf-8", errors="ignore") as f:
    hb_sql = f.read()
    hb_rows = re.findall(r"\(([^;]+?)\)[,;]", hb_sql, re.DOTALL)
    for r in hb_rows:
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
        if len(fields) >= 14:
            relate_id = fields[13].strip("'")
            hb_name = fields[9].strip("'") if len(fields) > 9 else ""
            desc = fields[6].strip("'") if len(fields) > 6 else ""
            if relate_id and relate_id != 'NULL':
                handbook_relate.add(relate_id)
                handbook_names[relate_id] = {"name": hb_name, "desc": desc}

print(f"Handbook relate IDs: {len(handbook_relate)}")

# Parse creatures
rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
pet_res_nums = {}
pet_db_ids = {}

for r in rows:
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
    if len(fields) >= 35:
        cid = fields[0]
        catchable = fields[14]
        name = fields[24].strip("'")
        rc_str = fields[34]
        try:
            rc = int(rc_str)
            rem = rc % 1000000000000
            w1_id = rem // 1000000000
            rem = rem % 1000000000
            w2_id = rem // 1000000
            num = rem % 1000000
            
            is_catchable = (catchable == "1")
            is_handbook = (cid in handbook_relate)
            
            if is_catchable or is_handbook:
                pet_info = {
                    "is_pet": True,
                    "catchable": is_catchable,
                    "in_handbook": is_handbook,
                    "db_name": name,
                    "desc": handbook_names.get(cid, {}).get("desc", "")
                }
                pet_res_nums[num] = pet_info
                pet_db_ids[cid] = pet_info
        except Exception:
            pass

print(f"Total unique pet res numbers: {len(pet_res_nums)}")

# 3. Update web/assets/monsters/catalog.json
catalog_path = r"web/assets/monsters/catalog.json"
with open(catalog_path, "r", encoding="utf-8") as f:
    data = json.load(f)

pet_count = 0
monster_count = 0
for item in data.get("monsters", []):
    res_num = item.get("res_code_num")
    db_id = item.get("db_id")
    pinfo = None
    if res_num in pet_res_nums:
        pinfo = pet_res_nums[res_num]
    elif db_id in pet_db_ids:
        pinfo = pet_db_ids[db_id]
        
    if pinfo:
        item["is_pet"] = True
        item["category"] = "pet"
        item["catchable"] = pinfo["catchable"]
        item["in_handbook"] = pinfo["in_handbook"]
        if pinfo["desc"]:
            item["desc"] = pinfo["desc"]
        if pinfo.get("db_name") and not item.get("real_name"):
            item["real_name"] = pinfo["db_name"]
        pet_count += 1
    else:
        item["is_pet"] = False
        item["category"] = "monster"
        item["catchable"] = False
        monster_count += 1

data["total_pets"] = pet_count
data["total_wild_monsters"] = monster_count

with open(catalog_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated catalog: {pet_count} Pets tagged, {monster_count} Wild Monsters tagged.")
