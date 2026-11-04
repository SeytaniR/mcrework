import sys, os, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('mcgame/supabase/seeds/data_tbl_skill.sql', 'r', encoding='utf-8', errors='ignore') as f:
    sql = f.read()

m = re.search(r'INSERT INTO "data"\."data_tbl_skill"\s*\((.+?)\)\s*VALUES', sql)
if m:
    cols = [c.strip(' "') for c in m.group(1).split(',')]
    print(f'Columns ({len(cols)}):', cols)
else:
    print('No column header match')
    sys.exit(1)

# Split by rows
rows = re.findall(r'\(([^;]+?)\)[,;]', sql, re.DOTALL)
print('Total rows found:', len(rows))

def parse_row(r):
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
    return [f.strip("'") for f in fields]

parsed_samples = 0
unique_icon_codes = set()
unique_code_names = set()

for i, r in enumerate(rows):
    parsed = parse_row(r)
    if len(parsed) == len(cols):
        d = dict(zip(cols, parsed))
        icon = d.get('icon_code')
        cname = d.get('code_name')
        if icon:
            unique_icon_codes.add(icon)
        if cname:
            unique_code_names.add(cname)
        if parsed_samples < 15:
            print(f"ID={d.get('id'):<6} Name={d.get('name'):<16} Code={cname:<16} Icon={icon:<12} Kind={d.get('kind'):<4} Type={d.get('type'):<4} Level={d.get('level')}")
            parsed_samples += 1

print(f"\nTotal unique icon_codes: {len(unique_icon_codes)}")
print(f"Total unique code_names: {len(unique_code_names)}")
print("Sample icon codes:", list(unique_icon_codes)[:20])
print("Sample code names:", list(unique_code_names)[:20])
