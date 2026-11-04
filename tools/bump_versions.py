import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_JS = os.path.join(BASE_DIR, "web", "main.js")
INDEX_HTML = os.path.join(BASE_DIR, "web", "index.html")

with open(MAIN_JS, "r", encoding="utf-8") as f:
    js = f.read()

js = js.replace("v=1.5.2", "v=1.5.3")
js = js.replace("v=1.5.1", "v=1.5.3")

with open(MAIN_JS, "w", encoding="utf-8") as f:
    f.write(js)

with open(INDEX_HTML, "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("v=1.5.0", "v=1.5.3")
html = html.replace("v=1.5.2", "v=1.5.3")

with open(INDEX_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Bumped all cache buster tags to v=1.5.3 in main.js and index.html!")
