import os, shutil, json, struct, zlib
from PIL import Image
import io

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, r"mcgame\frontend\s\res")
WEB_DIR = os.path.join(BASE_DIR, "web")
os.makedirs(os.path.join(WEB_DIR, "assets", "map1"), exist_ok=True)
os.makedirs(os.path.join(WEB_DIR, "assets", "char1"), exist_ok=True)

# 1. Copy Map 1 Background
map1_hash = "36d51dd37392edf908666bced3544007"
shutil.copyfile(os.path.join(RES_DIR, map1_hash), os.path.join(WEB_DIR, "assets", "map1", "map1.jpg"))
print("Copied Map 1 background (2000x1500)!")

# 2. Extract Character 1 (Warrior Male: PC_MALE_000001.swf)
char1_hash = "b68e68f7e6ed33ca378b507e60664d2b"
swf_path = os.path.join(RES_DIR, char1_hash)

with open(swf_path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
full = b"FWS\t" + data[4:8] + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

bitmaps = {} # char_id -> PIL Image
shapes = {}  # shape_id -> (xmin, xmax, ymin, ymax)
labels = {}  # frame_idx -> label_name
placements = {} # frame_idx -> char_id

frame_idx = 1
current_label = "0-0"

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
        current_label = tag_data[:null_idx].decode("utf-8", errors="ignore")
        labels[frame_idx] = current_label
    elif t_type == 1: # ShowFrame
        frame_idx += 1
    elif t_type == 35: # DefineBitsJPEG3
        cid = int.from_bytes(tag_data[:2], "little")
        alpha_offset = int.from_bytes(tag_data[2:6], "little")
        jpeg_data = tag_data[6:6+alpha_offset]
        alpha_comp = tag_data[6+alpha_offset:]
        try:
            alpha_data = zlib.decompress(alpha_comp)
            img = Image.open(io.BytesIO(jpeg_data)).convert("RGBA")
            if len(alpha_data) == img.width * img.height:
                img.putalpha(Image.frombytes("L", (img.width, img.height), alpha_data))
            bitmaps[cid] = img
        except Exception as e:
            print(f"Error bitmap {cid}: {e}")
    elif t_type == 2: # DefineShape
        sid = int.from_bytes(tag_data[:2], "little")
        b_stream = "".join(f"{b:08b}" for b in tag_data[2:15])
        n_bits = int(b_stream[:5], 2)
        idx = 5
        vals = []
        for _ in range(4):
            v = int(b_stream[idx:idx+n_bits], 2)
            if v & (1 << (n_bits - 1)): v -= (1 << n_bits)
            idx += n_bits
            vals.append(v / 20.0)
        shapes[sid] = tuple(vals)
    elif t_type == 26: # PlaceObject2
        flags = tag_data[0]
        if flags & 0x02: # HasCharacter
            cid = int.from_bytes(tag_data[3:5], "little")
            placements[frame_idx] = cid

    pos += t_len

print(f"Loaded {len(bitmaps)} bitmaps, {len(shapes)} shapes, {len(labels)} labels, {len(placements)} placements")

# Save extracted images and build spritesheet manifest
# Group by label: 'dir-action'
# e.g., '0-0' (stand direction 0), '0-1' (walk direction 0)
sorted_frames = sorted(labels.keys())
animations = {}

# Map frames to labels
current_lbl = "0-0"
for f_num in range(1, frame_idx):
    if f_num in labels:
        current_lbl = labels[f_num]
    
    # Check if a character was placed at or before this frame
    # Find latest placement at or before f_num
    placed_cid = None
    for p_f in range(f_num, 0, -1):
        if p_f in placements:
            placed_cid = placements[p_f]
            break
            
    if placed_cid and placed_cid in shapes:
        # Bitmap ID is placed_cid - 1
        bmp_id = placed_cid - 1
        if bmp_id in bitmaps:
            img = bitmaps[bmp_id]
            bounds = shapes[placed_cid]
            # Save bitmap
            bmp_filename = f"frame_{f_num}_{current_lbl}.png"
            bmp_path = os.path.join(WEB_DIR, "assets", "char1", bmp_filename)
            img.save(bmp_path)
            
            if current_lbl not in animations:
                animations[current_lbl] = []
                
            animations[current_lbl].append({
                "frame": f_num,
                "file": f"assets/char1/{bmp_filename}",
                "width": img.width,
                "height": img.height,
                "bounds": {
                    "xmin": bounds[0],
                    "xmax": bounds[1],
                    "ymin": bounds[2],
                    "ymax": bounds[3]
                },
                # Anchor in PixiJS (0..1) relative to registration point (feet)
                # Bounds: xmin, xmax, ymin, ymax
                # Feet is at x=0, y=0 in Flash coordinates!
                # So offset of top-left relative to feet is (bounds[0], bounds[2])
                "pivot_x": -bounds[0],
                "pivot_y": -bounds[2]
            })

# Remove duplicate consecutive frames in each animation
clean_anims = {}
for lbl, f_list in animations.items():
    unique = []
    seen_files = set()
    for item in f_list:
        if item["file"] not in seen_files:
            seen_files.add(item["file"])
            unique.append(item)
    clean_anims[lbl] = unique

manifest_path = os.path.join(WEB_DIR, "assets", "char1", "char_manifest.json")
with open(manifest_path, "w", encoding="utf-8") as out:
    json.dump(clean_anims, out, indent=2)

print(f"Generated clean animation manifest with {len(clean_anims)} animations!")
print("Sample animation '0-0' frames:", len(clean_anims.get("0-0", [])))
print("Sample animation '0-1' frames:", len(clean_anims.get("0-1", [])))
