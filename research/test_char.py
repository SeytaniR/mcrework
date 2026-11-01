import hashlib, os

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing_files = set(os.listdir(res_dir))

paths = [
    "resource/creature/PC_MALE_000001.swf",
    "resource/creature/PC_FEMALE_000001.swf",
    "resource/creature/PC_MALE_000011.swf",
    "resource/creature/PC_FEMALE_000011.swf",
    "creature/PC_MALE_000001.swf",
    "creature/PC_FEMALE_000001.swf"
]

for p in paths:
    h = hashlib.md5(p.encode("utf-8")).hexdigest()
    if h in existing_files:
        size = os.path.getsize(os.path.join(res_dir, h))
        print(f"FOUND CHARACTER SWF: '{p}' -> {h} ({size} bytes)")
    else:
        print(f"Not found: '{p}' -> {h}")
