import os, sys, hashlib, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi')
from tools.extract_character import extract_character
from tools.inspect_equipment import parse_sql_file, get_url

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
out_base = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\weapons'
os.makedirs(out_base, exist_ok=True)

# Test extracting the 16 MC1 weapons
mc1_swfs = [f"equip/EQUIP_MC1_{str(i).zfill(6)}.swf" for i in range(1, 17)]

t0 = time.time()
extracted_count = 0

for rel in mc1_swfs:
    h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
    swf_path = os.path.join(res_dir, h)
    if os.path.exists(swf_path):
        weapon_id = os.path.splitext(os.path.basename(rel))[0].lower() # e.g. equip_mc1_000001
        dest_dir = os.path.join(out_base, weapon_id)
        os.makedirs(dest_dir, exist_ok=True)
        print(f"Extracting {weapon_id}...")
        extract_character(swf_path, dest_dir)
        extracted_count += 1

print(f"Extracted {extracted_count} weapons in {time.time() - t0:.2f}s!")
