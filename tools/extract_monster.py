"""
Extrator de Monstros e Criaturas do Magic Campus para Pixi.js
"""

import os, sys, zlib, io, json, argparse
from PIL import Image

def extract_monster(swf_path, out_dir, name="monster"):
    os.makedirs(out_dir, exist_ok=True)
    print(f"Lendo SWF do Monstro: {swf_path}...")

    with open(swf_path, "rb") as f:
        data = f.read()

    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp

    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)

    bitmaps = {}
    labels = {}
    placements = {}
    shapes = {}
    frame_idx = 1

    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4

        tag_data = full[pos:pos+t_len]

        if t_type == 43: # FrameLabel
            null_idx = tag_data.find(b"\x00")
            raw = tag_data[:null_idx]
            try:
                name_lbl = raw.decode("ascii")
                if "-" in name_lbl:
                    labels[frame_idx] = name_lbl
            except:
                pass
        elif t_type == 1: # ShowFrame
            frame_idx += 1
        elif t_type == 36: # DefineBitsLossless2
            cid = int.from_bytes(tag_data[:2], "little")
            fmt = tag_data[2]
            w = int.from_bytes(tag_data[3:5], "little")
            h = int.from_bytes(tag_data[5:7], "little")
            if fmt == 5:
                decomp_img = zlib.decompress(tag_data[7:])
                img = Image.frombytes("RGBA", (w, h), decomp_img, "raw", "ARGB")
                bitmaps[cid] = img
        elif t_type == 35: # DefineBitsJPEG3
            cid = int.from_bytes(tag_data[:2], "little")
            alpha_offset = int.from_bytes(tag_data[2:6], "little")
            jpeg_data = tag_data[6:6+alpha_offset]
            alpha_comp = tag_data[6+alpha_offset:]
            try:
                alpha_data = zlib.decompress(alpha_comp)
                img = Image.open(io.BytesIO(jpeg_data)).convert("RGBA")
                img.putalpha(Image.frombytes("L", (img.width, img.height), alpha_data))
                bitmaps[cid] = img
            except Exception as e:
                print(f"Aviso JPEG3 cid={cid}: {e}")
        elif t_type in (2, 22, 32, 83): # Shape
            cid = int.from_bytes(tag_data[:2], "little")
            nb = tag_data[2] >> 3
            rect_bytes = (5 + 4 * nb + 7) // 8
            fill_data = tag_data[2+rect_bytes:]
            if len(fill_data) >= 4:
                bid = int.from_bytes(fill_data[2:4], "little")
                shapes[cid] = bid
        elif t_type == 26: # PlaceObject2
            flags = tag_data[0]
            if flags & 0x02:
                cid = int.from_bytes(tag_data[3:5], "little")
                placements[frame_idx] = cid

        pos += t_len

    print(f"Decodificados: {len(bitmaps)} imagens, {len(labels)} rotulos, {len(placements)} posicionamentos, {frame_idx} frames.")

    # Obter bounding box unificado
    bboxes = [img.getbbox() for img in bitmaps.values() if img.getbbox()]
    if bboxes:
        u_minx = min(b[0] for b in bboxes)
        u_miny = min(b[1] for b in bboxes)
        u_maxx = max(b[2] for b in bboxes)
        u_maxy = max(b[3] for b in bboxes)
    else:
        sample = list(bitmaps.values())[0]
        u_minx, u_miny, u_maxx, u_maxy = 0, 0, sample.width, sample.height

    crop_w = u_maxx - u_minx
    crop_h = u_maxy - u_miny
    print(f"BBox unificado: ({u_minx}, {u_miny}, {u_maxx}, {u_maxy}) -> {crop_w}x{crop_h}px")

    animations = {}
    current_lbl = None

    for f_num in range(1, frame_idx):
        if f_num in labels:
            current_lbl = labels[f_num]

        if not current_lbl:
            continue

        placed_cid = None
        for p_f in range(f_num, 0, -1):
            if p_f in placements:
                placed_cid = placements[p_f]
                break

        if placed_cid:
            bmp_id = shapes.get(placed_cid, placed_cid - 1)
            if bmp_id in bitmaps:
                img = bitmaps[bmp_id]
                cropped = img.crop((u_minx, u_miny, u_maxx, u_maxy))
                filename = f"frame_{f_num}_{current_lbl}.png"
                filepath = os.path.join(out_dir, filename)
                cropped.save(filepath)

                rel_path = f"assets/monsters/mushroom/{filename}"
                animations.setdefault(current_lbl, []).append({
                    "frame": f_num,
                    "file": rel_path,
                    "width": cropped.width,
                    "height": cropped.height
                })

    clean_manifest = {}
    for lbl, f_list in animations.items():
        unique = []
        seen = set()
        for item in f_list:
            if item["file"] not in seen:
                seen.add(item["file"])
                unique.append(item)
        clean_manifest[lbl] = unique

    manifest_path = os.path.join(out_dir, "monster_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as out:
        json.dump({
            "name": name,
            "width": crop_w,
            "height": crop_h,
            "animations": clean_manifest
        }, out, indent=2, ensure_ascii=False)

    print(f"Manifesto salvo em: {manifest_path} com {len(clean_manifest)} animações!")

if __name__ == "__main__":
    res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
    # Nấm Đồng Cỏ (Cogumelo do Campo)
    swf_mushroom = os.path.join(res_dir, "28af28f7cb24a4660eccf8576a787c5d")
    out_mushroom = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\monsters\mushroom"
    extract_monster(swf_mushroom, out_mushroom, name="Nấm Đồng Cỏ")
