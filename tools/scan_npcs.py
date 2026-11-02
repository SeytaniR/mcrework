import os, sys, hashlib, re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

res_dir = r"mcgame/frontend/s/res"
files = set(os.listdir(res_dir))

# 1. Map data_tbl_npc.sql
npc_names_by_num = {}
with open(r"mcgame/supabase/seeds/data_tbl_npc.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
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
    if len(fields) >= 26:
        npc_id = fields[0]
        name = fields[14].strip("'")
        map_id = fields[17].strip("'") if len(fields) > 17 else ""
        res_code_str = fields[25].strip("'")
        try:
            rc = int(res_code_str)
            rem = rc % 1000000000000
            rem2 = rem % 1000000000
            num = rem2 % 1000000
            if num not in npc_names_by_num:
                npc_names_by_num[num] = []
            npc_names_by_num[num].append({"npc_id": npc_id, "name": name, "map_id": map_id})
        except Exception:
            pass

print(f"Unique NPC res numbers in DB: {len(npc_names_by_num)}")

# 2. Find all existing NPC_FUNC_*.swf in res/
existing_npcs = []
for num in range(200000):
    rel = f"creature/NPC_FUNC_{num:06d}.swf"
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    if h in files:
        db_entries = npc_names_by_num.get(num, [])
        primary_name = db_entries[0]["name"] if db_entries else f"NPC {num}"
        existing_npcs.append({
            "num": num,
            "rel": rel,
            "hash": h,
            "name": primary_name,
            "db_entries": db_entries
        })

print(f"Total existing NPC_FUNC SWFs found in res/: {len(existing_npcs)}")
for n in existing_npcs[:15]:
    print(f"  Num {n['num']:06d}: {n['name']} (entries: {len(n['db_entries'])})")
