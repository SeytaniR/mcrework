import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
MAP_SQL = os.path.join(BASE_DIR, "mcgame", "supabase", "seeds", "data_tbl_map.sql")
PORTAL_SQL = os.path.join(BASE_DIR, "mcgame", "supabase", "seeds", "data_tbl_sceneitem_instance.sql")
MAPS_CAT = os.path.join(BASE_DIR, "web", "assets", "maps", "catalog.json")

with open(MAPS_CAT, "r", encoding="utf-8") as f:
    cat_maps = json.load(f)["maps"]

cat_by_name = {}
for m in cat_maps:
    cat_by_name[m["name"].strip()] = m["id"]
    # normalize common variants
    norm = m["name"].strip().lower()
    cat_by_name[norm] = m["id"]

print("Sample catalog map names:")
for m in cat_maps[:10]:
    print(f"  ID {m['id']}: '{m['name']}' (repr: {repr(m['name'])})")

# Read portals
with open(PORTAL_SQL, "r", encoding="utf-8", errors="ignore") as f:
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

unmatched = []
matched = []
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

    if len(fields) >= 15:
        try:
            tid = fields[14]
            target_name = fields[6]
            pos_map_id = int(fields[10])
            px = int(fields[12])
            py = int(fields[13])
            if tid == "38":
                t_id = cat_by_name.get(target_name.strip()) or cat_by_name.get(target_name.strip().lower())
                if not t_id:
                    unmatched.append((target_name, repr(target_name), pos_map_id, px, py))
                else:
                    matched.append((target_name, t_id, pos_map_id, px, py))
        except Exception:
            pass

print(f"\nMatched portals: {len(matched)}")
print(f"Unmatched portals: {len(unmatched)}")
if unmatched:
    print("Unmatched portal names:")
    for u in set(u[0] for u in unmatched):
        print(f"  '{u}' (repr: {repr(u)})")
