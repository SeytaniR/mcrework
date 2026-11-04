import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "web", "index.html")
STYLE_PATH = os.path.join(BASE_DIR, "web", "style.css")

print("1. Updating web/index.html...")
with open(INDEX_PATH, "r", encoding="utf-8") as f:
    html = f.read()

# Bump cache buster in index.html
html = html.replace("style.css?v=1.5.2", "style.css?v=1.5.3")
html = html.replace("main.js?v=1.5.2", "main.js?v=1.5.3")

# Add drawer button for costumes
drawer_target = """        <button id="btn-drawer-all-equipment" class="btn-view-all">
          🛡️ Abrir Armaria de Equipamentos, Armas & Sets (1.865 Itens) ➔
        </button>"""
drawer_repl = """        <button id="btn-drawer-all-equipment" class="btn-view-all">
          🛡️ Abrir Armaria de Equipamentos, Armas & Sets (1.865 Itens) ➔
        </button>
        <button id="btn-drawer-all-costumes" class="btn-view-all" style="margin-top: 6px; background: rgba(180, 142, 173, 0.18); border-color: rgba(180, 142, 173, 0.45); color: #d8bee5;">
          👗 Provar Modas, Trajes & Skins no Personagem (334 Modas) ➔
        </button>"""
if drawer_target in html:
    html = html.replace(drawer_target, drawer_repl, 1)
    print("  [OK] Added btn-drawer-all-costumes")
else:
    print("  [WARN] drawer_target not found in index.html")

# Update combat test header actions to include minimize toggle
combat_header_target = """      <div class="combat-header-actions">
        <button id="btn-combat-switch-mon" class="btn-switch-mon" title="Escolher outro monstro do Bestiário">👾 Trocar Monstro (543)</button>
        <button id="btn-close-combat-test" class="btn-close-combat" title="Encerrar Modo de Combate e Voltar ao Mapa">✕ Sair</button>
      </div>"""
combat_header_repl = """      <div class="combat-header-actions">
        <button id="btn-toggle-combat-panel" class="btn-toggle-combat" title="Minimizar / Expandir Controles">▼ Minimizar</button>
        <button id="btn-combat-switch-mon" class="btn-switch-mon" title="Escolher outro monstro do Bestiário">👾 Trocar Monstro (543)</button>
        <button id="btn-close-combat-test" class="btn-close-combat" title="Encerrar Modo de Combate e Voltar ao Mapa">✕ Sair</button>
      </div>"""
if combat_header_target in html:
    html = html.replace(combat_header_target, combat_header_repl, 1)
    print("  [OK] Added btn-toggle-combat-panel to combat header")
else:
    print("  [WARN] combat_header_target not found in index.html")

# Update modal-skills header with minimize button
skills_header_target = """        <button id="btn-close-skills-modal" class="modal-close-btn">✕</button>
      </div>

      <div class="modal-search-bar">"""
skills_header_repl = """        <div class="modal-header-btns">
          <button id="btn-minimize-skills-modal" class="modal-minimize-btn" title="Minimizar para testar no mapa">▼ Minimizar</button>
          <button id="btn-close-skills-modal" class="modal-close-btn">✕</button>
        </div>
      </div>

      <div class="modal-search-bar">"""
if skills_header_target in html:
    html = html.replace(skills_header_target, skills_header_repl, 1)
    print("  [OK] Added btn-minimize-skills-modal to skills modal")
else:
    print("  [WARN] skills_header_target not found in index.html")

# Add floating skills bar after modal-skills
skills_end_target = """      <div class="modal-grid-container" id="skills-grid-container">
        <!-- Renderizado dinamicamente via JS a partir de assets/skills/catalog.json -->
      </div>
    </div>
  </div>"""
skills_end_repl = """      <div class="modal-grid-container" id="skills-grid-container">
        <!-- Renderizado dinamicamente via JS a partir de assets/skills/catalog.json -->
      </div>
    </div>
  </div>

  <!-- Barra Flutuante de Teste de Habilidade / VFX (Ao Vivo no Mapa) -->
  <div id="skills-floating-bar" class="skills-floating-bar hidden">
    <div class="skills-floating-info">
      <span id="skills-floating-icon" class="floating-vfx-icon">✨</span>
      <div class="skills-floating-col">
        <strong id="skills-floating-title">Habilidade Disparada</strong>
        <span id="skills-floating-sub">Executando animação e efeito no mapa...</span>
      </div>
    </div>
    <div class="skills-floating-btns">
      <button id="btn-floating-repeat" class="btn-floating-action" title="Repetir Disparo">🔁 Repetir</button>
      <button id="btn-floating-grimorio" class="btn-floating-action btn-floating-accent" title="Voltar ao Grimório">📖 Grimório</button>
      <button id="btn-floating-close" class="btn-floating-action btn-floating-close" title="Fechar Teste">✕</button>
    </div>
  </div>"""
if skills_end_target in html:
    html = html.replace(skills_end_target, skills_end_repl, 1)
    print("  [OK] Added skills-floating-bar after modal-skills")
else:
    print("  [WARN] skills_end_target not found in index.html")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(html)
print("web/index.html updated successfully.")


# 2. Updating web/style.css
print("\n2. Updating web/style.css...")
with open(STYLE_PATH, "r", encoding="utf-8") as f:
    css = f.read()

# Replace .modal-grid-container !important
grid_target = """.modal-grid-container {
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)) !important;
}"""
grid_repl = """@media (min-width: 601px) {
  .modal-grid-container {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}
@media (max-width: 600px) {
  .modal-grid-container {
    grid-template-columns: 1fr !important;
    padding: 8px 10px 24px 10px !important;
    gap: 8px !important;
  }
}"""
if grid_target in css:
    css = css.replace(grid_target, grid_repl, 1)
    print("  [OK] Responsive modal-grid-container replaced")
else:
    print("  [WARN] grid_target not found in style.css")

# Add combat test minimized styles and toggle button
extra_css = """
/* ==========================================================================
   Controles Compactos de Combate & Minimizar
   ========================================================================== */
.btn-toggle-combat {
  background: rgba(136, 192, 208, 0.18);
  border: 1px solid rgba(136, 192, 208, 0.45);
  color: #88c0d0;
  font-size: 10.5px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.btn-toggle-combat:hover {
  background: rgba(136, 192, 208, 0.35);
  border-color: #88c0d0;
}

.combat-test-panel.minimized {
  max-height: 48px !important;
  height: 48px !important;
  overflow: hidden !important;
  padding: 8px 12px !important;
  border-radius: 14px 14px 0 0 !important;
  background: rgba(18, 22, 32, 0.96) !important;
}
.combat-test-panel.minimized .combat-status-bar,
.combat-test-panel.minimized .combat-controls-body {
  display: none !important;
}

/* Botão de Equipar Moda / Trajes */
.btn-costume-equip {
  background: rgba(180, 142, 173, 0.18);
  border: 1px solid rgba(180, 142, 173, 0.5);
  color: #d8bee5;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.btn-costume-equip:hover, .btn-costume-equip.active {
  background: #b48ead;
  border-color: #b48ead;
  color: #1e222b;
  box-shadow: 0 0 10px rgba(180, 142, 173, 0.45);
}

/* Barra Flutuante de Teste de Habilidade / VFX */
.skills-floating-bar {
  position: fixed;
  bottom: max(16px, var(--safe-bottom));
  left: 50%;
  transform: translateX(-50%);
  width: min(420px, calc(100vw - 20px));
  background: rgba(20, 24, 34, 0.96);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(180, 142, 173, 0.55);
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.75), 0 0 16px rgba(180, 142, 173, 0.3);
  padding: 8px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  z-index: 1050;
  animation: slideUp 0.22s ease-out;
  box-sizing: border-box;
}
.skills-floating-bar.hidden {
  display: none !important;
}
.skills-floating-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}
.floating-vfx-icon {
  font-size: 22px;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(180, 142, 173, 0.2);
  border: 1px solid rgba(180, 142, 173, 0.4);
  flex-shrink: 0;
}
.floating-vfx-icon img {
  width: 28px;
  height: 28px;
  object-fit: contain;
}
.skills-floating-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 1px;
}
.skills-floating-col strong {
  font-size: 12.5px;
  color: #eceff4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.skills-floating-col span {
  font-size: 10px;
  color: #88c0d0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.skills-floating-btns {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}
.btn-floating-action {
  padding: 6px 10px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  color: #e5e9f0;
  transition: all 0.15s;
}
.btn-floating-action:active {
  transform: scale(0.96);
}
.btn-floating-accent {
  background: linear-gradient(135deg, #b48ead, #88c0d0);
  border: none;
  color: #1e222b;
}
.btn-floating-close {
  padding: 6px 8px;
}

.modal-header-btns {
  display: flex;
  align-items: center;
  gap: 6px;
}
.modal-minimize-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #eceff4;
  font-size: 11px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.modal-minimize-btn:hover {
  background: rgba(180, 142, 173, 0.3);
  border-color: #b48ead;
}

.vfx-thumb-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}
"""

css += "\n" + extra_css

# In mobile media query, ensure combat panel max-height is 44vh
css = css.replace("max-height: 52vh !important;", "max-height: 44vh !important;")

with open(STYLE_PATH, "w", encoding="utf-8") as f:
    f.write(css)
print("web/style.css updated successfully.")
