import os, sys, re, hashlib
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
url_util_path = os.path.join(ws, 'mcgame', 'docs', 'client', 'utils', 'UrlUtil.as')
res_dir = os.path.join(ws, 'mcgame', 'frontend', 's', 'res')

res_files = set(os.listdir(res_dir))
print(f"Total hashed files in res: {len(res_files)}")

with open(url_util_path, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

# Find getResUrl function
lines = code.splitlines()
in_func = False
func_lines = []
for l in lines:
    if 'public static function getUrl(' in l:
        in_func = True
    if in_func:
        func_lines.append(l)
        if len(func_lines) > 80:
            break

print("getUrl snippet:")
for l in func_lines:
    print("  ", l)
