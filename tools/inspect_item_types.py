import sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('mcgame/docs/client/predef/GamePredef.as', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

types = re.findall(r'public static const (ITEM_TYPE_\w+):int\s*=\s*(\d+);', text)
type_map = {int(v): k for k, v in types}

# also find Language mapping for item types if any
name_matches = re.findall(r'ITEM_TYPE_NAME\[(ITEM_TYPE_\w+)\]\s*=\s*Language\.GAMEPREDEF_S\[(\d+)\];', text)
print(f"Total ITEM_TYPE constants: {len(types)}")
for k, s_idx in name_matches:
    print(f"{k} -> S[{s_idx}]")

with open('mcgame/docs/client/config/Language.as', 'r', encoding='utf-8', errors='ignore') as f:
    lang_text = f.read()
matches = re.findall(r'GAMEPREDEF_S\[(\d+)\]\s*=\s*"([^"]*)"', lang_text)
lang_dict = {int(k): v for k, v in matches}

print("\nResolved Weapon & Equipment Subtypes:")
for k, s_idx in name_matches:
    print(f"  {k} = {lang_dict.get(int(s_idx))}")
