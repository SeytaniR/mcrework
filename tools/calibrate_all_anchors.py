"""
Batch Anchor & Feet Calibration Tool
Magic Campus Rework Engine
Calculates the exact ground pivot (anchor_y) for all characters, mounts, and monsters
so they stand naturally on the ground with their feet touching the floor/shadow.
"""

import os, sys, json
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def calibrate_directory(base_dir, category_name):
    print(f"\n--- Calibrando {category_name} em {base_dir} ---")
    items = sorted(os.listdir(base_dir))
    count = 0
    updated = 0
    
    for item in items:
        item_dir = os.path.join(base_dir, item)
        if not os.path.isdir(item_dir):
            continue
            
        meta_p = os.path.join(item_dir, "visual_meta.json")
        atlas_p = os.path.join(item_dir, "atlas.json")
        webp_p = os.path.join(item_dir, "atlas.webp")
        
        if not (os.path.exists(meta_p) and os.path.exists(atlas_p) and os.path.exists(webp_p)):
            continue
            
        count += 1
        try:
            with open(meta_p, "r", encoding="utf-8") as f:
                meta = json.load(f)
            with open(atlas_p, "r", encoding="utf-8") as f:
                atlas = json.load(f)
            img = Image.open(webp_p)
            
            # 1. Obter frames de repouso (Ação 0: Stand / Respirando) em todas as direções
            stand_frames = set()
            for d in range(8):
                anim_key = f"0-{d}"
                for f_name in atlas.get("animations", {}).get(anim_key, []):
                    stand_frames.add(f_name)
                    
            # Se não houver 0-x, tentar ação 2 (corrida/caminhada)
            if not stand_frames:
                for d in range(8):
                    anim_key = f"2-{d}"
                    for f_name in atlas.get("animations", {}).get(anim_key, []):
                        stand_frames.add(f_name)
                        
            # Fallback para primeiro frame disponível
            if not stand_frames and atlas.get("frames"):
                stand_frames = [list(atlas["frames"].keys())[0]]
                
            bottoms = []
            for f_name in stand_frames:
                if f_name in atlas.get("frames", {}):
                    fd = atlas["frames"][f_name]["frame"]
                    cropped = img.crop((fd["x"], fd["y"], fd["x"] + fd["w"], fd["y"] + fd["h"]))
                    bb = cropped.getbbox()
                    if bb:
                        bottoms.append(bb[3])
                        
            if bottoms:
                mb = max(bottoms)
                h = meta.get("height", 100)
                if h <= 0:
                    h = 100
                anchor_y = round(mb / h, 4)
                anchor_y = max(0.5, min(1.0, anchor_y))
                
                old_anchor = meta.get("anchor", [0.5, 1.0])
                meta["anchor"] = [0.5, anchor_y]
                meta["feet_y"] = mb
                
                with open(meta_p, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2, ensure_ascii=False)
                    
                updated += 1
                if abs(old_anchor[1] - anchor_y) > 0.05:
                    print(f"[{item}] gap={h - mb}px | anchor: {old_anchor[1]:.4f} -> {anchor_y:.4f}")
        except Exception as e:
            print(f"Erro em {item}: {e}")
            
    print(f"Total {category_name}: {count} verificados, {updated} calibrados.")

def update_catalogs():
    # 1. Characters catalog
    chars_cat_p = "C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/characters/catalog.json"
    if os.path.exists(chars_cat_p):
        with open(chars_cat_p, "r", encoding="utf-8") as f:
            cat = json.load(f)
        for c in cat.get("classes", []):
            cid = c.get("id")
            meta_p = f"C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/characters/{cid}/visual_meta.json"
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    m = json.load(mf)
                c["anchor"] = m.get("anchor", [0.5, 1.0])
        with open(chars_cat_p, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2, ensure_ascii=False)
        print("Catalogo de classes atualizado com novos anchors.")

    # 2. Mounts catalog
    mounts_cat_p = "C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/mounts/catalog.json"
    if os.path.exists(mounts_cat_p):
        with open(mounts_cat_p, "r", encoding="utf-8") as f:
            cat = json.load(f)
        for m in cat.get("mounts", []):
            mid = m.get("id")
            meta_p = f"C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/mounts/{mid}/visual_meta.json"
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
                m["anchor"] = meta.get("anchor", [0.5, 1.0])
        with open(mounts_cat_p, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2, ensure_ascii=False)
        print("Catalogo de montarias atualizado com novos anchors.")

    # 3. Monsters catalog
    mon_cat_p = "C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/monsters/catalog.json"
    if os.path.exists(mon_cat_p):
        with open(mon_cat_p, "r", encoding="utf-8") as f:
            cat = json.load(f)
        for m in cat.get("monsters", []):
            mid = m.get("id")
            meta_p = f"C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/monsters/{mid}/visual_meta.json"
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
                m["anchor"] = meta.get("anchor", [0.5, 1.0])
        with open(mon_cat_p, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2, ensure_ascii=False)
        print("Catalogo de monstros atualizado com novos anchors.")

if __name__ == "__main__":
    calibrate_directory("C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/characters", "Classes")
    calibrate_directory("C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/mounts", "Montarias")
    calibrate_directory("C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/assets/monsters", "Monstros")
    update_catalogs()
    print("\nCalibração concluída com sucesso!")
