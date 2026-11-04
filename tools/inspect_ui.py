import os, re

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html_path = os.path.join(base_dir, "web", "index.html")

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

buttons = re.findall(r'id=["\'](btn-[a-zA-Z0-9\-_]+)["\']', html)
print("Total buttons found:", len(buttons))
for b in buttons:
    print("  ", b)

modals = re.findall(r'id=["\'](modal-[a-zA-Z0-9\-_]+)["\']', html)
print("Modals found:", modals)
