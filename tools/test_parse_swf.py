import os, sys, hashlib
from batch_extract_assets import parse_swf

res_dir = r"mcgame/frontend/s/res"

def test_swf(rel):
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    path = os.path.join(res_dir, h)
    bitmaps, anim_frames = parse_swf(path)
    print(f"=== {rel} ===")
    print(f"  Bitmaps count: {len(bitmaps)}")
    print(f"  Anim frames: {list(anim_frames.keys())}")
    for k, v in list(anim_frames.items())[:5]:
        print(f"    {k}: {v}")

test_swf("creature/PC_MALE_100001.swf")
test_swf("creature/PC_FEMALE_010010.swf")
test_swf("creature/NPC_FUNC_000001.swf")
test_swf("creature/NPC_FUNC_000033.swf")
