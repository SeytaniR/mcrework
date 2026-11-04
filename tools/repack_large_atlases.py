import os, sys, json, io
from PIL import Image

def repack_atlas(dir_path, max_dim=4096, pad=2):
    json_path = os.path.join(dir_path, "atlas.json")
    webp_path = os.path.join(dir_path, "atlas.webp")
    if not os.path.exists(json_path) or not os.path.exists(webp_path):
        return False, "Missing files"

    with open(json_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    with open(webp_path, 'rb') as f:
        img_bytes = f.read()

    atlas_img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")

    w_orig, h_orig = atlas_img.size
    if w_orig <= max_dim and h_orig <= max_dim:
        return True, "Already <= max_dim"

    print(f"Repacking {dir_path}: original size ({w_orig}, {h_orig}) -> target <= {max_dim}")

    # Extract cropped frames
    frames_dict = manifest.get('frames', {})
    cropped_frames = {}
    for name, f_info in frames_dict.items():
        fr = f_info['frame']
        fx, fy, fw, fh = fr['x'], fr['y'], fr['w'], fr['h']
        cropped = atlas_img.crop((fx, fy, fx + fw, fy + fh))
        cropped_frames[name] = cropped

    # Find optimal scale so that shelf packing fits in max_dim x max_dim
    best_scale = 1.0
    best_placements = None
    best_atlas_w = max_dim
    best_atlas_h = max_dim

    for scale in [1.0, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.50]:
        # Sort items by height descending
        items = []
        for name, img in cropped_frames.items():
            tw = max(1, int(img.width * scale))
            th = max(1, int(img.height * scale))
            items.append((name, tw, th))
        items.sort(key=lambda it: it[2], reverse=True)

        # Shelf packing
        cur_x = pad
        cur_y = pad
        row_h = 0
        placements = {}
        fits = True
        atlas_w = max_dim

        for name, w, h in items:
            if cur_x + w + pad > atlas_w:
                cur_x = pad
                cur_y += row_h + pad
                row_h = 0
            if cur_y + h + pad > max_dim:
                fits = False
                break
            placements[name] = (cur_x, cur_y, w, h)
            cur_x += w + pad
            row_h = max(row_h, h)

        if fits:
            total_h = cur_y + row_h + pad
            # find power of 2 for height
            final_h = 256
            while final_h < total_h and final_h <= max_dim:
                final_h *= 2
            if final_h <= max_dim:
                best_scale = scale
                best_placements = placements
                best_atlas_w = max_dim
                best_atlas_h = final_h
                break

    if not best_placements:
        return False, f"Could not fit even at 0.50 scale in {max_dim}x{max_dim}"

    print(f"  Selected scale: {best_scale:.2f}, new atlas size: ({best_atlas_w}, {best_atlas_h})")

    # Build new atlas image
    new_atlas = Image.new("RGBA", (best_atlas_w, best_atlas_h), (0, 0, 0, 0))
    new_frames_dict = {}

    for name, (x, y, w, h) in best_placements.items():
        orig_img = cropped_frames[name]
        if best_scale == 1.0:
            frame_img = orig_img
        else:
            frame_img = orig_img.resize((w, h), Image.Resampling.LANCZOS)
        new_atlas.paste(frame_img, (x, y))

        orig_f = frames_dict[name]
        orig_ss = orig_f.get('spriteSourceSize', {})
        orig_sz = orig_f.get('sourceSize', {})

        new_frames_dict[name] = {
            "frame": {"x": x, "y": y, "w": w, "h": h},
            "rotated": False,
            "trimmed": orig_f.get('trimmed', False),
            "spriteSourceSize": {
                "x": int(orig_ss.get('x', 0) * best_scale),
                "y": int(orig_ss.get('y', 0) * best_scale),
                "w": w,
                "h": h
            },
            "sourceSize": {
                "w": int(orig_sz.get('w', w) * best_scale),
                "h": int(orig_sz.get('h', h) * best_scale)
            }
        }

    # Save new webp directly
    new_atlas.save(webp_path, "WEBP", quality=90, method=4)
    manifest['frames'] = new_frames_dict
    manifest['meta']['size'] = {"w": best_atlas_w, "h": best_atlas_h}
    if 'scale' in manifest['meta']:
        manifest['meta']['scale'] = best_scale

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    return True, f"Repacked successfully to {best_atlas_w}x{best_atlas_h} (scale={best_scale:.2f})"

if __name__ == "__main__":
    ws = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets"
    folders = ['characters', 'wings', 'weapons', 'effects', 'mounts', 'monsters', 'npcs']
    count = 0
    repacked = 0

    for fld in folders:
        target = os.path.join(ws, fld)
        if not os.path.exists(target): continue
        for item in sorted(os.listdir(target)):
            dir_path = os.path.join(target, item)
            webp_path = os.path.join(dir_path, 'atlas.webp')
            if os.path.exists(webp_path):
                try:
                    with Image.open(webp_path) as im:
                        if im.width > 4096 or im.height > 4096:
                            count += 1
                            print(f"\nProcessing [{count}] {fld}/{item} with size {im.size}...")
                            succ, msg = repack_atlas(dir_path, max_dim=4096)
                            print(f" -> {succ}: {msg}")
                            if succ: repacked += 1
                except Exception as e:
                    print(f"Error checking {dir_path}: {e}")

    print(f"\nFinished! Found {count} large atlases, successfully repacked {repacked}.")

