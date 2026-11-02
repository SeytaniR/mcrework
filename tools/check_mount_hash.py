import os, sys, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

res_dir = r"mcgame/frontend/s/res"
files = set(os.listdir(res_dir))

mount_res_codes = [
    ("U Linh Hổ", 2050080010004),
    ("Hổ Vàng Răng Kiếm", 2050080010006),
    ("Bông Gòn", 2050080010007),
    ("Viêm Lang", 2050080010008),
    ("Cửu Vĩ Hồ", 2050080010009),
    ("Hồng Liên Bôn Lôi", 2050080010010),
    ("Hàn Sương Thiểm Điện", 2050080010011),
    ("Viễn Cổ Chiến Hùng", 2050080010012)
]

# Let's test different interpretations of rc
for name, rc in mount_res_codes:
    print(f"\n--- {name} (rc={rc}) ---")
    rem = rc % 1000000000000
    w1_id = rem // 1000000000
    rem2 = rem % 1000000000
    w2_id = rem2 // 1000000
    num = rem2 % 1000000
    print(f"w1_id={w1_id}, w2_id={w2_id}, num={num}")
    
    # Try various patterns
    candidates = [
        f"creature/MOUNT_{num:06d}.swf",
        f"creature/NPC_CRE_{num:06d}.swf",
        f"creature/PC_MALE_{num:06d}.swf",
        f"item/MOUNT_{num:06d}.swf",
        f"item/{num}.swf",
        f"creature/{num}.swf",
        f"creature/PC_MALE_1{num:05d}.swf"
    ]
    for c in candidates:
        h = hashlib.md5(f"resource/{c}".encode("utf-8")).hexdigest()
        if h in files:
            print(f"  FOUND: {c} -> hash={h}")
        # also check if any file in res has this hash without 'resource/'
        h2 = hashlib.md5(c.encode("utf-8")).hexdigest()
        if h2 in files:
            print(f"  FOUND (no prefix): {c} -> hash={h2}")
