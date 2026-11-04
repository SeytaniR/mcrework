import sys, os, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

print("Starting clean gh-pages deployment for v1.5.4...")

# 1. Checkout gh-pages
print("Checking out gh-pages...")
subprocess.run(['git', 'checkout', 'gh-pages'], check=True)

# 2. Checkout web/ contents from main directly into root of gh-pages
print("Checking out web/ contents from main...")
subprocess.run(['git', 'checkout', 'main', '--', 'web'], check=True)

# 3. Move files from web/ to root
print("Moving files from web/ to root...")
web_dir = 'web'
if os.path.exists(web_dir):
    for item in os.listdir(web_dir):
        s = os.path.join(web_dir, item)
        d = os.path.join('.', item)
        if os.path.isdir(s):
            if os.path.exists(d):
                for root, dirs, files in os.walk(s):
                    rel = os.path.relpath(root, s)
                    target_root = os.path.join(d, rel)
                    os.makedirs(target_root, exist_ok=True)
                    for f in files:
                        shutil.copyfile(os.path.join(root, f), os.path.join(target_root, f))
            else:
                shutil.copytree(s, d)
        else:
            shutil.copyfile(s, d)
    shutil.rmtree(web_dir, ignore_errors=True)

# 4. Stage ONLY web files on gh-pages
print("Staging web files on gh-pages...")
subprocess.run(['git', 'add', 'index.html', 'main.js', 'style.css', 'favicon.ico', 'assets/'], check=True)

# Remove any accidental tracked files if any exist
for item in ['tools', 'mcgame', 'extracted_char', 'action_previews']:
    subprocess.run(['git', 'rm', '-rf', '--cached', item], capture_output=True)

# 5. Commit
print("Committing on gh-pages...")
commit_msg = "deploy: v1.5.4 mobile ui fixes (costumes 4096 repack, flying mounts elevation bobbing, anti-squish skills layout)"
res = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

# 6. Push to origin gh-pages
print("Pushing to origin gh-pages...")
subprocess.run(['git', 'push', 'origin', 'gh-pages'], check=True)

# 7. Return to main
print("Returning to branch main...")
subprocess.run(['git', 'checkout', 'main'], check=True)
subprocess.run(['git', 'checkout', 'HEAD', '--', 'web'], check=True)

print("\nDeployment to gh-pages v1.5.3 completed successfully!")
