import sys, os, hashlib, json, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

RES_DIR = 'mcgame/frontend/s/res'
res_files = set(os.listdir(RES_DIR))

word2_list = [
    "", "EFF_", "FIRE_", "NORMAL_", "LOCAL_", "GLOBAL_",
    "STAGE_", "BATTLE_", "PLAYER_", "CRE_", "NPC_", "UI_",
    "SCREEN_", "SIDE_", "FUNC_", "WEAPON_", "WING_", "FLY_",
]

found_effects = {}
found_bullets = {}
found_icons = {}

# Also test numbers up to 50000
t0 = time.time()
for num in range(1, 50000):
    for w2 in word2_list:
        p_eff = f"resource/effect/EFF_{w2}{num:06d}.swf"
        h = hashlib.md5(p_eff.encode('utf-8')).hexdigest()
        if h in res_files:
            found_effects[p_eff] = h

        p_blt = f"resource/bullet/BLT_{w2}{num:06d}.swf"
        h_b = hashlib.md5(p_blt.encode('utf-8')).hexdigest()
        if h_b in res_files:
            found_bullets[p_blt] = h_b

print(f"Effects found: {len(found_effects)}")
print(f"Bullets found: {len(found_bullets)}")

with open('tools/all_found_effects.json', 'w', encoding='utf-8') as f:
    json.dump({'effects': found_effects, 'bullets': found_bullets}, f, indent=2)
