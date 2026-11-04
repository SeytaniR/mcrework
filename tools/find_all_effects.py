import sys, os, hashlib, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

RES_DIR = 'mcgame/frontend/s/res'
res_files = set(os.listdir(RES_DIR))
print(f'Total files in res: {len(res_files)}')

# All word2 prefixes in GamePredef
word2_list = [
    "", "EFF_", "FIRE_", "NORMAL_", "LOCAL_", "GLOBAL_",
    "STAGE_", "BATTLE_", "PLAYER_", "CRE_", "NPC_", "UI_",
    "SCREEN_", "SIDE_", "FUNC_", "WEAPON_", "WING_", "FLY_",
    "FC1_", "FC2_", "FC3_", "FC4_", "FC5_", "FC6_",
    "MC1_", "MC2_", "MC3_", "MC4_", "MC5_", "MC6_",
    "FOLDER_", "TREE_", "FLOWER_", "HOUSE_", "SPAWN_", "DESERT_", "FOREST_", "MALE_", "FEMALE_"
]

t0 = time.time()
found_effects = {}

# Try ranges: 1 to 20000 with 6-digit formatting and plain formatting
for num in range(1, 25000):
    for w2 in word2_list:
        # candidate patterns for effect
        patterns = [
            f"resource/effect/EFF_{w2}{num:06d}.swf",
            f"resource/effect/{w2}{num:06d}.swf",
            f"resource/effect/EFF_{w2}{num}.swf",
            f"resource/effect/{w2}{num}.swf",
            f"resource/skill/SKILL_{w2}{num:06d}.swf",
            f"resource/skill/{w2}{num:06d}.swf",
        ]
        for p in patterns:
            h = hashlib.md5(p.encode('utf-8')).hexdigest()
            if h in res_files:
                found_effects[p] = h

t1 = time.time()
print(f'Scan completed in {t1 - t0:.2f}s! Found {len(found_effects)} effect/skill SWFs:')
for p, h in sorted(found_effects.items())[:30]:
    print(f'  {p} -> {h}')
if len(found_effects) > 30:
    print(f'  ... and {len(found_effects) - 30} more!')

with open('tools/found_effects.json', 'w', encoding='utf-8') as f_out:
    import json
    json.dump(found_effects, f_out, indent=2)
print('Saved to tools/found_effects.json')
