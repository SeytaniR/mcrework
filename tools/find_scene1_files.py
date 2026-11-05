import os, hashlib

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
RES_DIR = os.path.join(BASE_DIR, "mcgame", "frontend", "s", "res")
existing_res = set(os.listdir(RES_DIR))

# Let's test different possible filenames in scene 1
prefixes = [
    "resource/scene/SCENE_FOLDER_000001",
    "resource/scene/1",
    "resource/scene/scene_1",
    "resource/scene/SCENE_FOLDER_1",
    "scene/1",
    "scene/SCENE_FOLDER_000001"
]

candidates = [
    "Mask.swf", "mask.swf", "MASK.swf",
    "Mask.png", "mask.png",
    "Hit.swf", "hit.swf",
    "MAP_HIT_NEW.swf",
    "MAP_MASK.swf", "MAP_MASK_NEW.swf",
    "MAP_COVER.swf", "Cover.swf", "cover.swf",
    "Alpha.swf", "alpha.swf",
    "Fore.swf", "fore.swf", "Foreground.swf",
    "Trans.swf", "trans.swf",
    "Building.swf", "building.swf"
]

found = []
for p in prefixes:
    for c in candidates:
        full_path = f"{p}/{c}"
        h = hashlib.md5(full_path.encode("utf-8")).hexdigest()
        if h in existing_res:
            found.append((full_path, h))

print(f"Found {len(found)} candidate files:")
for f, h in found:
    print(f"  {f} -> {h}")
