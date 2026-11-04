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

# 1. Mounts (Montarias)
mounts_found = []
for i in range(1000):
    for prefix in ["creature/MOUNT_", "creature/MOUNT_FLY_", "creature/PET_MOUNT_"]:
        p = f"resource/{prefix}{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok:
            mounts_found.append((p, sz, h))

# 2. Asas / Wings (Equip Wing)
wings_found = []
for i in range(10000):
    for prefix in ["equip/EQUIP_WING_", "equip/EQUIP_FLY_"]:
        p = f"resource/{prefix}{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok:
            wings_found.append((p, sz, h))

# 3. Trajes / Fashion / Outfits (Equip Dress)
dresses_found = []
for i in range(10000):
    for prefix in ["equip/EQUIP_DRESS_", "equip/EQUIP_CLOTH_", "creature/PC_DRESS_"]:
        p = f"resource/{prefix}{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok:
            dresses_found.append((p, sz, h))

# 4. Female Weapons (Armas Femininas)
female_weapons = []
for c in range(1, 7):
    for i in range(1000):
        p = f"resource/equip/EQUIP_FC{c}_{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok:
            female_weapons.append((p, sz, h))

# 5. Scene Items (Objetos Interativos de Mapa - Baús, Minérios, Portais, Flores)
scene_items = []
for i in range(10000):
    for ext in [".swf", ".png", ".jpg"]:
        for prefix in ["sceneitem/SITEM_", "sceneitem/SCENEITEM_"]:
            p = f"resource/{prefix}{i:06d}{ext}"
            ok, h, sz = check_res(p)
            if ok:
                scene_items.append((p, sz, h))

# 6. UI Assets (Telas, Janelas, Painéis, Molduras, World Maps)
ui_assets = []
for name in [
    "WorldMap1.jpg", "WorldMap2.jpg", "ChatPanel.swf", "MainUI.swf", "Backpack.swf", 
    "BattleUI.swf", "SkillPanel.swf", "PetPanel.swf", "EquipPanel.swf", "DialogPanel.swf"
]:
    p = f"resource/ui/{name}"
    ok, h, sz = check_res(p)
    if ok:
        ui_assets.append((p, sz, h))

# 7. Check items icons (data_tbl_item_template.sql)
item_icons = []
with open("mcgame/supabase/seeds/data_tbl_item_template.sql", "r", encoding="utf-8", errors="ignore") as f:
    item_sql = f.read()

# Match icon_code values
matches = set(re.findall(r"'(\d+)'", item_sql))
for val in matches:
    if len(val) >= 7 and val.startswith("407"):
        # Let's test URL
        # We know get_url logic
        pass

print(f"=== INVENTORY OF CANDIDATE ASSETS ===")
print(f"1. Montarias (Mounts / Fly Mounts): {len(mounts_found)} SWFs")
for m in mounts_found[:5]:
    print(f"   - {m[0]} ({m[1]} bytes)")

print(f"2. Asas Visuais (Wings): {len(wings_found)} SWFs")
for w in wings_found[:5]:
    print(f"   - {w[0]} ({w[1]} bytes)")

print(f"3. Armas Femininas (FC1 a FC6): {len(female_weapons)} SWFs")
for fw in female_weapons[:5]:
    print(f"   - {fw[0]} ({fw[1]} bytes)")

print(f"4. Objetos Interativos de Cenário (Scene Items): {len(scene_items)} assets")
for si in scene_items[:5]:
    print(f"   - {si[0]} ({si[1]} bytes)")

print(f"5. Trajes / Outfits Especiais: {len(dresses_found)} SWFs")
