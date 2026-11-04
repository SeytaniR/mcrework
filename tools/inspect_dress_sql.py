import os, sys, re, hashlib, json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
dress_sql = os.path.join(ws, 'mcgame', 'supabase', 'seeds', 'data_tbl_dress.sql')

with open(dress_sql, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("data_tbl_dress.sql sample (first 1000 chars):")
print(text[:1000])

rows = re.findall(r"\(([^;]+?)\)[,;]", text, re.DOTALL)
print(f"\nTotal rows in data_tbl_dress.sql: {len(rows)}")
for r in rows[:10]:
    print("  Row:", r.strip()[:150])
