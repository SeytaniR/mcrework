import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_JS_PATH = os.path.join(BASE_DIR, "web", "main.js")

with open(MAIN_JS_PATH, "r", encoding="utf-8") as f:
    code = f.read()

target = """              <div class="skill-icon-wrapper" style="background: radial-gradient(circle, #4c566a 20%, #2e3440 90%);">
                <span style="font-size: 20px;">⚡</span>
              </div>"""

replacement = """              <div class="skill-icon-wrapper" style="background: radial-gradient(circle, #4c566a 20%, #2e3440 90%);">
                <img src="${eff.thumb || `assets/effects/${eff.id}/thumb.png`}" alt="VFX #${eff.id}" class="vfx-thumb-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
                <span style="display:none; font-size: 20px;">⚡</span>
              </div>"""

if target in code:
    code = code.replace(target, replacement, 1)
    with open(MAIN_JS_PATH, "w", encoding="utf-8") as f:
        f.write(code)
    print("Successfully patched VFX cards to use real thumbnails!")
else:
    print("Target not found. Let's inspect characters.")
    pos = code.find('radial-gradient(circle, #4c566a 20%, #2e3440 90%)')
    print("Position in code:", pos)
    if pos != -1:
        print("Surrounding code:")
        print(repr(code[pos-50:pos+150]))
