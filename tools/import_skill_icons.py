import os, sys, hashlib, json, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
res_dir = 'mcgame/frontend/s/res'
all_res = set(os.listdir(res_dir))

out_dir = 'web/assets/skills/icons'
os.makedirs(out_dir, exist_ok=True)

# 1. Discover all skill icons
skill_icons_found = {}
for i in range(1, 10000):
    for pat in [f'icon/skill/SKILL_NORMAL_{i:06d}.png', f'icon/skill/SKILL_{i:06d}.png']:
        h = hashlib.md5(pat.encode('utf-8')).hexdigest()
        if h in all_res:
            src = os.path.join(res_dir, h)
            fname = f'skill_normal_{i:06d}.png'
            dst = os.path.join(out_dir, fname)
            if not os.path.exists(dst):
                shutil.copyfile(src, dst)
            skill_icons_found[i] = f'assets/skills/icons/{fname}'

print(f"Total de ícones de skills extraídos para {out_dir}: {len(skill_icons_found)}")

# 2. Update web/assets/skills/catalog.json
skills_cat_path = 'web/assets/skills/catalog.json'
with open(skills_cat_path, 'r', encoding='utf-8') as f:
    skills = json.load(f)

matched = 0
for sk in skills:
    # Try icon code if present, or sk['id']
    icon_code = sk.get('icon_code') or sk.get('id')
    # If icon_code is a big number like 4030200120001
    icon_num = None
    if isinstance(icon_code, int):
        icon_num = icon_code % 1000000
    elif isinstance(icon_code, str) and icon_code.isdigit():
        icon_num = int(icon_code) % 1000000
    
    if icon_num and icon_num in skill_icons_found:
        sk['icon_path'] = skill_icons_found[icon_num]
        matched += 1
    elif sk.get('id') in skill_icons_found:
        sk['icon_path'] = skill_icons_found[sk['id']]
        matched += 1

print(f"Habilidades no catálogo: {len(skills)}, com ícone associado: {matched}")

with open(skills_cat_path, 'w', encoding='utf-8') as f:
    json.dump(skills, f, indent=2, ensure_ascii=False)

print("web/assets/skills/catalog.json atualizado com sucesso!")
