import json, os
from PIL import Image

base = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web"
with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\char1\char_manifest.json") as f:
    m = json.load(f)

# Create a contact sheet or GIF for each action 0..7
out_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\action_previews"
os.makedirs(out_dir, exist_ok=True)

for action_id in range(8):
    key = f"0-{action_id}"
    frames = m.get(key, [])
    if not frames: continue
    
    # Save an animated GIF of this action!
    images = []
    for fr in frames:
        p = os.path.join(base, fr["file"])
        im = Image.open(p).convert("RGBA")
        # Crop to character area around (100, 110)
        crop = im.crop((50, 0, 160, 130))
        images.append(crop)
        
    gif_path = os.path.join(out_dir, f"action_{action_id}.gif")
    images[0].save(gif_path, save_all=True, append_images=images[1:], duration=90, loop=0)
    print(f"Generated {gif_path} with {len(images)} frames")
