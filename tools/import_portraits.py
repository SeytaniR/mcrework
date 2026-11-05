import os, sys, hashlib, json, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
res_dir = 'mcgame/frontend/s/res'
all_res = set(os.listdir(res_dir))

out_dir = 'web/assets/portraits'
os.makedirs(out_dir, exist_ok=True)

portraits = []
for i in range(1, 10000):
    for pat in [
        f'icon/creature/PC_MALE_{i:06d}.png',
        f'icon/creature/PC_FEMALE_{i:06d}.png',
        f'icon/creature/NPC_CRE_{i:06d}.png',
        f'icon/creature/NPC_FUNC_{i:06d}.png',
        f'icon/creature/NPC_{i:06d}.png'
    ]:
        h = hashlib.md5(pat.encode('utf-8')).hexdigest()
        if h in all_res:
            src = os.path.join(res_dir, h)
            fname = os.path.basename(pat).lower()
            dst = os.path.join(out_dir, fname)
            if not os.path.exists(dst):
                shutil.copyfile(src, dst)
            
            p_type = 'character_male' if 'pc_male' in fname else (
                'character_female' if 'pc_female' in fname else (
                    'monster_pet' if 'npc_cre' in fname else 'npc'
                )
            )
            portraits.append({
                "id": i,
                "filename": fname,
                "type": p_type,
                "path": f"assets/portraits/{fname}",
                "original_path": pat,
                "size_bytes": os.path.getsize(dst)
            })

print(f"Total de retratos/portraits extraídos para {out_dir}: {len(portraits)}")

catalog_data = {
    "version": "1.0.0",
    "total_portraits": len(portraits),
    "portraits": portraits
}

with open(os.path.join(out_dir, 'portraits_catalog.json'), 'w', encoding='utf-8') as f:
    json.dump(catalog_data, f, indent=2, ensure_ascii=False)

print(f"Salvo em {os.path.join(out_dir, 'portraits_catalog.json')}!")
