import os, sys, hashlib, re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
res_dir = os.path.join(ws, 'mcgame', 'frontend', 's', 'res')
res_files = set(os.listdir(res_dir))

def check_res(path):
    h = hashlib.md5(path.encode('utf-8')).hexdigest()
    if h in res_files:
        return (True, h, os.path.getsize(os.path.join(res_dir, h)))
    return (False, None, 0)

# 1. PC Avatars (Personagens Jogáveis Masculinos e Femininos)
pc_male = []
pc_female = []
for i in range(100):
    p_m = f"resource/creature/PC_MALE_{i:06d}.swf"
    p_f = f"resource/creature/PC_FEMALE_{i:06d}.swf"
    ok, h, sz = check_res(p_m)
    if ok: pc_male.append((p_m, sz))
    ok, h, sz = check_res(p_f)
    if ok: pc_female.append((p_f, sz))

# 2. Creature / Monster Models (NPC_CRE_*)
creatures = []
for i in range(5000):
    p = f"resource/creature/NPC_CRE_{i:06d}.swf"
    ok, h, sz = check_res(p)
    if ok: creatures.append((p, sz))

# 3. Mount Models (Montarias - como são chamados em creature/?)
mounts = []
for prefix in ["MOUNT_", "MOUNT_FLY_", "PET_MOUNT_", "NPC_MOUNT_", "FLY_", "NPC_FLY_"]:
    for i in range(500):
        p = f"resource/creature/{prefix}{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok: mounts.append((p, sz))

# 4. Asas (Wings / Fly Wings)
wings = []
for prefix in ["EQUIP_WING_", "EQUIP_FLY_"]:
    for i in range(100000):
        # Sample common numbers
        pass

# 5. Efeitos Visuais / VFX (EFFECT_*)
effects = []
for prefix in ["EFFECT_", "EFF_", "SKILL_"]:
    for i in range(2000):
        p = f"resource/effect/{prefix}{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok: effects.append((p, sz))

# 6. Item Templates Icons (Poções, Consumíveis, Minérios, etc.)
item_icons = []
with open("mcgame/supabase/seeds/data_tbl_item_template.sql", "r", encoding="utf-8", errors="ignore") as f:
    item_sql = f.read()

# Pattern for icon_code
matches = set(re.findall(r"40702\d{8}", item_sql))
for code_str in matches:
    # get_url for icon: icon/item/ITEM_NORMAL_...
    # Let's test standard icon patterns
    pass

print(f"=== DETAILED ASSET SCAN RESULTS ===")
print(f"1. Personagens Jogáveis (PC Models):")
print(f"   * Masculinos (PC_MALE): {len(pc_male)} modelos SWF encontrados")
for m in pc_male[:6]: print(f"     - {m[0]} ({m[1]} bytes)")
print(f"   * Femininos (PC_FEMALE): {len(pc_female)} modelos SWF encontrados")
for f in pc_female[:6]: print(f"     - {f[0]} ({f[1]} bytes)")

print(f"\n2. Monstros e Mascotes (NPC_CRE_*): {len(creatures)} modelos SWF encontrados")
for c in creatures[:6]: print(f"   - {c[0]} ({c[1]} bytes)")

print(f"\n3. Montarias (Mounts em creature/): {len(mounts)} modelos SWF encontrados")
for m in mounts[:6]: print(f"   - {m[0]} ({m[1]} bytes)")

print(f"\n4. Efeitos Visuais & Habilidades (EFFECT_*): {len(effects)} modelos SWF encontrados")
for e in effects[:6]: print(f"   - {e[0]} ({e[1]} bytes)")
