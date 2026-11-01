import re, json, csv, io

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\supabase\seeds\data_tbl_npc.sql", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

header_match = re.search(r'INSERT INTO "data"\."data_tbl_npc" \((.*?)\) VALUES', text, re.DOTALL)
cols = [c.strip().strip('"') for c in header_match.group(1).split(",")]

map_idx = cols.index("pos_map_id")
x_idx = cols.index("pos_x")
y_idx = cols.index("pos_y")
name_idx = cols.index("name")
id_idx = cols.index("id")

values_part = text[header_match.end():]
rows = []

for match in re.finditer(r"\((.+?)\)(?:,\n|;\n|$)", values_part, re.DOTALL):
    row_str = match.group(1)
    reader = csv.reader(io.StringIO(row_str), delimiter=',', quotechar="'", skipinitialspace=True)
    try:
        parts = next(reader)
        if len(parts) >= len(cols) and parts[map_idx] == "1":
            rows.append({
                "id": parts[id_idx],
                "name": parts[name_idx],
                "x": int(parts[x_idx]),
                "y": int(parts[y_idx])
            })
    except Exception:
        pass

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\npcs.json", "w", encoding="utf-8") as out:
    json.dump(rows, out, indent=2, ensure_ascii=False)

print(f"Total NPCs saved for Map 1: {len(rows)}")
