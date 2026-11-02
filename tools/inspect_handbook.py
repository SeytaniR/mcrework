import os, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('mcgame/supabase/seeds/data_tbl_creature_handbook.sql', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

header = re.search(r'INSERT INTO [^(]+\(([^)]+)\)', text)
cols = [c.strip().strip('"') for c in header.group(1).split(',')]
print("Columns in data_tbl_creature_handbook:", cols)

# Parse rows considering quotes
rows = re.findall(r"\(([^;]+?)\)[,;]", text, re.DOTALL)
entries = []
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
    if len(fields) == len(cols):
        d = dict(zip(cols, fields))
        entries.append(d)

print(f"Parsed {len(entries)} handbook pets!")
for e in entries[:25]:
    print(f"ID {e['id']}: name={e.get('name')} | mid={e.get('mid')} | relate_id={e.get('relate_id')} | class_id={e.get('class_id')}")
