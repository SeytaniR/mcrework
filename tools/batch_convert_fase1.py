import os, sys, hashlib, time, json, shutil
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from PIL import Image
import zlib, io

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
res_dir = os.path.join(ws, 'mcgame', 'frontend', 's', 'res')
res_files = set(os.listdir(res_dir))

def extract_optimized_swf(swf_path, out_dir, rel_prefix, is_wing=False):
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
                # Crop standard 800x640 canvas to 200x150 for weapons/characters
                if w == 800 and h == 640 and not is_wing:
                    bitmaps[cid] = img.crop((300, 266, 500, 416))
                else:
                    bitmaps[cid] = img
        elif t_type == 35: # DefineBitsJPEG3
            cid = int.from_bytes(tag_data[:2], 'little')
            alpha_offset = int.from_bytes(tag_data[2:6], 'little')
            jpeg_data = tag_data[6:6+alpha_offset]
            alpha_comp = tag_data[6+alpha_offset:]
            try:
                alpha_data = zlib.decompress(alpha_comp)
                img = Image.open(io.BytesIO(jpeg_data)).convert('RGBA')
                img.putalpha(Image.frombytes('L', (img.width, img.height), alpha_data))
                if img.width == 800 and img.height == 640 and not is_wing:
                    bitmaps[cid] = img.crop((300, 266, 500, 416))
                else:
                    bitmaps[cid] = img
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

def main():
    t0 = time.time()
    
    # --- 1. CONVERT WINGS (36 SWFs) ---
    wings_out_base = os.path.join(ws, 'web', 'assets', 'wings')
    os.makedirs(wings_out_base, exist_ok=True)
    
    # Load wings DB metadata
    wings_db_file = os.path.join(ws, 'tools', 'wings_db.json')
    wings_meta = {}
    if os.path.exists(wings_db_file):
        with open(wings_db_file, 'r', encoding='utf-8') as f:
            for item in json.load(f):
                if item.get('rel'):
                    k = item['rel'].replace('equip/', '').replace('.swf', '').lower()
                    wings_meta[k] = item

    wings_list = []
    # Find all 36 wings
    for prefix in ["equip/EQUIP_WING_", "equip/EQUIP_FLY_"]:
        for i in range(100000):
            rel = f"{prefix}{i:06d}.swf"
            h = hashlib.md5(f"resource/{rel}".encode('utf-8')).hexdigest()
            if h in res_files:
                model_name = rel.replace('equip/', '').replace('.swf', '').lower()
                swf_path = os.path.join(res_dir, h)
                wings_list.append((model_name, rel, swf_path, h))

    print(f"Total Wings to convert: {len(wings_list)}")
    wings_catalog = []
    for idx, (m_name, rel, swf_path, h) in enumerate(wings_list, 1):
        target_dir = os.path.join(wings_out_base, m_name)
        rel_prefix = f"assets/wings/{m_name}"
        extract_optimized_swf(swf_path, target_dir, rel_prefix, is_wing=True)
        
        meta = wings_meta.get(m_name, {})
        # Name resolution
        display_name = meta.get('name')
        if not display_name:
            if 'fly' in m_name:
                num = int(m_name.split('_')[-1])
                display_name = f"Cánh Phi Thiên {num:02d}"
            else:
                num = int(m_name.split('_')[-1])
                display_name = f"Cánh Ma Pháp {num:03d}"
                
        icon_path = None
        if meta.get('icon_rel'):
            icon_fname = os.path.basename(meta['icon_rel'])
            icon_candidate = f"assets/equipment/icons/{icon_fname}"
            if os.path.exists(os.path.join(ws, 'web', icon_candidate)):
                icon_path = icon_candidate
        if not icon_path:
            icon_path = "assets/equipment/icons/EQUIP_NORMAL_180001.png"
            
        wings_catalog.append({
            "id": meta.get('id') or (3000 + idx),
            "name": display_name,
            "model_id": m_name,
            "manifest_url": f"{rel_prefix}/char_manifest.json",
            "icon": icon_path,
            "description": meta.get('desc') or f"Asas visuais de alto nível ({m_name}). Concede poder e imponência ao personagem.",
            "type": "wing"
        })
        if idx % 5 == 0 or idx == len(wings_list):
            print(f"  [{idx}/{len(wings_list)}] Wing {m_name} converted -> {display_name}")

    with open(os.path.join(wings_out_base, 'catalog.json'), 'w', encoding='utf-8') as f:
        json.dump(wings_catalog, f, indent=2, ensure_ascii=False)
    print(f"Wings catalog saved with {len(wings_catalog)} wings!")

    # --- 2. CONVERT FEMALE WEAPONS (127 SWFs) ---
    weapons_out_base = os.path.join(ws, 'web', 'assets', 'weapons')
    os.makedirs(weapons_out_base, exist_ok=True)
    
    fc_list = []
    for c in range(1, 7):
        for i in range(1000):
            rel = f"equip/EQUIP_FC{c}_{i:06d}.swf"
            h = hashlib.md5(f"resource/{rel}".encode('utf-8')).hexdigest()
            if h in res_files:
                m_name = rel.replace('equip/', '').replace('.swf', '').lower()
                swf_path = os.path.join(res_dir, h)
                fc_list.append((m_name, rel, swf_path, h))

    print(f"\nTotal Female Weapons to convert: {len(fc_list)}")
    for idx, (m_name, rel, swf_path, h) in enumerate(fc_list, 1):
        target_dir = os.path.join(weapons_out_base, m_name)
        rel_prefix = f"assets/weapons/{m_name}"
        extract_optimized_swf(swf_path, target_dir, rel_prefix, is_wing=False)
        if idx % 20 == 0 or idx == len(fc_list):
            print(f"  [{idx}/{len(fc_list)}] Female Weapon {m_name} converted")

    t1 = time.time()
    print(f"\nFase 1 Assets Batch Extraction Completed in {t1 - t0:.1f}s!")

if __name__ == '__main__':
    main()
