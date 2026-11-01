import os, struct, zlib, json
from PIL import Image
import io

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, r"mcgame\frontend\s\res")
WEB_DIR = os.path.join(BASE_DIR, "web")
OUT_DIR = os.path.join(WEB_DIR, "assets", "char11")
os.makedirs(OUT_DIR, exist_ok=True)

char11_hash = "05a8cd74b99040be44e03b52f6ff1adb"
swf_path = os.path.join(RES_DIR, char11_hash)

print("Reading SWF...")
with open(swf_path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
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
            # Crop to 200x150 around feet at (400, 376) -> (300, 266, 500, 416)
            cropped = img.crop((300, 266, 500, 416))
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
            cropped = img.crop((300, 266, 500, 416))
            bitmaps[cid] = cropped
        except Exception as e:
            print(f"Error JPEG3 cid={cid}: {e}")
    elif t_type == 26: # PlaceObject2
        flags = tag_data[0]
        if flags & 0x02:
            cid = int.from_bytes(tag_data[3:5], "little")
            placements[frame_idx] = cid

    pos += t_len

print(f"Loaded {len(bitmaps)} bitmaps, {len(labels)} labels, {len(placements)} placements, {frame_idx} frames")

# Build animation frames grouped by label
animations = {}
current_lbl = None

for f_num in range(1, frame_idx):
    if f_num in labels:
        current_lbl = labels[f_num]

    if not current_lbl:
        continue

    # Find placed cid
    placed_cid = None
    for p_f in range(f_num, 0, -1):
        if p_f in placements:
            placed_cid = placements[p_f]
            break

    if placed_cid:
        # In SWF tag 26, placed_cid is the Shape ID (which is bmp_id + 1)
        bmp_id = placed_cid - 1
        if bmp_id in bitmaps:
            img = bitmaps[bmp_id]
            filename = f"frame_{f_num}_{current_lbl}.png"
            filepath = os.path.join(OUT_DIR, filename)
            img.save(filepath)

            animations.setdefault(current_lbl, []).append({
                "frame": f_num,
                "file": f"assets/char11/{filename}",
                "width": 200,
                "height": 150
            })

# Deduplicate consecutive identical files
clean_manifest = {}
for lbl, f_list in animations.items():
    unique = []
    seen = set()
    for item in f_list:
        if item["file"] not in seen:
            seen.add(item["file"])
            unique.append(item)
    clean_manifest[lbl] = unique

manifest_path = os.path.join(OUT_DIR, "char_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as out:
    json.dump(clean_manifest, out, indent=2)

print(f"SUCCESS: Generated char11 manifest with {len(clean_manifest)} animations!")
# Print actions summary
actions = sorted(set(k.split("-")[1] for k in clean_manifest.keys()), key=lambda x: int(x) if x.isdigit() else 99)
print(f"Extracted actions for char11: {actions}")
for act in actions:
    print(f"  Action {act}: dir 0 has {len(clean_manifest.get(f'0-{act}', []))} frames")
