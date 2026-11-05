import os, sys, hashlib, json, subprocess

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.path.append(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi')
from tools.extract_character import extract_character

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
all_res = set(os.listdir(res_dir))

out_em = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\emotions'
out_blt = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\bullets'
os.makedirs(out_em, exist_ok=True)
os.makedirs(out_blt, exist_ok=True)

# 1. EMOTIONS
emotions = []
for i in range(1, 100):
    for pat in [f'resource/emotion/EM_{i:06d}.swf', f'resource/emotion/EM_NORMAL_{i:06d}.swf']:
        h = hashlib.md5(pat.encode('utf-8')).hexdigest()
        if h in all_res:
            fname = os.path.splitext(os.path.basename(pat))[0].lower()
            emotions.append((pat, h, fname))

print(f"Total de Emotions encontradas: {len(emotions)}")
em_catalog = []
for pat, h, name in emotions:
    dest_dir = os.path.join(out_em, name)
    os.makedirs(dest_dir, exist_ok=True)
    swf_path = os.path.join(res_dir, h)
    
    # Try extract_character
    try:
        extract_character(swf_path, dest_dir)
    except:
        pass
    
    pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]
    if len(pngs) == 0:
        cmd = f'java -jar tools/ffdec/ffdec.jar -export image "{dest_dir}" "{swf_path}"'
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=8)
        except:
            pass
        pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]

    if len(pngs) == 0:
        cmd = f'java -jar tools/ffdec/ffdec.jar -export frame png "{dest_dir}" "{swf_path}"'
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=8)
        except:
            pass
        pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]

    em_catalog.append({
        "id": name,
        "name": name.replace('_', ' ').title(),
        "original_url": pat,
        "folder": f"assets/emotions/{name}",
        "total_frames": len(pngs),
        "frames": [f"assets/emotions/{name}/{p}" for p in sorted(pngs)]
    })

with open(os.path.join(out_em, 'emotions_catalog.json'), 'w', encoding='utf-8') as f:
    json.dump({"total_emotions": len(em_catalog), "emotions": em_catalog}, f, indent=2, ensure_ascii=False)
print("Emotions exportadas com sucesso!")

# 2. BULLETS
bullets = []
for i in range(1, 100):
    for pat in [f'resource/bullet/BLT_NORMAL_{i:06d}.swf', f'resource/bullet/BLT_{i:06d}.swf']:
        h = hashlib.md5(pat.encode('utf-8')).hexdigest()
        if h in all_res:
            fname = os.path.splitext(os.path.basename(pat))[0].lower()
            bullets.append((pat, h, fname))

print(f"Total de Bullets encontradas: {len(bullets)}")
blt_catalog = []
for pat, h, name in bullets:
    dest_dir = os.path.join(out_blt, name)
    os.makedirs(dest_dir, exist_ok=True)
    swf_path = os.path.join(res_dir, h)
    
    try:
        extract_character(swf_path, dest_dir)
    except:
        pass
    
    pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]
    if len(pngs) == 0:
        cmd = f'java -jar tools/ffdec/ffdec.jar -export frame png "{dest_dir}" "{swf_path}"'
        try:
            subprocess.run(cmd, shell=True, capture_output=True, timeout=8)
        except:
            pass
        pngs = [f for f in os.listdir(dest_dir) if f.endswith('.png')]

    blt_catalog.append({
        "id": name,
        "name": name.replace('_', ' ').title(),
        "original_url": pat,
        "folder": f"assets/bullets/{name}",
        "total_frames": len(pngs),
        "frames": [f"assets/bullets/{name}/{p}" for p in sorted(pngs)]
    })

with open(os.path.join(out_blt, 'bullets_catalog.json'), 'w', encoding='utf-8') as f:
    json.dump({"total_bullets": len(blt_catalog), "bullets": blt_catalog}, f, indent=2, ensure_ascii=False)
print("Bullets exportadas com sucesso!")
