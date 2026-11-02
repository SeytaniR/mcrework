import os, sys, hashlib, re, json, concurrent.futures
from PIL import Image
from batch_extract_assets import parse_swf, pack_atlas

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RES_DIR = r"mcgame/frontend/s/res"
OUT_BASE = r"web/assets/npcs"
os.makedirs(OUT_BASE, exist_ok=True)

files = set(os.listdir(RES_DIR))

# 1. Parse data_tbl_npc.sql for names and descriptions
npc_names_by_num = {}
with open(r"mcgame/supabase/seeds/data_tbl_npc.sql", "r", encoding="utf-8", errors="ignore") as f:
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
    if len(fields) >= 26:
        npc_id = fields[0]
        name = fields[14].strip("'")
        map_id = fields[17].strip("'") if len(fields) > 17 else ""
        res_code_str = fields[25].strip("'")
        try:
            rc = int(res_code_str)
            rem = rc % 1000000000000
            rem2 = rem % 1000000000
            num = rem2 % 1000000
            if num not in npc_names_by_num:
                npc_names_by_num[num] = []
            npc_names_by_num[num].append({"npc_id": npc_id, "name": name, "map_id": map_id})
        except Exception:
            pass

# 2. Collect all existing NPC SWFs
npc_tasks = []
for num in range(200000):
    rel = f"creature/NPC_FUNC_{num:06d}.swf"
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    if h in files:
        db_entries = npc_names_by_num.get(num, [])
        primary_name = db_entries[0]["name"] if db_entries else f"NPC {num}"
        npc_tasks.append({
            "num": num,
            "rel": rel,
            "hash": h,
            "name": primary_name,
            "db_entries": db_entries
        })

print(f"Total NPC SWFs to extract: {len(npc_tasks)}")

def process_npc(task):
    num = task["num"]
    rel = task["rel"]
    h = task["hash"]
    name = task["name"]
    swf_path = os.path.join(RES_DIR, h)
    out_dir = os.path.join(OUT_BASE, f"npc_{num:06d}")
    
    try:
        bitmaps, anim_frames = parse_swf(swf_path)
        if not bitmaps:
            return None
            
        extra_meta = {
            "name": name,
            "res_path": rel,
            "res_code_num": num,
            "type": "npc"
        }
        
        pack_atlas(bitmaps, anim_frames, out_dir, model_name=f"npc_{num:06d}", extra_meta=extra_meta)
        
        # Thumbnail
        first_bmp = list(bitmaps.values())[0]
        thumb = first_bmp.copy()
        thumb.thumbnail((80, 80), Image.Resampling.LANCZOS)
        thumb_path = os.path.join(out_dir, "thumb.webp")
        thumb.save(thumb_path, "WEBP", quality=85)
        
        return {
            "id": f"npc_{num:06d}",
            "name": name,
            "res_code_num": num,
            "atlas": f"assets/npcs/npc_{num:06d}/atlas.webp",
            "json": f"assets/npcs/npc_{num:06d}/atlas.json",
            "meta": f"assets/npcs/npc_{num:06d}/visual_meta.json",
            "thumb": f"assets/npcs/npc_{num:06d}/thumb.webp",
            "db_entries_count": len(task["db_entries"]),
            "db_id": task["db_entries"][0]["npc_id"] if task["db_entries"] else None,
            "map_id": task["db_entries"][0]["map_id"] if task["db_entries"] else None
        }
    except Exception as e:
        print(f"Error extracting NPC {num}: {e}")
        return None

# Process in parallel
catalog_npcs = []
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    results = list(executor.map(process_npc, npc_tasks))
    for res in results:
        if res:
            catalog_npcs.append(res)

catalog_npcs.sort(key=lambda x: x["res_code_num"])

catalog_data = {
    "total_npcs": len(catalog_npcs),
    "generated_at": "2026-11-02",
    "npcs": catalog_npcs
}

with open(os.path.join(OUT_BASE, "catalog.json"), "w", encoding="utf-8") as f:
    json.dump(catalog_data, f, indent=2, ensure_ascii=False)

print(f"Extraction finished! Total {len(catalog_npcs)} NPCs saved to {OUT_BASE}/catalog.json")
