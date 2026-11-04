import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = r'web\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update main.js version tag
html = html.replace('main.js?v=1.4.0', 'main.js?v=1.5.0')
html = html.replace('style.css?v=1.4.0', 'style.css?v=1.5.0')

# 2. Add nav button
old_btn = '''      <button id="btn-open-skills-modal" class="nav-pill-btn nav-skills" title="Grimório de Habilidades & Efeitos Especiais (1.923 Habilidades / 128 Efeitos)">
        <span class="nav-icon">🔮</span>
        <span class="nav-txt">Habilidades <span class="nav-count">1923</span></span>
      </button>'''

new_btn = '''      <button id="btn-open-skills-modal" class="nav-pill-btn nav-skills" title="Grimório de Habilidades & Efeitos Especiais (1.923 Habilidades / 128 Efeitos)">
        <span class="nav-icon">🔮</span>
        <span class="nav-txt">Habilidades <span class="nav-count">1923</span></span>
      </button>
      <button id="btn-open-equipment-modal" class="nav-pill-btn nav-equipment" title="Armaria de Equipamentos, Armas e Conjuntos (1.865 Itens)">
        <span class="nav-icon">🛡️</span>
        <span class="nav-txt">Armaria <span class="nav-count">1865</span></span>
      </button>'''

# Normalize line endings for replacement
html = html.replace(old_btn.replace('\r\n', '\n'), new_btn.replace('\r\n', '\n'))
html = html.replace(old_btn.replace('\n', '\r\n'), new_btn.replace('\n', '\r\n'))

# 3. Add drawer section
old_drawer = '''      <!-- Grimório de Habilidades & Efeitos Especiais (1.923 Habilidades / 128 Efeitos) -->
      <section class="drawer-section">
        <div class="section-header-row">
          <h4 class="section-title">🔮 Grimório de Habilidades & VFX</h4>
          <span class="badge-count">1.923 Habilidades</span>
        </div>
        <button id="btn-drawer-all-skills" class="btn-view-all">
          🔮 Abrir Grimório & Testar Efeitos Especiais (128 VFX) ➔
        </button>
      </section>'''

new_drawer = '''      <!-- Grimório de Habilidades & Efeitos Especiais (1.923 Habilidades / 128 Efeitos) -->
      <section class="drawer-section">
        <div class="section-header-row">
          <h4 class="section-title">🔮 Grimório de Habilidades & VFX</h4>
          <span class="badge-count">1.923 Habilidades</span>
        </div>
        <button id="btn-drawer-all-skills" class="btn-view-all">
          🔮 Abrir Grimório & Testar Efeitos Especiais (128 VFX) ➔
        </button>
      </section>

      <!-- Armaria & Equipamentos (1.865 Itens) -->
      <section class="drawer-section">
        <div class="section-header-row">
          <h4 class="section-title">🛡️ Armaria & Equipamentos</h4>
          <span class="badge-count">1.865 Itens</span>
        </div>
        <button id="btn-drawer-all-equipment" class="btn-view-all">
          🛡️ Abrir Armaria de Equipamentos, Armas & Sets (1.865 Itens) ➔
        </button>
      </section>'''

html = html.replace(old_drawer.replace('\r\n', '\n'), new_drawer.replace('\r\n', '\n'))
html = html.replace(old_drawer.replace('\n', '\r\n'), new_drawer.replace('\n', '\r\n'))

# 4. Add Modal 7 before </body>
modal_7 = '''
  <!-- Modal 7: Armaria de Equipamentos, Armas & Conjuntos -->
  <div id="modal-equipment" class="catalog-modal hidden">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title-group">
          <h3>🛡️ Armaria de Equipamentos, Armas & Conjuntos</h3>
          <span class="modal-subtitle">1.865 armas, armaduras, joias, asas e trajes divididos em 6 arquétipos e 248 conjuntos de equipamentos.</span>
        </div>
        <button id="btn-close-equipment-modal" class="modal-close-btn">✕</button>
      </div>

      <div class="modal-search-bar">
        <input type="text" id="equipment-search-input" placeholder="🔍 Buscar por nome, tipo, classe, nível ou conjunto (ex: Espada, Armadura, Guerreiro, Hàn Băng)..." />
      </div>

      <div class="modal-filter-pills" id="equipment-filter-pills">
        <button class="pill-filter active" data-filter="all">🌟 Todos (1865)</button>
        <button class="pill-filter" data-filter="weapons">⚔️ Armas Principais (123)</button>
        <button class="pill-filter" data-filter="offhand">🛡️ Armas Secundárias (101)</button>
        <button class="pill-filter" data-filter="armor">🥋 Armaduras (600)</button>
        <button class="pill-filter" data-filter="jewelry">💍 Joias & Acessórios (137)</button>
        <button class="pill-filter" data-filter="wings_costumes">🪽 Asas & Visuais (334)</button>
        <button class="pill-filter" data-filter="pet">🐾 Pets (570)</button>
        <button class="pill-filter" data-filter="suits">👑 Conjuntos / Sets (248)</button>
      </div>

      <div class="modal-grid-container" id="equipment-grid-container">
        <!-- Renderizado dinamicamente via JS a partir de assets/equipment/catalog.json -->
      </div>
    </div>
  </div>
'''

if 'id="modal-equipment"' not in html:
    html = html.replace('</body>', modal_7 + '\n</body>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated web/index.html successfully!")
