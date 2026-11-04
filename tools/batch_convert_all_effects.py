import sys, os, json, subprocess, shutil, glob, math, time, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

RES_DIR = 'mcgame/frontend/s/res'
OUT_EFFECTS_DIR = 'web/assets/effects'
os.makedirs(OUT_EFFECTS_DIR, exist_ok=True)
TMP_DIR = 'tools/tmp_effect_export'
os.makedirs(TMP_DIR, exist_ok=True)

with open('tools/found_effects.json', 'r', encoding='utf-8') as f:
    effects_map = json.load(f)

print(f"Total effects to process: {len(effects_map)}")

def pack_frames_to_atlas(frame_files, out_dir, effect_id, fps=24):
    os.makedirs(out_dir, exist_ok=True)
    if not frame_files:
        return None
    
    frame_files = sorted(frame_files, key=lambda f: int(os.path.splitext(os.path.basename(f))[0]))
    
    images = []
    bboxes = []
    for f in frame_files:
        try:
            im = Image.open(f).convert('RGBA')
            images.append(im)
            bboxes.append(im.getbbox())
        except Exception:
            pass
    
    if not images:
        return None
    
    valid_bboxes = [b for b in bboxes if b]
    if not valid_bboxes:
        sample = images[0]
        g_minx, g_miny, g_maxx, g_maxy = 0, 0, sample.width, sample.height
    else:
        g_minx = min(b[0] for b in valid_bboxes)
        g_miny = min(b[1] for b in valid_bboxes)
        g_maxx = max(b[2] for b in valid_bboxes)
        g_maxy = max(b[3] for b in valid_bboxes)
    
    crop_w = max(1, g_maxx - g_minx)
    crop_h = max(1, g_maxy - g_miny)
    
    num_frames = len(images)
    cols = math.isqrt(num_frames)
    if cols * cols < num_frames:
        cols += 1
    rows = (num_frames + cols - 1) // cols
    
    pad = 2
    atlas_w = cols * (crop_w + pad) + pad
    atlas_h = rows * (crop_h + pad) + pad
    
    atlas_img = Image.new('RGBA', (atlas_w, atlas_h), (0, 0, 0, 0))
    frames_dict = {}
    
    for idx, im in enumerate(images):
        col = idx % cols
        row = idx // cols
        x = pad + col * (crop_w + pad)
        y = pad + row * (crop_h + pad)
        
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
    
    atlas_path = os.path.join(out_dir, "atlas.webp")
    atlas_img.save(atlas_path, "WEBP", quality=90, method=6)
    
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
        
    return visual_meta

def process_single_effect(item):
    swf_path, swf_hash = item
    m = re.search(r'EFF_PLAYER_(\d+)\.swf', swf_path)
    if not m:
        return None
    num_str = str(int(m.group(1)))
    dest_dir = os.path.join(OUT_EFFECTS_DIR, num_str)
    
    # Check if already generated
    if os.path.exists(os.path.join(dest_dir, 'atlas.webp')) and os.path.exists(os.path.join(dest_dir, 'visual_meta.json')):
        try:
            with open(os.path.join(dest_dir, 'visual_meta.json'), 'r') as f_meta:
                meta = json.load(f_meta)
            return {
                "id": int(num_str),
                "num": num_str,
                "swf": os.path.basename(swf_path),
                "frames": meta["num_frames"],
                "width": meta["width"],
                "height": meta["height"],
                "duration_ms": meta["duration_ms"],
                "atlas": f"assets/effects/{num_str}/atlas.json"
            }
        except Exception:
            pass
            
    tmp_out = os.path.join(TMP_DIR, f"eff_{num_str}")
    if os.path.exists(tmp_out):
        shutil.rmtree(tmp_out, ignore_errors=True)
        
    cmd = [
        'java', '-jar', 'tools/ffdec/ffdec.jar',
        '-ignorebackground',
        '-format', 'sprite:png,frame:png',
        '-export', 'sprite,frame',
        tmp_out,
        os.path.join(RES_DIR, swf_hash)
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=40)
    except Exception as e:
        return None
        
    sprites_dir = os.path.join(tmp_out, 'sprites')
    frames_dir = os.path.join(tmp_out, 'frames')
    
    best_candidate_dir = None
    best_frame_count = 0
    
    if os.path.exists(sprites_dir):
        for s in os.listdir(sprites_dir):
            sp_path = os.path.join(sprites_dir, s)
            if os.path.isdir(sp_path):
                f_count = len(glob.glob(os.path.join(sp_path, '*.png')))
                if f_count > best_frame_count:
                    best_frame_count = f_count
                    best_candidate_dir = sp_path
                elif f_count == best_frame_count and best_candidate_dir:
                    if 'Timeline_1' in s:
                        best_candidate_dir = sp_path
    
    if os.path.exists(frames_dir):
        rf_count = len(glob.glob(os.path.join(frames_dir, '*.png')))
        if rf_count > best_frame_count:
            best_frame_count = rf_count
            best_candidate_dir = frames_dir
            
    result = None
    if best_candidate_dir and best_frame_count > 0:
        frame_files = glob.glob(os.path.join(best_candidate_dir, '*.png'))
        meta = pack_frames_to_atlas(frame_files, dest_dir, num_str)
        if meta:
            result = {
                "id": int(num_str),
                "num": num_str,
                "swf": os.path.basename(swf_path),
                "frames": meta["num_frames"],
                "width": meta["width"],
                "height": meta["height"],
                "duration_ms": meta["duration_ms"],
                "atlas": f"assets/effects/{num_str}/atlas.json"
            }
            
    if os.path.exists(tmp_out):
        shutil.rmtree(tmp_out, ignore_errors=True)
        
    return result

items = sorted(effects_map.items())
catalog = []
t0 = time.time()

print(f"Starting parallel conversion with 6 workers...")
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = {executor.submit(process_single_effect, item): item for item in items}
    done_count = 0
    for future in as_completed(futures):
        done_count += 1
        res = future.result()
        if res:
            catalog.append(res)
            print(f"[{done_count}/{len(items)}] Finished {res['swf']} -> {res['frames']} frames ({res['width']}x{res['height']})")
        else:
            item = futures[future]
            print(f"[{done_count}/{len(items)}] Skipped/no frames: {os.path.basename(item[0])}")

if os.path.exists(TMP_DIR):
    shutil.rmtree(TMP_DIR, ignore_errors=True)

catalog.sort(key=lambda x: x["id"])
catalog_path = os.path.join(OUT_EFFECTS_DIR, "catalog.json")
with open(catalog_path, "w", encoding="utf-8") as f_cat:
    json.dump(catalog, f_cat, indent=2)

print(f"\nAll done! Converted {len(catalog)} effects in {time.time() - t0:.1f}s.")
print(f"Catalog written to: {catalog_path}")
