import os, sys, hashlib, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append('tools')
from batch_repack_all_weapons import extract_optimized_weapon

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
test_out = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\tools\test_wing_out'

wing_hash = "cd8b971ccc23f34b1fadc4aafa7e449a"
swf_path = os.path.join(res_dir, wing_hash)

extract_optimized_weapon(swf_path, test_out, "assets/wings/equip_wing_001001")

manifest_path = os.path.join(test_out, 'char_manifest.json')
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)

print("Manifest animation keys:", len(manifest), list(manifest.keys())[:10])
for k in list(manifest.keys())[:3]:
    print(f"  Action {k}: {len(manifest[k])} frames -> e.g. {manifest[k][0]}")

bitmaps = [f for f in os.listdir(test_out) if f.endswith('.png')]
print(f"Saved unique bitmaps: {len(bitmaps)}")
