import os, sys, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
ffdec_jar = os.path.join(ws, 'tools', 'ffdec', 'ffdec.jar')
res_dir = os.path.join(ws, 'mcgame', 'frontend', 's', 'res')

# Let's inspect EQUIP_WING_001001 (hash: cd8b971ccc23f34b1fadc4aafa7e449a)
wing_hash = "cd8b971ccc23f34b1fadc4aafa7e449a"
wing_swf = os.path.join(res_dir, wing_hash)

temp_out = os.path.join(ws, 'tools', 'test_wing')
os.makedirs(temp_out, exist_ok=True)

# Copy with .swf extension
temp_swf = os.path.join(temp_out, "EQUIP_WING_001001.swf")
shutil.copyfile(wing_swf, temp_swf)

# Run ffdec to export shapes/images/frames
print("Exporting EQUIP_WING_001001 via ffdec...")
cmd = ['java', '-jar', ffdec_jar, '-export', 'image,frame', os.path.join(temp_out, 'export'), temp_swf]
res = subprocess.run(cmd, capture_output=True, text=True)
print("FFDec return code:", res.returncode)
if res.stderr:
    print("FFDec stderr:", res.stderr[:500])

export_dir = os.path.join(temp_out, 'export')
if os.path.exists(export_dir):
    for sub in os.listdir(export_dir):
        sub_path = os.path.join(export_dir, sub)
        if os.path.isdir(sub_path):
            files = os.listdir(sub_path)
            print(f"  Folder {sub}: {len(files)} files (e.g. {files[:5]})")
        else:
            print(f"  File {sub}")
