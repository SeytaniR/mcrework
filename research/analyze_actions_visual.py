import json
from PIL import Image

base = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web"

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\char1\char_manifest.json") as f:
    m = json.load(f)

for action_id in range(8):
    key = f"0-{action_id}"
    frames = m.get(key, [])
    print(f"\n--- ACTION {action_id} ('{key}', {len(frames)} frames) ---")
    
    bboxes = []
    for fr in frames:
        p = base + "/" + fr["file"]
        im = Image.open(p)
        bb = im.getbbox()
        bboxes.append(bb)
    
    # Analyze bounding box changes: width, height, ymin (head), ymax (feet)
    min_head_y = min(b[1] for b in bboxes)
    max_head_y = max(b[1] for b in bboxes)
    max_foot_y = max(b[3] for b in bboxes)
    min_foot_y = min(b[3] for b in bboxes)
    avg_w = sum(b[2]-b[0] for b in bboxes) / len(bboxes)
    avg_h = sum(b[3]-b[1] for b in bboxes) / len(bboxes)
    print(f"  Width: avg={avg_w:.1f}, Height: avg={avg_h:.1f}")
    print(f"  Head Y: [{min_head_y}..{max_head_y}], Feet Y: [{min_foot_y}..{max_foot_y}]")
    print(f"  First bbox: {bboxes[0]}, Mid bbox: {bboxes[len(bboxes)//2]}, Last bbox: {bboxes[-1]}")
