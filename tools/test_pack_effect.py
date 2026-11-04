import sys, os, json, glob
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

def pack_frames_to_atlas(frame_files, out_dir, effect_id, fps=24):
    os.makedirs(out_dir, exist_ok=True)
    if not frame_files:
        return False
    
    # Sort files numerically
    frame_files = sorted(frame_files, key=lambda f: int(os.path.splitext(os.path.basename(f))[0]))
    
    images = []
    bboxes = []
    for f in frame_files:
        im = Image.open(f).convert('RGBA')
        images.append(im)
        bboxes.append(im.getbbox())
    
    # Global bounding box across all frames
    valid_bboxes = [b for b in bboxes if b]
    if not valid_bboxes:
        return False
    
    g_minx = min(b[0] for b in valid_bboxes)
    g_miny = min(b[1] for b in valid_bboxes)
    g_maxx = max(b[2] for b in valid_bboxes)
    g_maxy = max(b[3] for b in valid_bboxes)
    
    crop_w = max(1, g_maxx - g_minx)
    crop_h = max(1, g_maxy - g_miny)
    
    # Pack into grid
    num_frames = len(images)
    import math
    cols = math.isqrt(num_frames)
    if cols * cols < num_frames:
        cols += 1
    rows = (num_frames + cols - 1) // cols
    
    pad = 2
    atlas_w = cols * (crop_w + pad) + pad
    atlas_h = rows * (crop_h + pad) + pad
    
    # Power of two or compact
    atlas_img = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))
    frames_dict = {}
    
    for idx, im in enumerate(images):
        col = idx % cols
        row = idx // cols
        x = pad + col * (crop_w + pad)
        y = pad + row * (crop_h + pad)
        
        # Crop region from source image
        cropped = im.crop((g_minx, g_miny, g_maxx, g_maxy))
        atlas_img.paste(cropped, (x, y))
        
        frame_name = f"{effect_id}_{idx:02d}"
        frames_dict[frame_name] = {
            "frame": {"x": x, "y": y, "w": crop_w, "h": crop_h},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": crop_w, "h": crop_h},
            "sourceSize": {"w": crop_w, "h": crop_h}
        }
    
    # Save atlas.webp
    atlas_path = os.path.join(out_dir, "atlas.webp")
    atlas_img.save(atlas_path, "WEBP", quality=90, method=6)
    
    # Save atlas.json
    atlas_json = {
        "frames": frames_dict,
        "animations": {
            "play": list(frames_dict.keys())
        },
        "meta": {
            "app": "MagicCampusEffectConverter",
            "version": "1.0",
            "image": "atlas.webp",
            "format": "RGBA8888",
            "size": {"w": atlas_w, "h": atlas_h},
            "scale": "1"
        }
    }
    with open(os.path.join(out_dir, "atlas.json"), "w", encoding="utf-8") as f_json:
        json.dump(atlas_json, f_json, indent=2)
        
    # Save visual_meta.json
    visual_meta = {
        "id": effect_id,
        "width": crop_w,
        "height": crop_h,
        "anchor_x": 0.5,
        "anchor_y": 0.5,
        "num_frames": num_frames,
        "fps": fps,
        "duration_ms": int((num_frames / fps) * 1000)
    }
    with open(os.path.join(out_dir, "visual_meta.json"), "w", encoding="utf-8") as f_meta:
        json.dump(visual_meta, f_meta, indent=2)
        
    print(f"Packaged effect {effect_id}: {num_frames} frames ({crop_w}x{crop_h}), atlas={atlas_w}x{atlas_h}, size={os.path.getsize(atlas_path)} bytes")
    return True

# Test with test_export_eff
test_files = glob.glob(r'tools/test_export_eff/sprites/DefineSprite_8_EFF_PLAYER_010008_fla.Timeline_1/*.png')
pack_frames_to_atlas(test_files, r'web/assets/effects/10008', '10008')
