import os, sys, hashlib, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi')
from tools.extract_character import extract_character
from tools.inspect_equipment import get_url

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
out_base = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\weapons'
os.makedirs(out_base, exist_ok=True)

# Popular weapon models across classes
popular = [
    # Swords (MC4)
    "equip/EQUIP_MC4_000000.swf",
    "equip/EQUIP_MC4_000001.swf",
    "equip/EQUIP_MC4_000002.swf",
    "equip/EQUIP_MC4_000003.swf",
    "equip/EQUIP_MC4_000004.swf",
    "equip/EQUIP_MC4_000005.swf",
    "equip/EQUIP_MC4_000006.swf",
    # Staffs (MC2)
    "equip/EQUIP_MC2_000001.swf",
    "equip/EQUIP_MC2_000002.swf",
    "equip/EQUIP_MC2_000003.swf",
    "equip/EQUIP_MC2_000004.swf",
    # Rifles (MC5)
    "equip/EQUIP_MC5_000001.swf",
    "equip/EQUIP_MC5_000002.swf",
    "equip/EQUIP_MC5_000003.swf",
    # Alaúdes (MC6)
    "equip/EQUIP_MC6_000001.swf",
    "equip/EQUIP_MC6_000002.swf",
    # Bastões (MC3)
    "equip/EQUIP_MC3_000001.swf",
    "equip/EQUIP_MC3_000002.swf"
]

t0 = time.time()
extracted_count = 0

for rel in popular:
    weapon_id = os.path.splitext(os.path.basename(rel))[0].lower()
    dest_dir = os.path.join(out_base, weapon_id)
    manifest_p = os.path.join(dest_dir, 'char_manifest.json')
    if os.path.exists(manifest_p):
        print(f"Already extracted: {weapon_id}")
        continue

    h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
    swf_path = os.path.join(res_dir, h)
    if os.path.exists(swf_path):
        os.makedirs(dest_dir, exist_ok=True)
        print(f"Extracting {weapon_id}...")
        extract_character(swf_path, dest_dir)
        
        # Ensure file paths have assets/ prefix
        if os.path.exists(manifest_p):
            with open(manifest_p, 'r', encoding='utf-8') as f:
                m = json.load(f)
            changed = False
            for k, frames in m.items():
                for fr in frames:
                    if not fr['file'].startswith('assets/'):
                        fr['file'] = 'assets/' + fr['file']
                        changed = True
            if changed:
                with open(manifest_p, 'w', encoding='utf-8') as f:
                    json.dump(m, f, indent=2)
        extracted_count += 1

print(f"Finished: {extracted_count} additional weapons extracted in {time.time() - t0:.2f}s!")
