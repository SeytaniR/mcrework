import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('mcgame/docs/client/config/Language.as', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

matches = re.findall(r'GAMEPREDEF_S\[(\d+)\]\s*=\s*"([^"]*)"', text)
lang_dict = {int(k): v for k, v in matches}

print("=== ITEM KINDS ===")
for idx in [167, 168, 169, 170, 171, 172, 173, 370, 383, 384, 390, 394, 459, 467]:
    print(f"GAMEPREDEF_S[{idx}]: {lang_dict.get(idx)}")

print("\n=== EQUIP POSITIONS ===")
for pos, s_idx in [(1,300), (2,301), (3,302), (4,303), (5,304), (6,305), (7,306), (8,307), (9,308), (10,309), (11,310), (12,311), (13,409), (14,383), (15,381), (21,390), (22,459)]:
    print(f"Position {pos} (S[{s_idx}]): {lang_dict.get(s_idx)}")

for pos, s_idx in [(50,371), (51,372), (52,373), (53,374), (54,375), (55,376), (56,377), (57,378)]:
    print(f"Pet Position {pos} (S[{s_idx}]): {lang_dict.get(s_idx)}")
