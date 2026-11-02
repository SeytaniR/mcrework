import os, sys, re, hashlib, json

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

res_dir = r"mcgame/frontend/s/res"
files = set(os.listdir(res_dir))

# 1. Analyze Pets in data_tbl_creature.sql
with open(r"mcgame/supabase/seeds/data_tbl_creature.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
catchable_pets = []
non_catchable_monsters = []

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
            w1 = "NPC_" if w1_id == 60 else "PC_"
            w2_map = {70: "MALE_", 80: "FEMALE_", 90: "FUNC_", 100: "CRE_", 110: "WEAPON_", 160: "NPC_"}
            w2 = w2_map.get(w2_id, "CRE_")
            rel = f"creature/{w1}{w2}{num:06d}.swf"
            h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
            if h in files:
                item = {
                    "db_id": cid,
                    "name": name,
                    "res_code_num": num,
                    "rel_path": rel,
                    "catchable": catchable == "1",
                    "hash": h
                }
                if catchable == "1":
                    catchable_pets.append(item)
                else:
                    non_catchable_monsters.append(item)
        except Exception:
            pass

print(f"Total Catchable Pets from DB: {len(catchable_pets)}")
print(f"Total Wild Monsters from DB: {len(non_catchable_monsters)}")
print("Sample Catchable Pets:")
for p in catchable_pets[:10]:
    print(f"  ID {p['db_id']}: {p['name']} (res {p['res_code_num']})")

# 2. Check Mounts
with open(r"mcgame/supabase/seeds/data_tbl_mount_dress.sql", "r", encoding="utf-8", errors="ignore") as f:
    md_sql = f.read()

md_rows = re.findall(r"\(([^;]+?)\)[,;]", md_sql, re.DOTALL)
mount_dresses = []
for r in md_rows:
    fields = [x.strip() for x in r.split(',')]
    if len(fields) >= 15:
        # fields: id, debuff_basic, debuff_per, description, effective_time, gold, icon_code, life_basic, life_per, mag_attack_basic, mag_attack_per, mag_defense_basic, mag_defense_per, name
        m_id = fields[0].strip("'")
        icon_code = fields[6].strip("'")
        name = fields[13].strip("'") if len(fields) > 13 else f"Mount {m_id}"
        mount_dresses.append((m_id, name, icon_code))

print(f"\nTotal Mount Dresses in DB: {len(mount_dresses)}")
for md in mount_dresses[:10]:
    print(f"  Mount ID {md[0]}: {md[1]} | icon_code={md[2]}")

# 3. Check NPCs
with open(r"mcgame/supabase/seeds/data_tbl_npc.sql", "r", encoding="utf-8", errors="ignore") as f:
    npc_sql = f.read()

npc_rows = re.findall(r"\(([^;]+?)\)[,;]", npc_sql, re.DOTALL)
npcs = {}
for r in npc_rows:
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
    if len(fields) >= 26:
        npc_id = fields[0]
        name = fields[14].strip("'")
        res_code_str = fields[25].strip("'")
        try:
            rc = int(res_code_str)
            rem = rc % 1000000000000
            w1_id = rem // 1000000000
            rem = rem % 1000000000
            w2_id = rem // 1000000
            num = rem % 1000000
            w1 = "NPC_" if w1_id == 60 else "PC_"
            w2_map = {70: "MALE_", 80: "FEMALE_", 90: "FUNC_", 100: "CRE_", 110: "WEAPON_", 160: "NPC_"}
            w2 = w2_map.get(w2_id, "FUNC_")
            rel = f"creature/{w1}{w2}{num:06d}.swf"
            h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
            if h in files and rel not in npcs:
                npcs[rel] = {
                    "npc_id": npc_id,
                    "name": name,
                    "num": num,
                    "rel_path": rel,
                    "hash": h
                }
        except Exception:
            pass

print(f"\nTotal Unique NPCs matched with existing SWF: {len(npcs)}")
for n in list(npcs.values())[:10]:
    print(f"  NPC {n['npc_id']}: {n['name']} ({n['rel_path']})")
