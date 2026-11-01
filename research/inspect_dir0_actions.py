import json

with open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\char1\char_manifest.json") as f:
    m = json.load(f)

for action_id in range(8):
    key = f"0-{action_id}"
    frames = m.get(key, [])
    print(f"Action {action_id} ('{key}'): {len(frames)} frames")
    if frames:
        print(f"   First frame: {frames[0]['file']}")
        print(f"   Last frame:  {frames[-1]['file']}")
