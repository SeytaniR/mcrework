import sys

with open('web/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''          <div class="stat-item">
            <span class="stat-label">Sob Telhado/Árvore:</span>
            <strong id="drawer-occluded" style="color: #88c0d0;">NÃO (Visível)</strong>
          </div>'''

replacement = '''          <div class="stat-item">
            <span class="stat-label">Sob Telhado/Árvore:</span>
            <strong id="drawer-occluded" style="color: #88c0d0;">NÃO (Visível)</strong>
          </div>
          <div class="stat-item" style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between;">
            <div>
              <span class="stat-label">Arma Empunhada:</span>
              <strong id="drawer-weapon" style="color: #ebcb8b;">Nenhuma (Desarmado)</strong>
            </div>
            <button id="btn-unequip-weapon" class="btn" style="display:none; padding: 2px 8px; font-size: 10px; border-radius: 10px; background: rgba(191, 97, 106, 0.2); color: #bf616a; border: 1px solid #bf616a;">🖐️ Desempunhar</button>
          </div>'''

if target in content:
    content = content.replace(target, replacement, 1)
    print("Replaced drawer status item.")
else:
    # try normalized CRLF
    t_norm = target.replace('\r\n', '\n')
    c_norm = content.replace('\r\n', '\n')
    if t_norm in c_norm:
        content = c_norm.replace(t_norm, replacement.replace('\r\n', '\n'), 1)
        print("Replaced with LF.")
    else:
        print("Target not found in index.html!")

toast_tag = '<div id="toast-weapon" class="toast-weapon-equip"></div>'
if 'toast-weapon' not in content:
    content = content.replace('</body>', f'  {toast_tag}\n</body>')
    print("Added toast-weapon.")

# Bump version to 1.5.1
content = content.replace('main.js?v=1.5.0', 'main.js?v=1.5.1')

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("web/index.html updated successfully!")
