import re

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\supabase\seeds\data_tbl_class.sql", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# The columns are:
# name, res_code_female, res_code_female2, res_code_male, res_code_male2
# Let's find all big numbers (13 digits):
for line in text.split("\n"):
    nums = re.findall(r"\b(1\d{12})\b", line)
    if nums:
        print("Found res_codes in line:", nums)
