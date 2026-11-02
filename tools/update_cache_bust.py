import os

web_dir = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web"
main_js_path = os.path.join(web_dir, "main.js")
index_html_path = os.path.join(web_dir, "index.html")

with open(main_js_path, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('fetch("assets/characters/catalog.json")', 'fetch("assets/characters/catalog.json?v=1.2.1")')
c = c.replace('fetch("assets/monsters/catalog.json")', 'fetch("assets/monsters/catalog.json?v=1.2.1")')
c = c.replace('fetch("assets/mounts/catalog.json")', 'fetch("assets/mounts/catalog.json?v=1.2.1")')
c = c.replace('fetch("assets/npcs/catalog.json")', 'fetch("assets/npcs/catalog.json?v=1.2.1")')

with open(main_js_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(c)

with open(index_html_path, "r", encoding="utf-8") as f:
    h = f.read()

h = h.replace('style.css?v=1.2.0', 'style.css?v=1.2.1')
h = h.replace('main.js?v=1.2.0', 'main.js?v=1.2.1')

with open(index_html_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(h)

print("Cache busting updated to v=1.2.1 successfully")
