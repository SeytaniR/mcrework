"""
Extrator de NPCs do Mapa 1 para Pixi.js
Magic Campus Modern Rework
"""

import os, sys, re, zlib, io, json, hashlib
from PIL import Image

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
SQL_PATH = os.path.join(BASE_DIR, "mcgame", "supabase", "seeds", "data_tbl_npc.sql")
OUT_NPCS_DIR = os.path.join(BASE_DIR, "web", "assets", "map1", "npcs")
OUT_JSON_PATH = os.path.join(BASE_DIR, "web", "assets", "map1", "npcs.json")

def decode_res_code(code_num):
    ext_id = code_num // 1000000000000
    rem = code_num % 1000000000000
    ext_map = {1: "", 2: ".swf", 3: ".jpg", 4: ".png"}
    ext = ext_map.get(ext_id, ".swf")

    w1_id = rem // 1000000000
    rem = rem % 1000000000
    folder = "creature/"
    w1 = "NPC_" if w1_id == 60 else "PC_"

    w2_id = rem // 1000000
    num = rem % 1000000
    w2_map = {70: "MALE_", 80: "FEMALE_", 90: "FUNC_", 100: "CRE_", 110: "WEAPON_", 160: "NPC_"}
    w2 = w2_map.get(w2_id, "FUNC_")

    num_str = f"{num:06d}"
    rel_path = f"{folder}{w1}{w2}{num_str}{ext}"
    full_url = f"resource/{rel_path}"
    h = hashlib.md5(full_url.encode("utf-8")).hexdigest()
    res_name = f"{w1}{w2}{num_str}"
    return res_name, rel_path, full_url, h

def extract_swf_bitmaps(swf_file_path):
    if not os.path.exists(swf_file_path):
        return {}
    with open(swf_file_path, "rb") as f:
        data = f.read()
    decomp = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]
    full = b"FWS\t" + data[4:8] + decomp
    pos = 8 + ((5 + (full[8] >> 3) * 4 + 7) // 8 + 4)
    bitmaps = {}
    while pos < len(full):
        hdr = int.from_bytes(full[pos:pos+2], "little")
        t_type = hdr >> 6
        t_len = hdr & 0x3F
        pos += 2
        if t_len == 0x3F:
            t_len = int.from_bytes(full[pos:pos+4], "little")
            pos += 4
        tag_data = full[pos:pos+t_len]
        if t_type == 36: # Lossless2
            cid = int.from_bytes(tag_data[:2], "little")
            w = int.from_bytes(tag_data[3:5], "little")
            h = int.from_bytes(tag_data[5:7], "little")
            decomp_img = zlib.decompress(tag_data[7:])
            img = Image.frombytes("RGBA", (w, h), decomp_img, "raw", "ARGB")
            bitmaps[cid] = img
        elif t_type == 35: # JPEG3
            cid = int.from_bytes(tag_data[:2], "little")
            alpha_off = int.from_bytes(tag_data[2:6], "little")
            jpeg = tag_data[6:6+alpha_off]
            alpha = zlib.decompress(tag_data[6+alpha_off:])
            img = Image.open(io.BytesIO(jpeg)).convert("RGBA")
            img.putalpha(Image.frombytes("L", (img.width, img.height), alpha))
            bitmaps[cid] = img
        pos += t_len
    return bitmaps

def main():
    os.makedirs(OUT_NPCS_DIR, exist_ok=True)
    print("1. Lendo banco de dados data_tbl_npc.sql...")
    with open(SQL_PATH, "r", encoding="utf-8", errors="ignore") as f:
        sql = f.read()

    rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
    map1_npcs_raw = []
    for r in rows:
        fields = []
        in_quote = False
        cur = []
        for ch in r:
            if ch == "'":
                in_quote = not in_quote
                cur.append(ch)
            elif ch == ',' and not in_quote:
                fields.append(''.join(cur).strip())
                cur = []
            else:
                cur.append(ch)
        fields.append(''.join(cur).strip())

        if len(fields) >= 26:
            try:
                map_id = int(fields[20])
                if map_id == 1:
                    npc_id = int(fields[0])
                    name = fields[14].strip("'")
                    dir_val = int(fields[19])
                    x = int(fields[21])
                    y = int(fields[22])
                    res_code = int(fields[25])
                    map1_npcs_raw.append({
                        "id": npc_id,
                        "name": name,
                        "x": x,
                        "y": y,
                        "dir": dir_val,
                        "res_code": res_code
                    })
            except Exception:
                pass

    print(f"Total de NPCs encontrados no Mapa 1: {len(map1_npcs_raw)}")

    # Mapeamento e extração de recursos
    extracted_resources = {}
    unique_res_codes = set(npc["res_code"] for npc in map1_npcs_raw)

    for code in unique_res_codes:
        res_name, rel_path, full_url, h = decode_res_code(code)
        swf_path = os.path.join(RES_DIR, h)
        bmps = extract_swf_bitmaps(swf_path)
        
        # Fallback para 000094 (Vận Đội) se SWF for vetorial:
        if not bmps and code == 2060090000094:
            print("NPC_FUNC_000094 é vetorial - usando visual de escolta de NPC_FUNC_000010...")
            res_name_fb, _, _, h_fb = decode_res_code(2060090000010)
            bmps = extract_swf_bitmaps(os.path.join(RES_DIR, h_fb))

        if not bmps:
            print(f"Aviso: Nenhuma imagem encontrada para res_code={code} ({res_name})")
            continue

        # Ordenar cids
        sorted_cids = sorted(bmps.keys())
        bmp_list = [bmps[cid] for cid in sorted_cids]

        # Calcular bbox unificado
        bboxes = [img.getbbox() for img in bmp_list if img.getbbox()]
        if not bboxes:
            continue
        u_xmin = min(b[0] for b in bboxes)
        u_ymin = min(b[1] for b in bboxes)
        u_xmax = max(b[2] for b in bboxes)
        u_ymax = max(b[3] for b in bboxes)

        res_out_dir = os.path.join(OUT_NPCS_DIR, res_name)
        os.makedirs(res_out_dir, exist_ok=True)

        cropped_frames = []
        for i, img in enumerate(bmp_list):
            cropped = img.crop((u_xmin, u_ymin, u_xmax, u_ymax))
            frame_filename = f"frame_{i}.png"
            cropped.save(os.path.join(res_out_dir, frame_filename))
            cropped_frames.append(f"assets/map1/npcs/{res_name}/{frame_filename}")

        # Se tiver 3 bitmaps (padrão de idle do Magic Campus: 1 -> 3 -> 5 -> 3 loop)
        animation_sequence = []
        if len(cropped_frames) == 3:
            animation_sequence = [
                cropped_frames[0],
                cropped_frames[1],
                cropped_frames[2],
                cropped_frames[1]
            ]
        else:
            animation_sequence = cropped_frames

        w = u_xmax - u_xmin
        h = u_ymax - u_ymin

        extracted_resources[code] = {
            "res_name": res_name,
            "frames": animation_sequence,
            "width": w,
            "height": h,
            "is_animated": len(animation_sequence) > 1
        }
        print(f"Extraído {res_name}: {len(animation_sequence)} frames ({w}x{h}px)")

    # Montar JSON final para o cliente Pixi
    final_npcs = []
    seen_positions = set()

    for npc in map1_npcs_raw:
        # Deduplicar árvore de natal no mesmo tile se houver duplicata de ID de evento
        pos_key = (npc["x"], npc["y"], npc["name"])
        if pos_key in seen_positions:
            print(f"Ignorando duplicata de evento: {npc['name']} em ({npc['x']}, {npc['y']})")
            continue
        seen_positions.add(pos_key)

        res_info = extracted_resources.get(npc["res_code"])
        if not res_info:
            print(f"Aviso: NPC {npc['name']} sem recurso gráfico!")
            continue

        final_npcs.append({
            "id": npc["id"],
            "name": npc["name"],
            "x": npc["x"],
            "y": npc["y"],
            "dir": npc["dir"],
            "res_code": npc["res_code"],
            "res_name": res_info["res_name"],
            "frames": res_info["frames"],
            "width": res_info["width"],
            "height": res_info["height"],
            "is_animated": res_info["is_animated"],
            "shadow_radius_x": max(14, int(res_info["width"] * 0.35)),
            "shadow_radius_y": max(7, int(res_info["width"] * 0.18))
        })

    with open(OUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(final_npcs, f, ensure_ascii=False, indent=2)

    print(f"\nSucesso! {len(final_npcs)} NPCs exportados para {OUT_JSON_PATH}")

if __name__ == "__main__":
    main()
