import os, sys, hashlib

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
res_dir = os.path.join(ws, 'mcgame', 'frontend', 's', 'res')
res_files = set(os.listdir(res_dir))

def check_res(path):
    h = hashlib.md5(path.encode('utf-8')).hexdigest()
    if h in res_files:
        return (True, h, os.path.getsize(os.path.join(res_dir, h)))
    return (False, None, 0)

# 1. Inspect all wings
wings_found = []
# Check range for EQUIP_WING_ and EQUIP_FLY_
for prefix in ["equip/EQUIP_WING_", "equip/EQUIP_FLY_"]:
    for i in range(100000):
        # Format with 6 digits
        p = f"resource/{prefix}{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok:
            wings_found.append((p, h, sz, prefix, i))

print(f"Total Wings found in res: {len(wings_found)}")
for w in wings_found:
    print(f"  {w[0]} | size: {w[2]:,} bytes | hash: {w[1]}")

# 2. Inspect all FC weapons (Female Classes 1 to 6)
fc_weapons = []
for c in range(1, 7):
    for i in range(1000):
        p = f"resource/equip/EQUIP_FC{c}_{i:06d}.swf"
        ok, h, sz = check_res(p)
        if ok:
            fc_weapons.append((p, h, sz, c, i))

print(f"\nTotal FC Weapons found in res: {len(fc_weapons)}")
for c in range(1, 7):
    c_list = [w for w in fc_weapons if w[3] == c]
    print(f"  FC{c}: {len(c_list)} SWFs")
