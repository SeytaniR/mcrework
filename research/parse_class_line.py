with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\supabase\seeds\data_tbl_class.sql", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if "INSERT INTO" in l or (len(l) > 10 and l.strip().startswith("(1,")):
        print(f"Line {i+1}:")
        tokens = l.strip().split(",")
        for t_idx, t in enumerate(tokens):
            if any(k in t for k in ["res", "00", "Code", "code"]) or t_idx > len(tokens) - 10:
                print(f"  [{t_idx}] = {t.strip()}")
