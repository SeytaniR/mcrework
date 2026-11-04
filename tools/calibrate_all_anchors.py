"""
Batch Anchor & Feet Calibration Tool (v2 - True Foot Stance)
Magic Campus Rework Engine
Calculates the exact ground pivot (anchor_y) for all characters, mounts, and monsters
based on the true front-facing resting foot stance (eliminating cape/weapon offsets)
so they stand naturally on the ground with their feet firmly planted on the floor/shadow.
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
            
            # 1. Prioridade máxima: Frames de repouso frontais (Ação 0, Direção 0: Sul / Frente)
            # Na direção 0, o personagem está ereto de frente para a câmera e as solas dos pés
            # tocam o solo sem interferência de espadas, cajados ou capas pendendo para baixo.
            d0_frames = atlas.get("animations", {}).get("0-0", [])
            
            bottoms = []
            if d0_frames:
                for f_name in d0_frames:
                    if f_name in atlas.get("frames", {}):
                        fd = atlas["frames"][f_name]["frame"]
                        cropped = img.crop((fd["x"], fd["y"], fd["x"] + fd["w"], fd["y"] + fd["h"]))
                        bb = cropped.getbbox()
                        if bb:
                            bottoms.append(bb[3])
                            
            # Se não houver 0-0, tenta direção 4 (costas) ou o menor bottom das direções de repouso
            if not bottoms:
                all_stand_bottoms = []
                for d in range(8):
                    for f_name in atlas.get("animations", {}).get(f"0-{d}", []):
                        if f_name in atlas.get("frames", {}):
                            fd = atlas["frames"][f_name]["frame"]
                            cropped = img.crop((fd["x"], fd["y"], fd["x"] + fd["w"], fd["y"] + fd["h"]))
                            bb = cropped.getbbox()
                            if bb:
                                all_stand_bottoms.append(bb[3])
                if all_stand_bottoms:
                    # Usa a média dos bottoms ou o valor central para não pegar pontas de capa
                    bottoms = [round(sum(all_stand_bottoms) / len(all_stand_bottoms))]
                    
            # Fallback para ação 2 (corrida) se não houver ação 0
            if not bottoms:
                for d in range(8):
                    for f_name in atlas.get("animations", {}).get(f"2-{d}", []):
                        if f_name in atlas.get("frames", {}):
                            fd = atlas["frames"][f_name]["frame"]
                            cropped = img.crop((fd["x"], fd["y"], fd["x"] + fd["w"], fd["y"] + fd["h"]))
                            bb = cropped.getbbox()
                            if bb:
                                bottoms.append(bb[3])
                                
            # Fallback final
            if not bottoms and atlas.get("frames"):
                f_name = list(atlas["frames"].keys())[0]
                fd = atlas["frames"][f_name]["frame"]
                cropped = img.crop((fd["x"], fd["y"], fd["x"] + fd["w"], fd["y"] + fd["h"]))
                bb = cropped.getbbox()
                if bb:
                    bottoms.append(bb[3])
                    
            if bottoms:
                # O pé real do personagem é a média dos frames de repouso da postura frontal
                feet_y = round(sum(bottoms) / len(bottoms))
                h = meta.get("height", 100)
                if h <= 0:
                    h = 100
                anchor_y = round(feet_y / h, 4)
                anchor_y = max(0.4, min(1.0, anchor_y))
                
                old_anchor = meta.get("anchor", [0.5, 1.0])
                old_feet = meta.get("feet_y", 0)
                meta["anchor"] = [0.5, anchor_y]
                meta["feet_y"] = feet_y
                
                with open(meta_p, "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2, ensure_ascii=False)
                    
                updated += 1
                if abs(old_anchor[1] - anchor_y) > 0.02:
                    print(f"[{item}] feet: {old_feet} -> {feet_y}px | anchor: {old_anchor[1]:.4f} -> {anchor_y:.4f} (baixou {round((old_anchor[1] - anchor_y)*h*0.7, 1)}px)")
        except Exception as e:
            print(f"Erro em {item}: {e}")
            
    print(f"Total {category_name}: {count} verificados, {updated} calibrados.")

def update_catalogs():
    BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets"
    
    # 1. Characters catalog
    chars_cat_p = os.path.join(BASE_DIR, "characters", "catalog.json")
    if os.path.exists(chars_cat_p):
        with open(chars_cat_p, "r", encoding="utf-8") as f:
            cat = json.load(f)
        for c in cat.get("classes", []):
            cid = c.get("id")
            meta_p = os.path.join(BASE_DIR, "characters", cid, "visual_meta.json")
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    m = json.load(mf)
                c["anchor"] = m.get("anchor", [0.5, 1.0])
                c["feet_y"] = m.get("feet_y")
        with open(chars_cat_p, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2, ensure_ascii=False)
        print("Catalogo de classes atualizado.")

    # 2. Mounts catalog
    mounts_cat_p = os.path.join(BASE_DIR, "mounts", "catalog.json")
    if os.path.exists(mounts_cat_p):
        with open(mounts_cat_p, "r", encoding="utf-8") as f:
            cat = json.load(f)
        for m_item in cat.get("mounts", []):
            mid = m_item.get("id")
            meta_p = os.path.join(BASE_DIR, "mounts", mid, "visual_meta.json")
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    m = json.load(mf)
                m_item["anchor"] = m.get("anchor", [0.5, 1.0])
                m_item["feet_y"] = m.get("feet_y")
        with open(mounts_cat_p, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2, ensure_ascii=False)
        print("Catalogo de montarias atualizado.")

    # 3. Monsters catalog
    mon_cat_p = os.path.join(BASE_DIR, "monsters", "catalog.json")
    if os.path.exists(mon_cat_p):
        with open(mon_cat_p, "r", encoding="utf-8") as f:
            cat = json.load(f)
        for m_item in cat.get("monsters", []):
            mid = m_item.get("id")
            if not mid: continue
            meta_p = os.path.join(BASE_DIR, "monsters", mid, "visual_meta.json")
            if os.path.exists(meta_p):
                with open(meta_p, "r", encoding="utf-8") as mf:
                    m = json.load(mf)
                m_item["anchor"] = m.get("anchor", [0.5, 1.0])
                m_item["feet_y"] = m.get("feet_y")
        with open(mon_cat_p, "w", encoding="utf-8") as f:
            json.dump(cat, f, indent=2, ensure_ascii=False)
        print("Catalogo de monstros atualizado.")

if __name__ == "__main__":
    BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets"
    calibrate_directory(os.path.join(BASE_DIR, "characters"), "Classes")
    calibrate_directory(os.path.join(BASE_DIR, "mounts"), "Montarias")
    calibrate_directory(os.path.join(BASE_DIR, "monsters"), "Monstros")
    update_catalogs()
    print("\nCalibração de solo concluída com sucesso para todas as entidades!")
