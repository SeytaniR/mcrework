import hashlib, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

res_dir = r"mcgame/frontend/s/res"
files = set(os.listdir(res_dir))

# Check all possible PC_MALE_ and PC_FEMALE_ numbers
male_swfs = []
female_swfs = []
for i in range(150000):
    rel_m = f"creature/PC_MALE_{i:06d}.swf"
    h_m = hashlib.md5(f"resource/{rel_m}".encode("utf-8")).hexdigest()
    if h_m in files:
        male_swfs.append((i, rel_m, h_m))
    rel_f = f"creature/PC_FEMALE_{i:06d}.swf"
    h_f = hashlib.md5(f"resource/{rel_f}".encode("utf-8")).hexdigest()
    if h_f in files:
        female_swfs.append((i, rel_f, h_f))

print(f"Total PC_MALE found: {len(male_swfs)}")
for m in male_swfs:
    print(" ", m[0], m[1])

print(f"Total PC_FEMALE found: {len(female_swfs)}")
for f in female_swfs:
    print(" ", f[0], f[1])
