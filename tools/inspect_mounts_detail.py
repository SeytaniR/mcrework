import os, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

for name in ['data_tbl_mount.sql', 'data_tbl_mount_dress.sql']:
    path = os.path.join('mcgame', 'supabase', 'seeds', name)
    if os.path.exists(path):
        print(f"\n=== {name} ===")
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        header = re.search(r'INSERT INTO [^(]+\(([^)]+)\)', text)
        if header:
            cols = [c.strip().strip('"') for c in header.group(1).split(',')]
            print("Columns:", cols)
            rows = re.findall(r"\(([^;]+?)\)[,;]", text, re.DOTALL)
            for r in rows[:10]:
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
                if len(fields) == len(cols):
                    d = dict(zip(cols, fields))
                    print(d)
                else:
                    print("Field count mismatch:", len(fields), "vs", len(cols), fields[:5])
