import os, sys, hashlib, struct
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
res_dir = os.path.join(ws, 'mcgame', 'frontend', 's', 'res')

res_files = set(os.listdir(res_dir))
print(f"Total files in mcgame/frontend/s/res: {len(res_files)}")

# 1. Inspect file signatures (SWF, PNG, JPEG, MP3, WAV, etc.)
types_count = Counter()
sizes_by_type = defaultdict(int)

for fname in res_files:
    fpath = os.path.join(res_dir, fname)
    try:
        with open(fpath, 'rb') as f:
            header = f.read(16)
        sz = os.path.getsize(fpath)
        
        # Check signature
        if header.startswith(b'CWS') or header.startswith(b'FWS') or header.startswith(b'ZWS'):
            t = 'SWF (Flash Movie/Animation)'
        elif header.startswith(b'\x89PNG\r\n\x1a\n'):
            t = 'PNG Image'
        elif header.startswith(b'\xff\xd8\xff'):
            t = 'JPEG Image'
        elif header.startswith(b'RIFF') and b'WAVE' in header:
            t = 'WAV Audio'
        elif header.startswith(b'ID3') or header[:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2']:
            t = 'MP3 Audio'
        elif header.startswith(b'PK\x03\x04'):
            t = 'ZIP / Package'
        else:
            t = 'Binary / Data / Other'
            
        types_count[t] += 1
        sizes_by_type[t] += sz
    except Exception as e:
        pass

print("\n--- Summary of File Types in `res/` by Magic Bytes ---")
for t, cnt in types_count.most_common():
    sz_mb = sizes_by_type[t] / (1024 * 1024)
    print(f"  * {t}: {cnt:,} files ({sz_mb:.2f} MB)")
