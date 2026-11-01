import hashlib, os, io

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing_files = set(os.listdir(res_dir))
print("Total files in res/ folder:", len(existing_files))

tests = [
    "resource/scene/SCENE_FOLDER_000001/MAP_0_0.jpg",
    "scene/SCENE_FOLDER_000001/MAP_0_0.jpg",
    "SCENE_FOLDER_000001/MAP_0_0.jpg",
    "SCENE_FOLDER_000001_MAP_0_0.jpg",
    "MAP_0_0.jpg",
    "resource/scene/SCENE_FOLDER_000001",
    "scene/SCENE_FOLDER_000001",
    "resource/ui/WorldMap1.jpg",
    "ui/WorldMap1.jpg",
    "WorldMap1.jpg",
    "res/4399.txt",
    "4399.txt"
]

matches = 0
for t in tests:
    h = hashlib.md5(t.encode('utf-8')).hexdigest()
    if h in existing_files:
        print(f"MATCH! '{t}' -> {h}")
        matches += 1

print(f"Direct tests completed. Matches: {matches}")
