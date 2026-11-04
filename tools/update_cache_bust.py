import sys, os, re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

TARGET_VERSION = "1.4.0"

# 1. Update index.html
with open('web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'style\.css\?v=[0-9a-zA-Z\.\-]+', f'style.css?v={TARGET_VERSION}', html)
html = re.sub(r'main\.js\?v=[0-9a-zA-Z\.\-]+', f'main.js?v={TARGET_VERSION}', html)

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update main.js
with open('web/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

js = re.sub(r'catalog\.json\?v=[0-9a-zA-Z\.\-]+', f'catalog.json?v={TARGET_VERSION}', js)
js = re.sub(r'collision\.bin\?v=[0-9a-zA-Z\.\-]+', f'collision.bin?v={TARGET_VERSION}', js)

with open('web/main.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"Updated cache bust version to v={TARGET_VERSION} in index.html and main.js!")
