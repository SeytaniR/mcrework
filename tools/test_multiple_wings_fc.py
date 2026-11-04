import os, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from batch_repack_all_weapons import extract_optimized_weapon

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
res_files = set(os.listdir(res_dir))

test_wings = [
    "resource/equip/EQUIP_WING_005003.swf",
    "resource/equip/EQUIP_WING_061003.swf",
    "resource/equip/EQUIP_FLY_000004.swf",
    "resource/equip/EQUIP_FLY_000018.swf",
    "resource/equip/EQUIP_FC1_000001.swf",
    "resource/equip/EQUIP_FC4_000000.swf",
]

for p in test_wings:
    h = hashlib.md5(p.encode('utf-8')).hexdigest()
    if h in res_files:
        name = os.path.basename(p).replace('.swf', '').lower()
        out_dir = os.path.join(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\tools\test_pack', name)
        swf_path = os.path.join(res_dir, h)
        try:
            extract_optimized_weapon(swf_path, out_dir, f"assets/test/{name}")
            files = os.listdir(out_dir)
            print(f"Success for {name}: {len(files)} files created")
        except Exception as e:
            print(f"Error for {name}: {e}")
    else:
        print(f"Hash not found for {p}")
