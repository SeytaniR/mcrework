import re, sys

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\supabase\seeds\data_tbl_class.sql", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Find all lines with values
for line in text.split("\n"):
    line = line.strip()
    if line.startswith("(") and line.endswith("),") or line.endswith(");"):
        # print sanitized ascii
        print(line.encode("ascii", "replace").decode("ascii")[:140])
