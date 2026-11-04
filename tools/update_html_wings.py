import os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
path = 'web/index.html'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update version
text = text.replace('style.css?v=1.5.1', 'style.css?v=1.5.2')
text = text.replace('main.js?v=1.5.1', 'main.js?v=1.5.2')

# 2. Add wing drawer item after weapon item
old_weapon_drawer = '''          <div class="stat-item" style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between;">
            <div>
              <span class="stat-label">Arma Empunhada:</span>
              <strong id="drawer-weapon" style="color: #ebcb8b;">Nenhuma (Desarmado)</strong>
            </div>
            <button id="btn-unequip-weapon" class="btn" style="display:none; padding: 2px 8px; font-size: 10px; border-radius: 10px; background: rgba(191, 97, 106, 0.2); color: #bf616a; border: 1px solid #bf616a;">🖐️ Desempunhar</button>
          </div>'''

new_weapon_and_wing_drawer = '''          <div class="stat-item" style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between;">
            <div>
              <span class="stat-label">Arma Empunhada:</span>
              <strong id="drawer-weapon" style="color: #ebcb8b;">Nenhuma (Desarmado)</strong>
            </div>
            <button id="btn-unequip-weapon" class="btn" style="display:none; padding: 2px 8px; font-size: 10px; border-radius: 10px; background: rgba(191, 97, 106, 0.2); color: #bf616a; border: 1px solid #bf616a;">🖐️ Desempunhar</button>
          </div>
          <div class="stat-item" style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between; margin-top: 2px;">
            <div>
              <span class="stat-label">Asas Equipadas:</span>
              <strong id="drawer-wing" style="color: #b48ead;">Nenhuma (Sem Asas)</strong>
            </div>
            <button id="btn-unequip-wing" class="btn" style="display:none; padding: 2px 8px; font-size: 10px; border-radius: 10px; background: rgba(191, 97, 106, 0.2); color: #bf616a; border: 1px solid #bf616a;">🪽 Desequipar</button>
          </div>'''

if old_weapon_drawer in text:
    text = text.replace(old_weapon_drawer, new_weapon_and_wing_drawer)
    print('Replaced weapon drawer with weapon + wing drawer')
else:
    print('Warning: old_weapon_drawer not found')

# 3. Add pill filter for wings
old_pill = '<button class="pill-filter" data-filter="wings_costumes">🪽 Asas & Visuais (334)</button>'
new_pill = '''<button class="pill-filter" data-filter="wings">🪽 Asas Animadas (36)</button>
        <button class="pill-filter" data-filter="wings_costumes">👗 Trajes & Visuais (334)</button>'''

if old_pill in text:
    text = text.replace(old_pill, new_pill)
    print('Updated pill filters for wings')
else:
    print('Warning: old_pill not found')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('index.html updated successfully!')
