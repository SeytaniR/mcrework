import os, re, hashlib, json

print("=== INSPECTING MOUNT DRESS ===")
with open(r"mcgame/supabase/seeds/data_tbl_mount_dress.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
print(f"Total mount dress rows: {len(rows)}")
for r in rows[:15]:
    # parse fields
    fields = [x.strip() for x in r.split(',')]
    print(fields[:10])

print("\n=== INSPECTING CREATURE COLUMNS FOR PETS ===")
with open(r"mcgame/supabase/seeds/data_tbl_creature.sql", "r", encoding="utf-8", errors="ignore") as f:
    c_sql = f.read()

# Get header columns
header_match = re.search(r'INSERT INTO "data"\."data_tbl_creature" \((.*?)\) VALUES', c_sql, re.DOTALL)
if header_match:
    cols = [c.strip().strip('"') for c in header_match.group(1).split(',')]
    print("Creature columns count:", len(cols))
    print("Creature columns:", cols)
    # Check for pet or type columns
    pet_cols = [c for c in cols if 'pet' in c.lower() or 'type' in c.lower() or 'catch' in c.lower() or 'kind' in c.lower()]
    print("Potential pet/type columns:", pet_cols)
