import hashlib, os

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing_files = set(os.listdir(res_dir))

# Map 1: width=2000, height=1500
# Let's test tile dimensions: could be 100x100, 200x100, 256x256, 300x300, 500x500
found_tiles = {}
for x in range(50):
    for y in range(50):
        path = f"resource/scene/SCENE_FOLDER_000001/MAP_{x}_{y}.jpg"
        h = hashlib.md5(path.encode("utf-8")).hexdigest()
        if h in existing_files:
            file_size = os.path.getsize(os.path.join(res_dir, h))
            found_tiles[(x, y)] = (h, file_size)

print(f"Total tiles found for Map 1: {len(found_tiles)}")
if found_tiles:
    max_x = max(k[0] for k in found_tiles.keys())
    max_y = max(k[1] for k in found_tiles.keys())
    print(f"Max tile X: {max_x}, Max tile Y: {max_y}")
    print("Sample tiles:", list(found_tiles.items())[:5])
