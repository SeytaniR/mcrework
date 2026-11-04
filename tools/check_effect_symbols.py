import json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('tools/found_effects.json', 'r') as f:
    effs = json.load(f)

from inspect_effects_deep import inspect_swf

for num in [1, 2, 6, 301, 302, 310, 402, 410, 10001, 10008]:
    p = f'resource/effect/EFF_PLAYER_{num:06d}.swf'
    h = effs.get(p)
    if h:
        info = inspect_swf(h)
        print(f"Num {num:5d}: sprites={info['sprites']}, frames={info['sprite_frames']}, symbols={info['symbols']}")
