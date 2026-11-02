import os, sys, json, time
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def generate_thumb_for_asset(asset_dir, target_size=(80, 80)):
    atlas_json_path = os.path.join(asset_dir, "atlas.json")
    atlas_webp_path = os.path.join(asset_dir, "atlas.webp")
    out_thumb_path = os.path.join(asset_dir, "thumb.webp")

    if not os.path.exists(atlas_json_path) or not os.path.exists(atlas_webp_path):
        return None

    try:
        with open(atlas_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        anims = data.get("animations", {})
        # Prefer direction 0 (down) or 2 (right)
        anim = anims.get("0-0") or anims.get("2-0") or anims.get("1-0") or (list(anims.values())[0] if anims else None)
        if not anim or not anim[0]:
            return None

        frame_key = anim[0]
        frame_info = data.get("frames", {}).get(frame_key)
        if not frame_info:
            return None

        rect = frame_info["frame"]
        x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]
        if w <= 0 or h <= 0:
            return None

        with Image.open(atlas_webp_path) as atlas:
            cropped = atlas.crop((x, y, x + w, y + h))

            scale = min(target_size[0] / max(w, 1), target_size[1] / max(h, 1), 1.0)
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))

            resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

            canvas = Image.new("RGBA", target_size, (0, 0, 0, 0))
            paste_x = (target_size[0] - new_w) // 2
            paste_y = target_size[1] - new_h - 2

            canvas.paste(resized, (paste_x, max(0, paste_y)), resized)
            canvas.save(out_thumb_path, "WEBP", quality=88)
            return out_thumb_path
    except Exception as e:
        return None

def process_all():
    print("="*60)
    print("🖼️ GERANDO MINIATURAS VISUAIS (THUMBNAILS) PARA TODOS OS ASSETS")
    print("="*60)

    start = time.time()

    # 1. Characters
    char_cat_path = "web/assets/characters/catalog.json"
    with open(char_cat_path, "r", encoding="utf-8") as f:
        char_cat = json.load(f)

    char_count = 0
    for c in char_cat.get("classes", []):
        cid = c["id"]
        cdir = os.path.join("web/assets/characters", cid)
        t = generate_thumb_for_asset(cdir)
        if t:
            c["thumb"] = f"assets/characters/{cid}/thumb.webp"
            char_count += 1

    with open(char_cat_path, "w", encoding="utf-8") as f:
        json.dump(char_cat, f, indent=2, ensure_ascii=False)
    print(f"✓ Miniaturas geradas para {char_count} classes/skins!")

    # 2. Monsters
    mon_cat_path = "web/assets/monsters/catalog.json"
    with open(mon_cat_path, "r", encoding="utf-8") as f:
        mon_cat = json.load(f)

    mon_count = 0
    for m in mon_cat.get("monsters", []):
        mid = m["id"]
        mdir = os.path.join("web/assets/monsters", mid)
        t = generate_thumb_for_asset(mdir)
        if t:
            m["thumb"] = f"assets/monsters/{mid}/thumb.webp"
            mon_count += 1

    # Also mushroom
    generate_thumb_for_asset("web/assets/monsters/mushroom")

    with open(mon_cat_path, "w", encoding="utf-8") as f:
        json.dump(mon_cat, f, indent=2, ensure_ascii=False)
    print(f"✓ Miniaturas geradas para {mon_count} monstros/pets!")

    elapsed = time.time() - start
    print(f"🎉 Concluído em {elapsed:.1f}s! Total de miniaturas: {char_count + mon_count}")

if __name__ == "__main__":
    process_all()
