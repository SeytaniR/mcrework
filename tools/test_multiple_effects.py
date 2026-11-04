import sys, os, json, subprocess, shutil
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('tools/found_effects.json', 'r') as f:
    effs = json.load(f)

test_nums = [1, 3, 6, 9, 10, 20, 301, 402, 10001, 10008]

for num in test_nums:
    p = f"resource/effect/EFF_PLAYER_{num:06d}.swf"
    h = effs.get(p)
    if not h:
        continue
    out_tmp = f"tools/test_export_{num}"
    if os.path.exists(out_tmp):
        shutil.rmtree(out_tmp)
    
    cmd = ['java', '-jar', 'tools/ffdec/ffdec.jar', '-ignorebackground', '-format', 'sprite:png,frame:png', '-export', 'sprite,frame', out_tmp, f'mcgame/frontend/s/res/{h}']
    subprocess.run(cmd, capture_output=True)
    
    # Analyze output
    sprites_dir = os.path.join(out_tmp, 'sprites')
    frames_dir = os.path.join(out_tmp, 'frames')
    
    root_frames = len(os.listdir(frames_dir)) if os.path.exists(frames_dir) else 0
    sprite_counts = {}
    if os.path.exists(sprites_dir):
        for s in os.listdir(sprites_dir):
            sp_path = os.path.join(sprites_dir, s)
            if os.path.isdir(sp_path):
                sprite_counts[s] = len(os.listdir(sp_path))
    
    print(f"Effect {num:5d}: Root frames={root_frames}, Sprites={sprite_counts}")
    shutil.rmtree(out_tmp)
