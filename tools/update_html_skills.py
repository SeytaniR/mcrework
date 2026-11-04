import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('web/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add top bar button if not present
if 'btn-open-skills-modal' not in html:
    npc_btn = '</button>\n      <button id="btn-open-npcs-modal"'
    replacement = '''</button>
      <button id="btn-open-skills-modal" class="nav-pill-btn nav-skills" title="Grimório de Habilidades & Efeitos Especiais (1.923 Habilidades / 128 Efeitos)">
        <span class="nav-icon">🔮</span>
        <span class="nav-txt">Habilidades <span class="nav-count">1923</span></span>
      </button>
      <button id="btn-open-npcs-modal"'''
    html = html.replace(npc_btn, replacement, 1)

# 2. Add drawer section if not present
if 'btn-drawer-all-skills' not in html:
    npc_drawer = '<!-- Enciclopédia de NPCs (365 NPCs) -->'
    skills_drawer = '''<!-- Grimório de Habilidades & Efeitos Especiais (1.923 Habilidades / 128 Efeitos) -->
      <section class="drawer-section">
        <div class="section-header-row">
          <h4 class="section-title">🔮 Grimório de Habilidades & VFX</h4>
          <span class="badge-count">1.923 Habilidades</span>
        </div>
        <button id="btn-drawer-all-skills" class="btn-view-all">
          🔮 Abrir Grimório & Testar Efeitos Especiais (128 VFX) ➔
        </button>
      </section>

      <!-- Enciclopédia de NPCs (365 NPCs) -->'''
    html = html.replace(npc_drawer, skills_drawer, 1)

# 3. Add modal-skills before </body>
if 'id="modal-skills"' not in html:
    skills_modal = '''  <!-- Modal 6: Grimório de Habilidades & Efeitos Especiais -->
  <div id="modal-skills" class="catalog-modal hidden">
    <div class="modal-card">
      <div class="modal-header">
        <div class="modal-title-group">
          <h3>🔮 Grimório de Habilidades & Efeitos Especiais</h3>
          <span class="modal-subtitle">1.923 habilidades e 128 efeitos visuais animados (VFX). Selecione qualquer habilidade para disparar seu efeito visual ao vivo!</span>
        </div>
        <button id="btn-close-skills-modal" class="modal-close-btn">✕</button>
      </div>

      <div class="modal-search-bar">
        <input type="text" id="skills-search-input" placeholder="🔍 Buscar habilidade por nome, tipo, classe ou código (ex: Thiên Lôi, Magia, Guerreiro, 10008)..." />
      </div>

      <div class="modal-filter-pills" id="skills-filter-pills">
        <button class="pill-filter active" data-filter="all">🌟 Todas (1923)</button>
        <button class="pill-filter" data-filter="class">⚔️ Classes</button>
        <button class="pill-filter" data-filter="warrior">🛡️ Guerreiro</button>
        <button class="pill-filter" data-filter="bard">🎵 Bardo</button>
        <button class="pill-filter" data-filter="priest">✨ Clérigo</button>
        <button class="pill-filter" data-filter="gunner">🎯 Atirador</button>
        <button class="pill-filter" data-filter="hunter">🐾 Caçador</button>
        <button class="pill-filter" data-filter="paladin">🗡️ Paladino</button>
        <button class="pill-filter" data-filter="pet">🐶 Pets</button>
        <button class="pill-filter" data-filter="buff">💫 Buffs</button>
        <button class="pill-filter" data-filter="vfx">⚡ Efeitos VFX (128)</button>
      </div>

      <div class="modal-grid-container" id="skills-grid-container">
        <!-- Renderizado dinamicamente via JS a partir de assets/skills/catalog.json -->
      </div>
    </div>
  </div>

</body>'''
    html = html.replace('</body>', skills_modal, 1)

with open('web/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated web/index.html successfully!")
