import zlib, struct, os, json
from PIL import Image

path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res\c3f43ddd342956b8d22490808a5cc3c7"
with open(path, "rb") as f:
    data = f.read()

decomp = zlib.decompress(data[8:])
full = b"FWS\t" + data[4:8] + decomp

pos = 8
nbits = full[pos] >> 3
pos += (5 + nbits * 4 + 7) // 8 + 4

mask_items = []
# In MAP_MASK.swf, let's extract all DefineBitsJPEG3 sizes and find matching matrices in Shape 8
# Shape 8 starts around offset...
while pos < len(full):
    hdr = int.from_bytes(full[pos:pos+2], "little")
    t_type = hdr >> 6
    t_len = hdr & 0x3F
    pos += 2
    if t_len == 0x3F:
        t_len = int.from_bytes(full[pos:pos+4], "little")
        pos += 4
    if t_type in (2, 22):
        tag_bytes = full[pos:pos+t_len]
        sid = int.from_bytes(tag_bytes[:2], "little")
        # In DefineShape, let's scan for Matrix records:
        # A matrix record following a fillstyle 0x41/0x40/0x42
        for i in range(len(tag_bytes) - 10):
            # FillStyleType: 0x40, 0x41, 0x42, 0x43 (repeating/clipped bitmap)
            if tag_bytes[i] in (0x40, 0x41, 0x42, 0x43):
                bitmap_id = int.from_bytes(tag_bytes[i+1:i+3], "little")
                if 1 <= bitmap_id <= 7:
                    # Matrix follows immediately at i+3
                    m_data = tag_bytes[i+3:]
                    b_stream = "".join(f"{b:08b}" for b in m_data[:16])
                    b_idx = 0
                    has_scale = int(b_stream[b_idx]); b_idx += 1
                    if has_scale:
                        n_scale_bits = int(b_stream[b_idx:b_idx+5], 2)
                        b_idx += 5 + n_scale_bits * 2
                    has_rotate = int(b_stream[b_idx]); b_idx += 1
                    if has_rotate:
                        n_rotate_bits = int(b_stream[b_idx:b_idx+5], 2)
                        b_idx += 5 + n_rotate_bits * 2
                    n_trans_bits = int(b_stream[b_idx:b_idx+5], 2); b_idx += 5
                    if n_trans_bits > 0 and len(b_stream) >= b_idx + n_trans_bits * 2:
                        raw_tx = int(b_stream[b_idx:b_idx+n_trans_bits], 2)
                        if raw_tx & (1 << (n_trans_bits - 1)): raw_tx -= (1 << n_trans_bits)
                        b_idx += n_trans_bits
                        raw_ty = int(b_stream[b_idx:b_idx+n_trans_bits], 2)
                        if raw_ty & (1 << (n_trans_bits - 1)): raw_ty -= (1 << n_trans_bits)
                        tx = raw_tx / 20.0
                        ty = raw_ty / 20.0
                        mask_items.append({
                            "bitmap_id": bitmap_id,
                            "file": f"assets/map1/mask/mask_{bitmap_id}.png",
                            "x": tx,
                            "y": ty
                        })
    pos += t_len

# Filter duplicates
unique_items = []
seen = set()
for item in mask_items:
    k = (item["bitmap_id"], round(item["x"], 1), round(item["y"], 1))
    if k not in seen:
        seen.add(k)
        unique_items.append(item)

print(f"Total unique mask placements found: {len(unique_items)}")
for it in unique_items:
    print(f"  Mask {it['bitmap_id']}: ({it['x']:.1f}, {it['y']:.1f}) -> {it['file']}")

out_json = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\masks.json"
with open(out_json, "w", encoding="utf-8") as out:
    json.dump(unique_items, out, indent=2)
