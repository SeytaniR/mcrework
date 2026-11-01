import json
from PIL import Image

with open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\npcs.json', 'r', encoding='utf-8') as f:
    npcs = json.load(f)

img = Image.open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\collision.png')
w, h = img.size
print(f'Collision image size: {w}x{h}')

walkable_count = 0
for npc in npcs:
    x = int(npc['x'])
    y = int(npc['y'])
    val = img.getpixel((x, y)) if (0 <= x < w and 0 <= y < h) else -1
    is_walk = (val == 255)
    if is_walk:
        walkable_count += 1
    # Also check a 5x5 neighborhood around the NPC
    found_near = False
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and img.getpixel((nx, ny)) == 255:
                found_near = True
                break
        if found_near: break
    npc_id = npc.get('id', '?')
    print(f"NPC {npc_id} ({x}, {y}): exact={val} (walk={is_walk}), near_walk={found_near}")

print(f"Total NPCs exactly on walkable pixel: {walkable_count}/{len(npcs)}")
