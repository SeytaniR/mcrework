import os, sys, hashlib, time, json, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from PIL import Image
import zlib, io

res_dir = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res'
out_base = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\weapons'

def extract_optimized_weapon(swf_path, out_dir, rel_prefix):
    os.makedirs(out_dir, exist_ok=True)
    with open(swf_path, 'rb') as f:
        data = f.read()

    decomp = zlib.decompress(data[8:]) if data[:3] == b'CWS' else data[8:]
    full = b'FWS\t' + data[4:8] + decomp

    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    bitmaps = {}
    labels = {}
    placements = {}
    frame_idx = 1

    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], 'little')
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], 'little')
            pos += 4
        tag_data = full[pos:pos+t_len]

        if t_type == 43: # FrameLabel
            raw = tag_data[:tag_data.find(b'\x00')]
            try:
                name = raw.decode('ascii')
                if '-' in name: labels[frame_idx] = name
            except: pass
        elif t_type == 1: # ShowFrame
            frame_idx += 1
        elif t_type == 36: # DefineBitsLossless2
            cid = int.from_bytes(tag_data[:2], 'little')
            fmt = tag_data[2]
            w = int.from_bytes(tag_data[3:5], 'little')
            h = int.from_bytes(tag_data[5:7], 'little')
            if fmt == 5:
                decomp_img = zlib.decompress(tag_data[7:])
                img = Image.frombytes('RGBA', (w, h), decomp_img, 'raw', 'ARGB')
                bitmaps[cid] = img.crop((300, 266, 500, 416)) if w == 800 and h == 640 else img
        elif t_type == 35: # DefineBitsJPEG3
            cid = int.from_bytes(tag_data[:2], 'little')
            alpha_offset = int.from_bytes(tag_data[2:6], 'little')
            jpeg_data = tag_data[6:6+alpha_offset]
            alpha_comp = tag_data[6+alpha_offset:]
            try:
                alpha_data = zlib.decompress(alpha_comp)
                img = Image.open(io.BytesIO(jpeg_data)).convert('RGBA')
                img.putalpha(Image.frombytes('L', (img.width, img.height), alpha_data))
                bitmaps[cid] = img.crop((300, 266, 500, 416)) if img.width == 800 and img.height == 640 else img
            except: pass
        elif t_type == 26: # PlaceObject2
            flags = tag_data[0]
            if flags & 0x02:
                cid = int.from_bytes(tag_data[3:5], 'little')
                placements[frame_idx] = cid
        pos += t_len

    saved_files = {}
    for cid, img in bitmaps.items():
        fname = f'bmp_{cid}.png'
        fpath = os.path.join(out_dir, fname)
        img.save(fpath)
        saved_files[cid] = f'{rel_prefix}/{fname}'

    animations = {}
    current_lbl = None
    for f_num in range(1, frame_idx):
        if f_num in labels: current_lbl = labels[f_num]
        if not current_lbl: continue
        placed_cid = None
        for p_f in range(f_num, 0, -1):
            if p_f in placements:
                placed_cid = placements[p_f]
                break
        if placed_cid:
            bmp_id = placed_cid - 1
            if bmp_id in saved_files:
                animations.setdefault(current_lbl, []).append({
                    'frame': f_num,
                    'file': saved_files[bmp_id],
                    'width': bitmaps[bmp_id].width,
                    'height': bitmaps[bmp_id].height
                })

    with open(os.path.join(out_dir, 'char_manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(animations, f, indent=2)

# Collect all male weapon SWFs
all_swfs = []
for c in ['MC1', 'MC2', 'MC3', 'MC4', 'MC5', 'MC6']:
    for i in range(0, 22):
        rel = f"equip/EQUIP_{c}_{str(i).zfill(6)}.swf"
        h = hashlib.md5(('resource/' + rel).encode('utf-8')).hexdigest()
        p = os.path.join(res_dir, h)
        if os.path.exists(p):
            all_swfs.append((rel, p))

print(f"Total weapon SWFs to convert: {len(all_swfs)}")

# Clean and recreate out_base
if os.path.exists(out_base):
    shutil.rmtree(out_base)
os.makedirs(out_base, exist_ok=True)

t0 = time.time()
converted = 0
for idx, (rel, swf_path) in enumerate(all_swfs):
    weapon_id = os.path.splitext(os.path.basename(rel))[0].lower()
    dest_dir = os.path.join(out_base, weapon_id)
    rel_prefix = f"assets/weapons/{weapon_id}"
    try:
        extract_optimized_weapon(swf_path, dest_dir, rel_prefix)
        converted += 1
        if (idx + 1) % 10 == 0 or (idx + 1) == len(all_swfs):
            print(f"[{idx+1}/{len(all_swfs)}] Converted {weapon_id}...")
    except Exception as e:
        print(f"Error converting {weapon_id}: {e}")

total_files = sum(len(files) for _, _, files in os.walk(out_base))
total_mb = sum(os.path.getsize(os.path.join(r, f)) for r, _, files in os.walk(out_base) for f in files) / (1024*1024)
print(f"Batch optimization complete! {converted} weapons in {time.time()-t0:.1f}s.")
print(f"Stats: {total_files} files, {total_mb:.2f} MB total.")
