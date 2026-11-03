import sys, re

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

with open("mcgame/supabase/seeds/data_tbl_map.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
for r in rows:
    if r.strip().startswith("1,"):
        print("Found row 1 len:", len(r))
        fields = []
        in_quote = False
        cur = []
        for c in r:
            if c == "'":
                in_quote = not in_quote
                cur.append(c)
            elif c == ',' and not in_quote:
                fields.append("".join(cur).strip())
                cur = []
            else:
                cur.append(c)
        fields.append("".join(cur).strip())
        print("Field count:", len(fields))
        for i, fld in enumerate(fields):
            print(f"  {i}: {fld[:40]}")
        break
