import os, json
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EFFECTS_DIR = os.path.join(BASE_DIR, "web", "assets", "effects")
CATALOG_PATH = os.path.join(EFFECTS_DIR, "catalog.json")

print("Generating thumbnails for VFX effects...")
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    effects = json.load(f)

success_count = 0
for eff in effects:
    eid = str(eff["id"])
    eff_dir = os.path.join(EFFECTS_DIR, eid)
    atlas_json_path = os.path.join(eff_dir, "atlas.json")
    atlas_img_path = os.path.join(eff_dir, "atlas.webp")

    if not (os.path.exists(atlas_json_path) and os.path.exists(atlas_img_path)):
        continue

    try:
        with open(atlas_json_path, "r", encoding="utf-8") as jf:
            atlas_data = json.load(jf)
        frames_dict = atlas_data.get("frames", {})
        if not frames_dict:
            continue

        atlas_img = Image.open(atlas_img_path).convert("RGBA")

        # Pick best frame: evaluate mid or max-content frame
        frame_keys = list(frames_dict.keys())
        # Inspect 3 candidates: 1/3, 1/2, 2/3 of anim
        candidates = [
            frame_keys[len(frame_keys) // 3],
            frame_keys[len(frame_keys) // 2],
            frame_keys[min(len(frame_keys) - 1, (len(frame_keys) * 2) // 3)]
        ]

        best_crop = None
        best_area = -1

        for c_key in candidates:
            f_info = frames_dict[c_key]["frame"]
            box = (f_info["x"], f_info["y"], f_info["x"] + f_info["w"], f_info["y"] + f_info["h"])
            sub = atlas_img.crop(box)
            bb = sub.getbbox()
            if bb:
                area = (bb[2] - bb[0]) * (bb[3] - bb[1])
                if area > best_area:
                    best_area = area
                    best_crop = sub.crop(bb)

        if not best_crop:
            # Fallback to first candidate
            f_info = frames_dict[frame_keys[0]]["frame"]
            box = (f_info["x"], f_info["y"], f_info["x"] + f_info["w"], f_info["y"] + f_info["h"])
            best_crop = atlas_img.crop(box)

        # Target thumbnail: 90x90 canvas
        target_size = (90, 90)
        thumb = Image.new("RGBA", target_size, (0, 0, 0, 0))
        w, h = best_crop.size
        scale = min(82.0 / w, 82.0 / h)
        new_w = max(1, int(w * scale))
        new_h = max(1, int(h * scale))
        resized = best_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)

        pos_x = (target_size[0] - new_w) // 2
        pos_y = (target_size[1] - new_h) // 2
        thumb.paste(resized, (pos_x, pos_y), resized)

        out_thumb = os.path.join(eff_dir, "thumb.png")
        thumb.save(out_thumb, "PNG", optimize=True)

        eff["thumb"] = f"assets/effects/{eid}/thumb.png"
        success_count += 1
    except Exception as e:
        print(f"Error on effect {eid}: {e}")

with open(CATALOG_PATH, "w", encoding="utf-8") as f:
    json.dump(effects, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {success_count} / {len(effects)} VFX effect thumbnails!")
