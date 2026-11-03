import hashlib, os

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing = set(os.listdir(res_dir))

for mid in [1, 2, 3, 9, 10]:
    folder = f"resource/scene/SCENE_FOLDER_{mid:06d}"
    tiles = []
    for x in range(30):
        for y in range(30):
            p = f"{folder}/MAP_{x}_{y}.jpg"
            h = hashlib.md5(p.encode("utf-8")).hexdigest()
            if h in existing:
                tiles.append((x, y, os.path.getsize(os.path.join(res_dir, h))))
    print(f"Map {mid}: found {len(tiles)} tiles. Max X={max([t[0] for t in tiles], default=0)}, Max Y={max([t[1] for t in tiles], default=0)}")
