import sys, os, subprocess, shutil

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

print("Starting gh-pages deployment...")

# 1. Ensure working directory on main is clean
res = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
if res.stdout.strip():
    print("Warning: uncommitted changes on current branch:", res.stdout)

# 2. Checkout gh-pages
print("Checking out gh-pages...")
subprocess.run(['git', 'checkout', 'gh-pages'], check=True)

# 3. Checkout web/ files from main directly into root of gh-pages!
# In git: git checkout main -- web/
print("Checking out web/ contents from main...")
subprocess.run(['git', 'checkout', 'main', '--', 'web'], check=True)

# 4. Move files from web/ to root
print("Moving files from web/ to root...")
web_dir = 'web'
if os.path.exists(web_dir):
    for item in os.listdir(web_dir):
        s = os.path.join(web_dir, item)
        d = os.path.join('.', item)
        if os.path.isdir(s):
            if os.path.exists(d):
                # Copy tree
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

# 5. Stage all changes
print("Staging all changes on gh-pages...")
subprocess.run(['git', 'add', '-A'], check=True)

# 6. Commit
print("Committing on gh-pages...")
commit_msg = "deploy(skills): update gh-pages v1.4.0 with 1.923 skills and 128 VFX effects"
res = subprocess.run(['git', 'commit', '-m', commit_msg], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)

# 7. Push to origin gh-pages
print("Pushing to origin gh-pages...")
subprocess.run(['git', 'push', 'origin', 'gh-pages'], check=True)

# 8. Return to main
print("Returning to branch main...")
subprocess.run(['git', 'checkout', 'main'], check=True)

print("\nDeployment to gh-pages completed successfully!")
