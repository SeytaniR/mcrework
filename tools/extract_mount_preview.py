import os, sys, hashlib
from extract_monster import extract_swf

res_dir = r"mcgame/frontend/s/res"

def extract_preview(rel, out_dir):
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    path = os.path.join(res_dir, h)
    os.makedirs(out_dir, exist_ok=True)
    images = extract_swf(path, out_dir)
    print(f"Extracted {len(images)} images from {rel} to {out_dir}")

extract_preview("creature/PC_MALE_100001.swf", "test_out/male_100001")
extract_preview("creature/PC_FEMALE_010010.swf", "test_out/female_010010")
