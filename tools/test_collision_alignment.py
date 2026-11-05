import os, sys, json
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

with open('web/assets/maps/catalog.json', 'r', encoding='utf-8') as f:
    cat = json.load(f)

test_maps = [1, 2, 3, 4, 5, 9, 22]

for mid in test_maps:
    m = next(m for m in cat['maps'] if m['id'] == mid)
    bg_p = os.path.join('web', m['bg_image'])
    col_p = os.path.join('web', m.get('collision_bin', ''))
    if not os.path.exists(col_p):
        print(f"Map {mid}: col bin not found")
        continue
    with open(col_p, 'rb') as f_col:
        col_bytes = f_col.read()
    
    bw, bh = m['width'], m['height']
    cw, ch = m['col_width'], m['col_height']
    print(f"\n--- MAP {mid} ({m['name']}) ---")
    print(f"BG: {bw}x{bh}, COL_DIMS: {cw}x{ch}, bin_len: {len(col_bytes)}, bits: {len(col_bytes)*8}")
    
    # Let's check what PIL image we get if we render cw x ch
    # and overlay onto bg image (bw x bh)
    bg_img = Image.open(bg_p).convert("RGBA")
    
    # Mode '1' image:
    # Notice: In Flash: bit 0 is (idx & 7) == 0.
    # In PIL: mode '1' has 8 pixels per byte, MSB first!
    # Let's render byte by byte
    col_img = Image.new("L", (cw, ch), 0)
    col_pixels = col_img.load()
    
    # Sample a slice to test
    # In web/main.js: idx = iy * COL_WIDTH + ix; bit = (colBytes[byteIdx] & (1 << (idx & 7)))
    for y in range(min(ch, bh)):
        y_off = y * cw
        for x in range(min(cw, bw)):
            idx = y_off + x
            b_idx = idx >> 3
            if b_idx < len(col_bytes):
                bit = (col_bytes[b_idx] >> (idx & 7)) & 1
                col_pixels[x, y] = 255 if bit else 0
    
    # Save a small composite of corner and center
    comp = Image.new("RGBA", (bw, bh), (0,0,0,0))
    # Paste red overlay where NOT walkable (bit == 0)
    overlay = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ov_pixels = overlay.load()
    for y in range(0, bh, 2):
        for x in range(0, bw, 2):
            if x < cw and y < ch:
                if col_pixels[x, y] == 0:
                    ov_pixels[x, y] = (255, 0, 0, 120)
                else:
                    ov_pixels[x, y] = (0, 255, 0, 30)
                    
    res = Image.alpha_composite(bg_img, overlay)
    out_debug = f"tools/debug_col_map_{mid}.jpg"
    res.convert("RGB").save(out_debug, "JPEG", quality=75)
    print(f"Saved {out_debug}")
