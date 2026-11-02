import os, sys, hashlib, json
from PIL import Image
from batch_extract_assets import parse_swf, pack_atlas

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

res_dir = r"mcgame/frontend/s/res"
out_dir = r"web/assets/npcs/npc_000001"

rel = "creature/NPC_FUNC_000001.swf"
h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
path = os.path.join(res_dir, h)

print(f"Testing NPC extraction for {rel} (hash={h})...")
bitmaps, anim_frames = parse_swf(path)
print(f"Found {len(bitmaps)} bitmaps, {len(anim_frames)} anim labels")

extra_meta = {
    "name": "Sứ Giả Long Tộc",
    "res_path": rel,
    "res_code_num": 1,
    "type": "npc"
}

pack_atlas(bitmaps, anim_frames, out_dir, model_name="npc_000001", extra_meta=extra_meta)
print("Packing completed!")

# Also generate thumb.webp
first_bmp = list(bitmaps.values())[0]
thumb = first_bmp.copy()
thumb.thumbnail((80, 80), Image.Resampling.LANCZOS)
thumb.save(os.path.join(out_dir, "thumb.webp"), "WEBP", quality=85)
print(f"Thumb saved to {out_dir}/thumb.webp")
