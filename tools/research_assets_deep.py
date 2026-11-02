import os, re, hashlib, json

res_dir = r"mcgame/frontend/s/res"
files = set(os.listdir(res_dir))

print("=== 1. CHECKING data_tbl_mount.sql ===")
with open(r"mcgame/supabase/seeds/data_tbl_mount.sql", "r", encoding="utf-8", errors="ignore") as f:
    mount_sql = f.read()
print("Mount SQL sample (first 1000 chars):")
print(mount_sql[:1000])

print("\n=== 2. CHECKING data_tbl_mount_dress.sql ===")
with open(r"mcgame/supabase/seeds/data_tbl_mount_dress.sql", "r", encoding="utf-8", errors="ignore") as f:
    md_sql = f.read()
print(md_sql[:1000])

print("\n=== 3. CHECKING data_tbl_npc.sql ===")
with open(r"mcgame/supabase/seeds/data_tbl_npc.sql", "r", encoding="utf-8", errors="ignore") as f:
    npc_sql = f.read()
print(npc_sql[:1000])

print("\n=== 4. CHECKING NPC_FUNC SWFS IN RES ===")
func_swfs = {}
for i in range(10000):
    rel = f"creature/NPC_FUNC_{i:06d}.swf"
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    if h in files:
        func_swfs[i] = (rel, h, os.path.getsize(os.path.join(res_dir, h)))
print(f"Total NPC_FUNC SWFs found in res: {len(func_swfs)}")
for k in list(func_swfs.keys())[:10]:
    print(f"  NPC_FUNC_{k:06d}: {func_swfs[k][2]} bytes, hash={func_swfs[k][1]}")
