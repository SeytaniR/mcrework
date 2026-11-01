import re, hashlib, os

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing = set(os.listdir(res_dir))

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\supabase\seeds\data_tbl_creature.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
creatures = []
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

    if len(fields) >= 38:
        cid = fields[0]
        name = fields[24].strip("'")
        res_code = fields[34]
        try:
            rc = int(res_code)
            ext_id = rc // 1000000000000
            rem = rc % 1000000000000
            w1_id = rem // 1000000000
            rem = rem % 1000000000
            w2_id = rem // 1000000
            num = rem % 1000000
            w1 = "NPC_" if w1_id == 60 else "PC_"
            w2_map = {70: "MALE_", 80: "FEMALE_", 90: "FUNC_", 100: "CRE_", 110: "WEAPON_", 160: "NPC_"}
            w2 = w2_map.get(w2_id, "CRE_")
            rel = f"creature/{w1}{w2}{num:06d}.swf"
            full_url = f"resource/{rel}"
            h = hashlib.md5(full_url.encode("utf-8")).hexdigest()
            ex = h in existing
            sz = os.path.getsize(os.path.join(res_dir, h)) if ex else 0
            clean_name = name.encode("ascii", errors="replace").decode()
            if ex and sz > 5000:
                creatures.append((cid, clean_name, name, rel, h, sz))
        except Exception:
            pass

print(f"Total creatures with existing SWF: {len(creatures)}")
for c in creatures[:25]:
    print(f"ID {c[0]:<4}: {c[1]:<25} | {c[3]} | {c[5]} bytes | {c[4]}")
