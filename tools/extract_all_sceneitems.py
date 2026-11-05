import os, sys, hashlib, json, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi')
from tools.extract_character import extract_character

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
all_res = set(os.listdir(res_dir))

out_base = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\sceneitems'
os.makedirs(out_base, exist_ok=True)

scene_swfs = []
for i in range(1, 5000):
    for pat in [
        f'resource/item/SITEM_{i:06d}.swf',
        f'resource/item/SITEM_NORMAL_{i:06d}.swf',
        f'resource/item/SITEM_TREE_{i:06d}.swf',
        f'resource/item/SITEM_FLOWER_{i:06d}.swf',
        f'resource/item/SITEM_HOUSE_{i:06d}.swf',
        f'resource/item/SITEM_SPAWN_{i:06d}.swf'
    ]:
        h = hashlib.md5(pat.encode('utf-8')).hexdigest()
        if h in all_res:
            fname = os.path.splitext(os.path.basename(pat))[0].lower()
            scene_swfs.append((pat, h, fname))

print(f"Total de Scene Items encontrados: {len(scene_swfs)}")

catalog = []
for pat, h, name in scene_swfs:
    dest_dir = os.path.join(out_base, name)
    os.makedirs(dest_dir, exist_ok=True)
    swf_path = os.path.join(res_dir, h)
    
    # 1. Try extract_character (extracts lossless bitmaps and manifests)
    try:
        extract_character(swf_path, dest_dir)
    except Exception as e:
        pass
    
    # Check what images were extracted
    pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]
    
    # 2. If 0 images, use ffdec export image
    if len(pngs) == 0:
        cmd = f'java -jar tools/ffdec/ffdec.jar -export image "{dest_dir}" "{swf_path}"'
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        except Exception:
            pass
        pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]

    # 3. If still 0 images, use ffdec export frame
    if len(pngs) == 0:
        cmd = f'java -jar tools/ffdec/ffdec.jar -export frame png "{dest_dir}" "{swf_path}"'
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
        except Exception:
            pass
        pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]
    
    cat_type = 'tree' if 'tree' in name else (
        'flower' if 'flower' in name else (
            'house' if 'house' in name else (
                'spawn' if 'spawn' in name else 'chest_interactive'
            )
        )
    )
    
    catalog.append({
        "id": name,
        "name": name.replace('_', ' ').title(),
        "category": cat_type,
        "original_url": pat,
        "folder": f"assets/sceneitems/{name}",
        "total_frames": len(pngs),
        "frames": [f"assets/sceneitems/{name}/{p}" for p in sorted(pngs)]
    })

print(f"Concluída a extração de {len(catalog)} Scene Items!")
with open(os.path.join(out_base, 'sceneitems_catalog.json'), 'w', encoding='utf-8') as f:
    json.dump({"total_sceneitems": len(catalog), "sceneitems": catalog}, f, indent=2, ensure_ascii=False)

print(f"Salvo catálogo em {os.path.join(out_base, 'sceneitems_catalog.json')}!")
