import sys, os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('web/main.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Find the marker where skills modal starts
split_marker = "// ==========================================\n  // MODAL 6: GRIMÓRIO DE HABILIDADES"
if split_marker not in code:
    # Try with  if encoding altered it
    import re
    m = re.search(r'// ==========================================\s+// MODAL 6: GRIM.*?DE HABILIDADES', code)
    if m:
        split_pos = m.start()
    else:
        print("Error: Could not find skills modal marker!")
        sys.exit(1)
else:
    split_pos = code.find(split_marker)

base_code = code[:split_pos].rstrip()
skills_code = code[split_pos:].strip()

# Now find where initGame ends in base_code
end_marker = 'console.log("Magic Campus Mobile Engine inicializado com sucesso!");'
if end_marker not in base_code:
    print("Error: Could not find end_marker in base_code!")
    sys.exit(1)

# Also expose playSkillVFX and executeSkill in window.__gameEngine
if 'playSkillVFX,' not in base_code:
    base_code = base_code.replace('testPlayerSkill,', 'testPlayerSkill,\n    playSkillVFX,\n    executeSkill,\n    openSkillsModal,', 1)

# Insert skills_code before console.log(...)
insert_pos = base_code.find(end_marker)
new_code = base_code[:insert_pos] + "\n  " + skills_code + "\n\n  " + base_code[insert_pos:]

with open('web/main.js', 'w', encoding='utf-8') as f:
    f.write(new_code)

print("Moved skills modal inside initGame() successfully!")
