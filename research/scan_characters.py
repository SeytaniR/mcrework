import os, hashlib

res_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\res"
existing_hashes = set(os.listdir(res_dir))
print(f"Total files in frontend/s/res: {len(existing_hashes)}")

def check_path(rel_path):
    h = hashlib.md5(f"resource/{rel_path}".encode("utf-8")).hexdigest()
    if h in existing_hashes:
        return h, os.path.getsize(os.path.join(res_dir, h))
    return None, 0

# Check PC_MALE variants
found_pc = []
for cid in range(1, 30):
    for pad in [f"{cid:06d}", f"{cid:05d}", f"{cid}"]:
        for prefix in ["PC_MALE_", "PC_FEMALE_", "creature/PC_MALE_", "creature/PC_FEMALE_"]:
            p = f"{prefix}{pad}.swf"
            h, sz = check_path(p)
            if h:
                found_pc.append((p, h, sz))

# Also check 100000 series (default / mounts / special)
for cid in [100000, 100001, 100002, 200000, 300000, 10000, 20000]:
    for prefix in ["PC_MALE_", "PC_FEMALE_", "creature/PC_MALE_", "creature/PC_FEMALE_"]:
        p = f"{prefix}{cid}.swf"
        h, sz = check_path(p)
        if h:
            found_pc.append((p, h, sz))

print(f"\nFound {len(found_pc)} PC characters:")
for p, h, sz in found_pc:
    print(f"  {p} -> {h} ({sz/1024:.1f} KB)")
