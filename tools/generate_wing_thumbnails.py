import os, json
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WINGS_DIR = os.path.join(BASE_DIR, "web", "assets", "wings")
WINGS_CATALOG = os.path.join(WINGS_DIR, "catalog.json")
EQUIP_CATALOG = os.path.join(BASE_DIR, "web", "assets", "equipment", "catalog.json")

print("1. Generating cropped thumbnails for all wings in:", WINGS_DIR)
generated_count = 0
for folder in sorted(os.listdir(WINGS_DIR)):
    folder_path = os.path.join(WINGS_DIR, folder)
    if not os.path.isdir(folder_path):
        continue

    # Look for bmp_1.png or first png
    png_path = os.path.join(folder_path, "bmp_1.png")
    if not os.path.exists(png_path):
        pngs = [f for f in os.listdir(folder_path) if f.endswith(".png") and f != "thumb.png"]
        if pngs:
            png_path = os.path.join(folder_path, pngs[0])
        else:
            print(f"  [WARN] No PNG found in {folder}")
            continue

    try:
        img = Image.open(png_path).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            cropped = img.crop(bbox)
        else:
            cropped = img

        # Target 120x120 canvas with padding
        target_size = (120, 120)
        thumb = Image.new("RGBA", target_size, (0, 0, 0, 0))

        # Scale down cropped while preserving aspect ratio
        w, h = cropped.size
        scale = min(110.0 / w, 110.0 / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

        pos_x = (target_size[0] - new_w) // 2
        pos_y = (target_size[1] - new_h) // 2
        thumb.paste(resized, (pos_x, pos_y), resized)

        thumb_out = os.path.join(folder_path, "thumb.png")
        thumb.save(thumb_out, "PNG", optimize=True)
        generated_count += 1
        print(f"  [OK] {folder} -> thumb.png ({new_w}x{new_h})")
    except Exception as e:
        print(f"  [ERROR] {folder}: {e}")

print(f"\nGenerated {generated_count} wing thumbnails.")

# 2. Update web/assets/wings/catalog.json
print("\n2. Updating wings/catalog.json...")
if os.path.exists(WINGS_CATALOG):
    with open(WINGS_CATALOG, "r", encoding="utf-8") as f:
        wings = json.load(f)

    for w in wings:
        mid = w.get("model_id", "").lower()
        thumb_rel = f"assets/wings/{mid}/thumb.png"
        w["icon"] = thumb_rel
        if "manifest_url" in w:
            w["manifest_url"] = w["manifest_url"].lower()

    with open(WINGS_CATALOG, "w", encoding="utf-8") as f:
        json.dump(wings, f, indent=2, ensure_ascii=False)
    print("  Updated wings/catalog.json successfully.")

# 3. Update web/assets/equipment/catalog.json
print("\n3. Updating equipment/catalog.json...")
if os.path.exists(EQUIP_CATALOG):
    with open(EQUIP_CATALOG, "r", encoding="utf-8") as f:
        eq = json.load(f)

    # Normalize icon paths to lowercase
    if "wings" in eq:
        for w in eq["wings"]:
            mid = w.get("model_id", "").lower()
            w["icon"] = f"assets/wings/{mid}/thumb.png"
            if "manifest_url" in w:
                w["manifest_url"] = w["manifest_url"].lower()

    if "items" in eq:
        for it in eq["items"]:
            if it.get("icon"):
                it["icon"] = it["icon"].lower()
            if (it.get("type") == "wing" or it.get("category_group") == "wings" or it.get("position") == 22) and it.get("model_id"):
                mid = it["model_id"].lower()
                thumb_path = os.path.join(WINGS_DIR, mid, "thumb.png")
                if os.path.exists(thumb_path):
                    it["icon"] = f"assets/wings/{mid}/thumb.png"

    with open(EQUIP_CATALOG, "w", encoding="utf-8") as f:
        json.dump(eq, f, indent=2, ensure_ascii=False)
    print("  Updated equipment/catalog.json successfully.")

print("\nDone!")
