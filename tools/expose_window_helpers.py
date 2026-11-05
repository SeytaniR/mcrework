import os

MAIN_JS = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\main.js"
with open(MAIN_JS, "r", encoding="utf-8") as f:
    text = f.read()

target = 'console.log("Magic Campus Mobile Engine inicializado com sucesso!");'
replacement = '''console.log("Magic Campus Mobile Engine inicializado com sucesso!");
  window.switchMap = switchMap;
  window.player = player;
  window.maskSprites = maskSprites;
  window.getCurrentMapPortals = () => currentMapPortals;'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(MAIN_JS, "w", encoding="utf-8") as f:
        f.write(text)
    print("Successfully exposed window helpers!")
else:
    print("Target not found!")
