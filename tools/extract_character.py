"""
Ferramenta Universal de Extração de Personagens (SWF -> PNG + Manifest JSON)
Magic Campus Modern Rework
"""

import os, sys, struct, zlib, json, argparse
from PIL import Image
import io

def extract_character(swf_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    print(f"Lendo SWF: {swf_path}...")
    with open(swf_path, "rb") as f:
        data = f.read()

    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp

    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)

    bitmaps = {}
    labels = {}
    placements = {}
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
                name = raw.decode("ascii")
                if "-" in name:
                    labels[frame_idx] = name
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
                if w == 800 and h == 640:
                    cropped = img.crop((300, 266, 500, 416))
                else:
                    cropped = img
                bitmaps[cid] = cropped
        elif t_type == 35: # DefineBitsJPEG3
            cid = int.from_bytes(tag_data[:2], "little")
            alpha_offset = int.from_bytes(tag_data[2:6], "little")
            jpeg_data = tag_data[6:6+alpha_offset]
            alpha_comp = tag_data[6+alpha_offset:]
            try:
                alpha_data = zlib.decompress(alpha_comp)
                img = Image.open(io.BytesIO(jpeg_data)).convert("RGBA")
                img.putalpha(Image.frombytes("L", (img.width, img.height), alpha_data))
                if img.width == 800 and img.height == 640:
                    cropped = img.crop((300, 266, 500, 416))
                else:
                    cropped = img
                bitmaps[cid] = cropped
            except Exception as e:
                print(f"Aviso JPEG3 cid={cid}: {e}")
        elif t_type == 26: # PlaceObject2
            flags = tag_data[0]
            if flags & 0x02:
                cid = int.from_bytes(tag_data[3:5], "little")
                placements[frame_idx] = cid

        pos += t_len

    print(f"Decodificados: {len(bitmaps)} imagens, {len(labels)} rotulos, {len(placements)} posicionamentos, {frame_idx} frames.")

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
            bmp_id = placed_cid - 1
            if bmp_id in bitmaps:
                img = bitmaps[bmp_id]
                filename = f"frame_{f_num}_{current_lbl}.png"
                filepath = os.path.join(out_dir, filename)
                img.save(filepath)

                # Caminho relativo para o cliente Pixi
                rel_dir = os.path.relpath(out_dir, start=os.path.join(os.path.dirname(out_dir), "..")).replace("\\", "/")
                animations.setdefault(current_lbl, []).append({
                    "frame": f_num,
                    "file": f"{rel_dir}/{filename}",
                    "width": img.width,
                    "height": img.height
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

    manifest_path = os.path.join(out_dir, "char_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as out:
        json.dump(clean_manifest, out, indent=2)

    print(f"Manifesto salvo em: {manifest_path} com {len(clean_manifest)} animações!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai personagens SWF do Magic Campus para Pixi.js")
    parser.add_argument("--swf", required=True, help="Caminho do arquivo SWF do personagem")
    parser.add_argument("--out", required=True, help="Diretório de saída para os frames PNG e manifesto")
    args = parser.parse_args()
    extract_character(args.swf, args.out)
