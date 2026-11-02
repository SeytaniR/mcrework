import os, sys, hashlib, re, json
from PIL import Image
from batch_extract_assets import parse_swf, pack_atlas

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RES_DIR = r"mcgame/frontend/s/res"
OUT_BASE = r"web/assets/mounts"
os.makedirs(OUT_BASE, exist_ok=True)

files = set(os.listdir(RES_DIR))

# Parse data_tbl_mount_dress.sql
mount_dresses = {}
with open(r"mcgame/supabase/seeds/data_tbl_mount_dress.sql", "r", encoding="utf-8", errors="ignore") as f:
    sql = f.read()

rows = re.findall(r"\(([^;]+?)\)[,;]", sql, re.DOTALL)
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
    if len(fields) >= 19:
        dress_id = fields[0].strip("'")
        name = fields[13].strip("'") if len(fields) > 13 else f"Mount {dress_id}"
        res_code = fields[18].strip("'") if len(fields) > 18 else ""
        icon_code = fields[6].strip("'") if len(fields) > 6 else ""
        mount_dresses[dress_id] = {
            "dress_id": dress_id,
            "name": name,
            "res_code": res_code,
            "icon_code": icon_code
        }

print(f"Mount dresses in DB: {len(mount_dresses)}")
for d in mount_dresses.values():
    print(f"  ID {d['dress_id']}: {d['name']} (res_code={d['res_code']})")

# Also find character mount poses:
# PC_MALE_100000..100006, PC_FEMALE_100001..100006
# and high tier mount dresses: PC_FEMALE_010005, 010010, 010011, 010012, 010016, 010017, 010018, 010019, 010020
mount_candidates = [
    # Basic mounts
    {"id": "mount_000001", "name": "Bạch Mã (Cavalo Branco)", "rel": "creature/PC_MALE_100001.swf", "type": "male_mount", "mount_tier": 1},
    {"id": "mount_000002", "name": "Hắc Báo (Pantera Negra)", "rel": "creature/PC_MALE_100002.swf", "type": "male_mount", "mount_tier": 2},
    {"id": "mount_000003", "name": "Huyết Dực Điểu (Pássaro de Sangue)", "rel": "creature/PC_MALE_100003.swf", "type": "male_mount", "mount_tier": 3},
    {"id": "mount_000004", "name": "Bôn Lôi Thú (Fera do Trovão)", "rel": "creature/PC_MALE_100004.swf", "type": "male_mount", "mount_tier": 4},
    {"id": "mount_000005", "name": "Thanh Long Sư (Leão Dragão Celeste)", "rel": "creature/PC_MALE_100005.swf", "type": "male_mount", "mount_tier": 5},
    {"id": "mount_000006", "name": "Cực Quang Thần Lộc (Cervo da Aurora)", "rel": "creature/PC_MALE_100006.swf", "type": "male_mount", "mount_tier": 6},
    
    # Female mounts
    {"id": "mount_f_000001", "name": "Bạch Tuyết Mã (Égua Branca Polar)", "rel": "creature/PC_FEMALE_100001.swf", "type": "female_mount", "mount_tier": 1},
    {"id": "mount_f_000002", "name": "Nguyệt Dạ Hổ (Tigre da Noite Lunar)", "rel": "creature/PC_FEMALE_100002.swf", "type": "female_mount", "mount_tier": 2},
    {"id": "mount_f_000003", "name": "Linh Điểu (Pássaro Espiritual)", "rel": "creature/PC_FEMALE_100003.swf", "type": "female_mount", "mount_tier": 3},
    {"id": "mount_f_000004", "name": "Thần Thú Viêm Báo (Pantera de Chamas)", "rel": "creature/PC_FEMALE_100004.swf", "type": "female_mount", "mount_tier": 4},
    {"id": "mount_f_000005", "name": "Cửu Vĩ Linh Hồ (Raposa Espiritual de 9 Caudas)", "rel": "creature/PC_FEMALE_010005.swf", "type": "legendary_mount", "mount_tier": 5},
    {"id": "mount_f_000006", "name": "Kỳ Lân Hoàng Gia (Qilin Real)", "rel": "creature/PC_FEMALE_100006.swf", "type": "female_mount", "mount_tier": 6},
    
    # Legendary Mount Dresses from DB
    {"id": "mount_dress_010010", "name": "Hồng Liên Bôn Lôi (Lótus Carmesim do Trovão)", "rel": "creature/PC_FEMALE_010010.swf", "type": "divine_mount", "mount_tier": 7},
    {"id": "mount_dress_010011", "name": "Hàn Sương Thiểm Điện (Relâmpago Congelante)", "rel": "creature/PC_FEMALE_010011.swf", "type": "divine_mount", "mount_tier": 7},
    {"id": "mount_dress_010012", "name": "Viễn Cổ Chiến Hùng (Urso de Batalha Ancestral)", "rel": "creature/PC_FEMALE_010012.swf", "type": "divine_mount", "mount_tier": 8},
    {"id": "mount_dress_010016", "name": "Huyễn Ảnh Linh Hồ (Raposa Espectral Fantasma)", "rel": "creature/PC_FEMALE_010016.swf", "type": "divine_mount", "mount_tier": 8},
    {"id": "mount_dress_010017", "name": "Kim Quang Thần Thú (Fera Dourada Celestial)", "rel": "creature/PC_FEMALE_010017.swf", "type": "divine_mount", "mount_tier": 9},
    {"id": "mount_dress_010018", "name": "Tử Lôi Ma Thú (Besta Demoníaca do Trovão Roxo)", "rel": "creature/PC_FEMALE_010018.swf", "type": "divine_mount", "mount_tier": 9},
    {"id": "mount_dress_010019", "name": "Bá Vương Thánh Long (Dragão Sagrado Soberano)", "rel": "creature/PC_FEMALE_010019.swf", "type": "mythic_mount", "mount_tier": 10},
    {"id": "mount_dress_010020", "name": "Vĩnh Hằng Chí Tôn (Montaria Suprema da Eternidade)", "rel": "creature/PC_FEMALE_010020.swf", "type": "mythic_mount", "mount_tier": 10}
]

catalog_mounts = []

for m in mount_candidates:
    rel = m["rel"]
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    if h in files:
        swf_path = os.path.join(RES_DIR, h)
        out_dir = os.path.join(OUT_BASE, m["id"])
        print(f"Extracting mount {m['name']} ({rel})...")
        try:
            bitmaps, anim_frames = parse_swf(swf_path)
            if bitmaps:
                pack_atlas(bitmaps, anim_frames, out_dir, model_name=m["id"], extra_meta=m)
                
                # Thumb
                first_bmp = list(bitmaps.values())[0]
                thumb = first_bmp.copy()
                thumb.thumbnail((80, 80), Image.Resampling.LANCZOS)
                thumb_path = os.path.join(out_dir, "thumb.webp")
                thumb.save(thumb_path, "WEBP", quality=85)
                
                catalog_mounts.append({
                    "id": m["id"],
                    "name": m["name"],
                    "rel_path": rel,
                    "type": m["type"],
                    "tier": m["mount_tier"],
                    "atlas": f"assets/mounts/{m['id']}/atlas.webp",
                    "json": f"assets/mounts/{m['id']}/atlas.json",
                    "meta": f"assets/mounts/{m['id']}/visual_meta.json",
                    "thumb": f"assets/mounts/{m['id']}/thumb.webp"
                })
        except Exception as e:
            print(f"Error extracting mount {m['name']}: {e}")

catalog_data = {
    "total_mounts": len(catalog_mounts),
    "generated_at": "2026-11-02",
    "mounts": catalog_mounts
}

with open(os.path.join(OUT_BASE, "catalog.json"), "w", encoding="utf-8") as f:
    json.dump(catalog_data, f, indent=2, ensure_ascii=False)

print(f"All mounts extracted: {len(catalog_mounts)} mounts saved to {OUT_BASE}/catalog.json")
