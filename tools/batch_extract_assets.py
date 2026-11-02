"""
Batch Asset Extractor & Spritesheet Atlas Generator
Magic Campus Rework Engine (Pixi.js / WebGL / Mobile APK)
"""

import os, sys, zlib, io, json, re, hashlib, argparse, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

RES_DIR = r"mcgame/frontend/s/res"
SQL_CREATURES_PATH = r"mcgame/supabase/seeds/data_tbl_creature.sql"
OUT_MONSTERS_DIR = r"web/assets/monsters"
OUT_CHARACTERS_DIR = r"web/assets/characters"

def parse_swf(swf_path):
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
            except Exception:
                pass
        elif t_type == 1: # ShowFrame
            frame_idx += 1
        elif t_type == 36: # DefineBitsLossless2
            cid = int.from_bytes(tag_data[:2], "little")
            fmt = tag_data[2]
            w = int.from_bytes(tag_data[3:5], "little")
            h = int.from_bytes(tag_data[5:7], "little")
            if fmt == 5:
                try:
                    decomp_img = zlib.decompress(tag_data[7:])
                    img = Image.frombytes("RGBA", (w, h), decomp_img, "raw", "ARGB")
                    bitmaps[cid] = img
                except Exception:
                    pass
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
            except Exception:
                pass
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

    # Map frames to labels and active bitmap IDs
    anim_frames = {}
    cur_lbl = None
    cur_cid = None
    for f in range(1, frame_idx):
        if f in placements:
            cur_cid = placements[f]
        if f in labels:
            cur_lbl = labels[f]
        if cur_lbl and cur_cid:
            bmp_id = None
            if cur_cid in bitmaps:
                bmp_id = cur_cid
            elif cur_cid in shapes and shapes[cur_cid] in bitmaps:
                bmp_id = shapes[cur_cid]
            elif (cur_cid - 1) in bitmaps:
                bmp_id = cur_cid - 1

            if bmp_id is not None and bmp_id in bitmaps:
                anim_frames.setdefault(cur_lbl, []).append(bmp_id)

    return bitmaps, anim_frames

def pack_atlas(bitmaps, anim_frames, out_dir, model_name="model", extra_meta=None):
    os.makedirs(out_dir, exist_ok=True)

    used_bmp_ids = sorted(list(set(bmp for frame_list in anim_frames.values() for bmp in frame_list)))
    if not used_bmp_ids:
        return None

    bboxes = [bitmaps[bid].getbbox() for bid in used_bmp_ids if bitmaps[bid].getbbox()]
    if not bboxes:
        sample = bitmaps[used_bmp_ids[0]]
        u_minx, u_miny, u_maxx, u_maxy = 0, 0, sample.width, sample.height
    else:
        u_minx = min(b[0] for b in bboxes)
        u_miny = min(b[1] for b in bboxes)
        u_maxx = max(b[2] for b in bboxes)
        u_maxy = max(b[3] for b in bboxes)

    crop_w = max(1, u_maxx - u_minx)
    crop_h = max(1, u_maxy - u_miny)

    cropped_bmps = {}
    for bid in used_bmp_ids:
        img = bitmaps[bid]
        cropped_bmps[bid] = img.crop((u_minx, u_miny, u_maxx, u_maxy))

    # Shelf Bin Packing sorted by height descending
    pad = 2
    sorted_items = sorted(cropped_bmps.items(), key=lambda it: it[1].height, reverse=True)

    total_area = sum((b.width + pad) * (b.height + pad) for _, b in sorted_items)
    side = 256
    while side * side < total_area * 1.25:
        side *= 2
    atlas_w = side
    atlas_h = side

    cur_x = pad
    cur_y = pad
    row_h = 0
    placements = {}

    for bid, bmp in sorted_items:
        w, h = bmp.width, bmp.height
        if cur_x + w + pad > atlas_w:
            cur_x = pad
            cur_y += row_h + pad
            row_h = 0
        while cur_y + h + pad > atlas_h:
            atlas_h *= 2

        placements[bid] = (cur_x, cur_y, w, h)
        cur_x += w + pad
        row_h = max(row_h, h)

    # Tighten final height to power of 2
    final_h = 256
    while final_h < cur_y + row_h + pad:
        final_h *= 2
    atlas_h = final_h

    # Create atlas image
    atlas_img = Image.new("RGBA", (atlas_w, atlas_h), (0, 0, 0, 0))
    for bid, (x, y, w, h) in placements.items():
        atlas_img.paste(cropped_bmps[bid], (x, y))

    webp_path = os.path.join(out_dir, "atlas.webp")
    atlas_img.save(webp_path, "WEBP", quality=92, method=4)
    file_size_kb = os.path.getsize(webp_path) / 1024

    frames_dict = {}
    for bid, (x, y, w, h) in placements.items():
        frames_dict[f"bmp_{bid}"] = {
            "frame": {"x": x, "y": y, "w": w, "h": h},
            "rotated": False,
            "trimmed": False,
            "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
            "sourceSize": {"w": w, "h": h}
        }

    animations_dict = {}
    for lbl, b_list in anim_frames.items():
        animations_dict[lbl] = [f"bmp_{bid}" for bid in b_list]

    manifest = {
        "frames": frames_dict,
        "animations": animations_dict,
        "meta": {
            "app": "MagicCampus-AtlasPacker",
            "version": "2.0",
            "image": "atlas.webp",
            "format": "RGBA8888",
            "size": {"w": atlas_w, "h": atlas_h},
            "scale": 1
        }
    }

    json_path = os.path.join(out_dir, "atlas.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    actions = sorted(list(set(int(k.split("-")[1]) for k in anim_frames.keys() if "-" in k)))
    directions = sorted(list(set(int(k.split("-")[0]) for k in anim_frames.keys() if "-" in k)))
    total_frames = sum(len(f_list) for f_list in anim_frames.values())

    visual_meta = {
        "name": model_name,
        "anchor": [0.5, 1.0],
        "width": crop_w,
        "height": crop_h,
        "bbox": [u_minx, u_miny, u_maxx, u_maxy],
        "total_unique_bitmaps": len(used_bmp_ids),
        "animations_count": len(anim_frames),
        "total_animation_frames": total_frames,
        "actions": actions,
        "directions": directions,
        "atlas_size_kb": round(file_size_kb, 1),
        "atlas_dimensions": [atlas_w, atlas_h]
    }
    if extra_meta:
        visual_meta.update(extra_meta)

    meta_path = os.path.join(out_dir, "visual_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(visual_meta, f, indent=2, ensure_ascii=False)

    return visual_meta

def process_single_asset(task):
    """Worker function for multiprocessing"""
    swf_path, out_dir, model_name, extra_meta = task
    try:
        bitmaps, anims = parse_swf(swf_path)
        if not bitmaps or not anims:
            return {"status": "skip", "name": model_name, "reason": "No bitmaps or animations"}
        meta = pack_atlas(bitmaps, anims, out_dir, model_name, extra_meta)
        if meta:
            return {"status": "ok", "name": model_name, "meta": meta, "dir": out_dir}
        else:
            return {"status": "skip", "name": model_name, "reason": "Packing returned None"}
    except Exception as e:
        return {"status": "error", "name": model_name, "error": str(e)}

def extract_all_characters():
    print("\n" + "="*60)
    print("🧙 EXTRAÇÃO DE TODAS AS CLASSES E SKINS DE PERSONAGENS")
    print("="*60)

    res_files = set(os.listdir(RES_DIR))
    tasks = []

    # Male classes mapping
    male_names = {
        1: "Guerreiro Base (M)",
        2: "Mago Base (M)",
        3: "Caçador / Arqueiro Base (M)",
        4: "Sacerdote Base (M)",
        5: "Artífice / Mecânico Base (M)",
        6: "Místico / Assassino Base (M)",
        11: "Guerreiro Sagrado Tier 2 (M)",
        12: "Arquimago Supremo Tier 2 (M)",
        13: "Franco-Atirador Tier 2 (M)",
        14: "Sumo Sacerdote Tier 2 (M)",
        15: "Mestre Mecatrônico Tier 2 (M)",
        16: "Lorde Místico Tier 2 (M)",
        100000: "Pose de Montaria Cavalo (M)",
        100001: "Pose de Montaria Lobo (M)",
        100002: "Pose de Montaria Tigre (M)",
        100003: "Pose de Montaria Dragão (M)",
        100004: "Pose de Montaria Pássaro (M)",
        100005: "Pose de Montaria Nuvem (M)",
        100006: "Pose de Montaria Tapete (M)",
    }

    # Female classes mapping
    female_names = {
        1: "Guerreira Base (F)",
        2: "Maga Base (F)",
        3: "Caçadora / Arqueira Base (F)",
        4: "Sacerdotisa Base (F)",
        5: "Artífice / Mecânica Base (F)",
        6: "Mística / Assassina Base (F)",
        11: "Guerreira Sagrada Tier 2 (F)",
        12: "Arquimaga Suprema Tier 2 (F)",
        13: "Franco-Atiradora Tier 2 (F)",
        14: "Suma Sacerdotisa Tier 2 (F)",
        15: "Mestra Mecatrônica Tier 2 (F)",
        16: "Lorde Mística Tier 2 (F)",
        10005: "Costume de Gala / Festa (F)",
        10010: "Vestido Nupcial Real (F)",
        10011: "Armadura Cerimonial Dourada (F)",
        10012: "Quimono Oriental da Primavera (F)",
        10016: "Traje Angelical com Asas Divinas (F)",
        10017: "Traje Casual Estudante (F)",
        10018: "Armadura Valquíria da Alvorada (F)",
        10019: "Traje Festivo Celebração (F)",
        10020: "Armadura Rainha Dracônica (F)",
        100001: "Pose de Montaria Lobo (F)",
        100002: "Pose de Montaria Tigre (F)",
        100003: "Pose de Montaria Dragão (F)",
        100004: "Pose de Montaria Pássaro (F)",
        100005: "Pose de Montaria Nuvem (F)",
        100006: "Pose de Montaria Tapete (F)",
    }

    for i in range(250000):
        rel = f"creature/PC_MALE_{i:06d}.swf"
        h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
        if h in res_files:
            swf_p = os.path.join(RES_DIR, h)
            cid = f"PC_MALE_{i:06d}"
            name = male_names.get(i, f"Classe Masculina #{i:06d}")
            tier = 2 if (11 <= i <= 16) else ("mount" if i >= 100000 else 1)
            out_d = os.path.join(OUT_CHARACTERS_DIR, cid)
            tasks.append((swf_p, out_d, name, {
                "id": cid,
                "gender": "MALE",
                "tier": tier,
                "res_code_num": i,
                "swf_hash": h
            }))

    for i in range(250000):
        rel = f"creature/PC_FEMALE_{i:06d}.swf"
        h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
        if h in res_files:
            swf_p = os.path.join(RES_DIR, h)
            cid = f"PC_FEMALE_{i:06d}"
            name = female_names.get(i, f"Classe Feminina #{i:06d}")
            tier = 2 if (11 <= i <= 16) else ("costume" if (10000 <= i < 100000) else ("mount" if i >= 100000 else 1))
            out_d = os.path.join(OUT_CHARACTERS_DIR, cid)
            tasks.append((swf_p, out_d, name, {
                "id": cid,
                "gender": "FEMALE",
                "tier": tier,
                "res_code_num": i,
                "swf_hash": h
            }))

    print(f"Total de classes/skins a extrair: {len(tasks)}")
    catalog = []
    start_time = time.time()

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_single_asset, t): t for t in tasks}
        for fut in as_completed(futures):
            res = fut.result()
            if res["status"] == "ok":
                meta = res["meta"]
                catalog.append({
                    "id": meta["id"],
                    "name": meta["name"],
                    "gender": meta["gender"],
                    "tier": meta["tier"],
                    "res_code_num": meta["res_code_num"],
                    "actions": meta["actions"],
                    "directions": meta["directions"],
                    "width": meta["width"],
                    "height": meta["height"],
                    "total_frames": meta["total_animation_frames"],
                    "atlas_size_kb": meta["atlas_size_kb"],
                    "path": f"assets/characters/{meta['id']}/atlas.json"
                })
                print(f"✓ {meta['id']} ({meta['name']}): {meta['width']}x{meta['height']}px | {meta['atlas_size_kb']} KB")
            else:
                print(f"✗ {res['name']}: {res.get('error') or res.get('reason')}")

    # Sort catalog by ID
    catalog.sort(key=lambda x: x["id"])
    catalog_path = os.path.join(OUT_CHARACTERS_DIR, "catalog.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_classes": len(catalog),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "classes": catalog
        }, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"\n🎉 Concluído: {len(catalog)} classes/skins extraídas em {elapsed:.1f}s!")
    print(f"Catálogo salvo em: {catalog_path}")
    return catalog

def extract_all_monsters():
    print("\n" + "="*60)
    print("👾 EXTRAÇÃO DE TODOS OS MONSTROS E PETS")
    print("="*60)

    res_files = set(os.listdir(RES_DIR))

    # Parse data_tbl_creature.sql
    with open(SQL_CREATURES_PATH, "r", encoding="utf-8", errors="ignore") as f:
        sql = f.read()

    rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
    creatures_dict = {}

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
        if len(fields) >= 35:
            cid = fields[0]
            name = fields[24].strip("'")
            rc_str = fields[34]
            try:
                rc = int(rc_str)
                rem = rc % 1000000000000
                w1_id = rem // 1000000000
                rem = rem % 1000000000
                w2_id = rem // 1000000
                num = rem % 1000000
                w1 = "NPC_" if w1_id == 60 else "PC_"
                w2_map = {70: "MALE_", 80: "FEMALE_", 90: "FUNC_", 100: "CRE_", 110: "WEAPON_", 160: "NPC_"}
                w2 = w2_map.get(w2_id, "CRE_")
                rel = f"creature/{w1}{w2}{num:06d}.swf"
                h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
                if h in res_files and rel not in creatures_dict:
                    creatures_dict[rel] = {
                        "db_id": cid,
                        "name": name,
                        "rel_path": rel,
                        "hash": h,
                        "num": num,
                        "prefix": f"{w1}{w2}"
                    }
            except Exception:
                pass

    # Also include any remaining NPC_CRE_*.swf
    for i in range(250000):
        rel = f"creature/NPC_CRE_{i:06d}.swf"
        if rel not in creatures_dict:
            h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
            if h in res_files:
                creatures_dict[rel] = {
                    "db_id": str(100000 + i),
                    "name": f"Criatura #{i:06d}",
                    "rel_path": rel,
                    "hash": h,
                    "num": i,
                    "prefix": "NPC_CRE_"
                }

    tasks = []
    for rel, c in creatures_dict.items():
        swf_p = os.path.join(RES_DIR, c["hash"])
        cid_slug = f"creature_{c['num']:06d}"
        out_d = os.path.join(OUT_MONSTERS_DIR, cid_slug)
        tasks.append((swf_p, out_d, c["name"], {
            "id": cid_slug,
            "db_id": c["db_id"],
            "res_code_num": c["num"],
            "swf_hash": c["hash"]
        }))

    # Also ensure Mushroom (res_code_num 15) outputs to web/assets/monsters/mushroom
    m_task = None
    for t in tasks:
        if t[3]["res_code_num"] == 15:
            m_task = (t[0], os.path.join(OUT_MONSTERS_DIR, "mushroom"), "Cogumelo Selvagem (Nấm Đồng Cỏ)", {
                "id": "mushroom",
                "db_id": t[3]["db_id"],
                "res_code_num": 15,
                "swf_hash": t[3]["swf_hash"]
            })
            break
    if m_task:
        tasks.append(m_task)

    print(f"Total de monstros/pets a extrair: {len(tasks)}")
    catalog = []
    start_time = time.time()

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_single_asset, t): t for t in tasks}
        count = 0
        total = len(tasks)
        for fut in as_completed(futures):
            count += 1
            res = fut.result()
            if res["status"] == "ok":
                meta = res["meta"]
                if meta["id"] != "mushroom": # Catalog contains unique model IDs
                    catalog.append({
                        "id": meta["id"],
                        "name": meta["name"],
                        "db_id": meta.get("db_id"),
                        "res_code_num": meta.get("res_code_num"),
                        "actions": meta["actions"],
                        "directions": meta["directions"],
                        "width": meta["width"],
                        "height": meta["height"],
                        "total_frames": meta["total_animation_frames"],
                        "atlas_size_kb": meta["atlas_size_kb"],
                        "path": f"assets/monsters/{meta['id']}/atlas.json"
                    })
                if count % 25 == 0 or count == total:
                    print(f"[{count}/{total}] Progresso da extração...")
            else:
                pass

    catalog.sort(key=lambda x: x["res_code_num"])
    catalog_path = os.path.join(OUT_MONSTERS_DIR, "catalog.json")
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_monsters": len(catalog),
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "monsters": catalog
        }, f, indent=2, ensure_ascii=False)

    # Clean up loose PNG files in mushroom directory if atlas files exist
    m_dir = os.path.join(OUT_MONSTERS_DIR, "mushroom")
    if os.path.exists(os.path.join(m_dir, "atlas.webp")):
        loose_count = 0
        for f in os.listdir(m_dir):
            if f.startswith("frame_") and f.endswith(".png"):
                try:
                    os.remove(os.path.join(m_dir, f))
                    loose_count += 1
                except Exception:
                    pass
        if loose_count > 0:
            print(f"🧹 Limpeza realizada: {loose_count} arquivos PNG soltos removidos de 'mushroom/'!")

    elapsed = time.time() - start_time
    print(f"\n🎉 Concluído: {len(catalog)} monstros/pets extraídos em {elapsed:.1f}s!")
    print(f"Catálogo salvo em: {catalog_path}")
    return catalog

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch Asset Extractor & Atlas Packer")
    parser.add_argument("--mode", choices=["all", "characters", "monsters"], default="all")
    args = parser.parse_args()

    if args.mode in ("all", "characters"):
        extract_all_characters()

    if args.mode in ("all", "monsters"):
        extract_all_monsters()
