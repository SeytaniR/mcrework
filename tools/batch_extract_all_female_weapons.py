import os, sys, hashlib, time, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi')
from tools.extract_character import extract_character

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
out_base = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\weapons'
os.makedirs(out_base, exist_ok=True)

all_swfs = []
for c in ['FC1', 'FC2', 'FC3', 'FC4', 'FC5', 'FC6']:
    for i in range(0, 25):
        rel = f"equip/EQUIP_{c}_{str(i).zfill(6)}.swf"
        h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
        if os.path.exists(os.path.join(res_dir, h)):
            all_swfs.append((c, i, rel, h))

print(f"Total existing female weapon SWFs to verify/extract: {len(all_swfs)}")

t0 = time.time()
extracted_count = 0
skipped_count = 0

for c, num, rel, h in all_swfs:
    weapon_id = os.path.splitext(os.path.basename(rel))[0].lower()
    dest_dir = os.path.join(out_base, weapon_id)
    manifest_p = os.path.join(dest_dir, 'char_manifest.json')
    if os.path.exists(manifest_p):
        skipped_count += 1
        continue

    swf_path = os.path.join(res_dir, h)
    os.makedirs(dest_dir, exist_ok=True)
    try:
        extract_character(swf_path, dest_dir)
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
        if extracted_count % 10 == 0:
            print(f"Progresso: {extracted_count}/{len(all_swfs)} extraídas...")
    except Exception as e:
        print(f"Error extracting {weapon_id}: {e}")

t1 = time.time()
print(f"Concluído em {t1 - t0:.2f}s! Extraídas: {extracted_count}, Já existentes: {skipped_count}")
