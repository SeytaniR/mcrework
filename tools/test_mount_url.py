import hashlib, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

res_dir = r"mcgame/frontend/s/res"
files = set(os.listdir(res_dir))

def get_url(rc):
    URL_WORD_EXT = 1000000000000
    URL_WORD_1 = 1000000000
    URL_WORD_2 = 1000000
    URL_NUM_LENGTH = 6
    
    FOLDER = {15: "scene/", 20: "sitem/", 30: "item/", 40: "tile/", 50: "creature/", 60: "creature/", 70: "item/", 80: "effect/", 90: "sound/", 100: "bullet/", 110: "emotion/", 120: "state/", 130: "ui/", 140: "skill/"}
    WORD1 = {10: "", 15: "SCENE_", 20: "SITEM_", 30: "ITEM_", 40: "TILE_", 50: "PC_", 60: "NPC_", 70: "EQUIP_", 80: "EFF_", 90: "WAV_", 100: "BLT_", 110: "EM_", 120: "ST_", 130: "UI_", 140: "SKILL_"}
    WORD2 = {10: "", 15: "FOLDER_", 16: "FLOWER_", 20: "TREE_", 30: "HOUSE_", 40: "SPAWN_", 50: "DESERT_", 60: "FOREST_", 70: "MALE_", 80: "FEMALE_", 90: "FUNC_", 100: "CRE_", 110: "WEAPON_", 120: "SCENE_", 130: "PLAYER_", 140: "SIDE_", 150: "SCREEN_", 160: "NPC_", 170: "UI_", 180: "EFF_", 190: "FIRE_", 200: "NORMAL_", 210: "LOCAL_", 220: "GLOBAL_", 230: "STAGE_", 240: "BATTLE_", 250: "LOADING_", 260: "FC1_", 270: "FC2_", 280: "FC3_", 290: "FC4_", 300: "FC5_", 310: "FC6_", 320: "MC1_", 330: "MC2_", 340: "MC3_", 350: "MC4_", 360: "MC5_", 370: "MC6_", 380: "FLY_", 390: "WING_"}
    EXT = {0: "", 1: ".swf", 2: ".swf", 3: ".jpg", 4: ".png"}

    ext_id = int(rc // URL_WORD_EXT)
    rc = rc % URL_WORD_EXT
    w1_id = int(rc // URL_WORD_1)
    rc = rc % URL_WORD_1
    w2_id = int(rc // URL_WORD_2)
    num_str = str(rc)[-URL_NUM_LENGTH:].zfill(URL_NUM_LENGTH)
    
    folder = FOLDER.get(w1_id, "creature/")
    w1 = WORD1.get(w1_id, "")
    w2 = WORD2.get(w2_id, "")
    ext = EXT.get(ext_id, ".swf")
    
    path = f"{folder}{w1}{w2}{num_str}{ext}"
    return path

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

for name, rc in mount_res_codes:
    rel = get_url(rc)
    h = hashlib.md5(f"resource/{rel}".encode("utf-8")).hexdigest()
    exists = h in files
    print(f"{name}: {rc} -> {rel} (hash={h}, exists={exists})")
