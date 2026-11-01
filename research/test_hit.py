import hashlib, os

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing_files = set(os.listdir(res_dir))

tests = [
    "resource/scene/SCENE_FOLDER_000001/MAP_HIT_NEW.swf",
    "resource/scene/SCENE_FOLDER_000001/MAP_HIT.swf",
    "scene/SCENE_FOLDER_000001/MAP_HIT_NEW.swf",
    "scene/SCENE_FOLDER_000001/MAP_HIT.swf",
    "resource/scene/SCENE_FOLDER_000001/MAP_MASK.png",
    "resource/scene/SCENE_FOLDER_000001/MAP_MASK.swf",
    "resource/scene/SCENE_FOLDER_000001/MAP_TOP.png",
    "resource/scene/SCENE_FOLDER_000001/MAP_TOP.swf",
    "resource/scene/SCENE_FOLDER_000001/MAP_HIT_NEW.png",
]

for t in tests:
    h = hashlib.md5(t.encode("utf-8")).hexdigest()
    if h in existing_files:
        size = os.path.getsize(os.path.join(res_dir, h))
        print(f"FOUND! '{t}' -> {h} ({size} bytes)")
