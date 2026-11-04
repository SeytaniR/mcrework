main_js_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\main.js"
with open(main_js_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("playerShadow", "shadow")
with open(main_js_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: Replaced playerShadow with shadow in main.js!")
