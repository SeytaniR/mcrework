import os

# 1. Update index.html to add wings subfilter pills
index_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\index.html"
with open(index_path, 'r', encoding='utf-8') as f:
    html = f.read()

subfilter_html = '''      <div class="modal-filter-pills" id="equipment-filter-pills">
        <button class="pill-filter active" data-filter="all">🌟 Todos (1865)</button>
        <button class="pill-filter" data-filter="weapons">⚔️ Armas Principais (123)</button>
        <button class="pill-filter" data-filter="offhand">🛡️ Armas Secundárias (101)</button>
        <button class="pill-filter" data-filter="armor">🥋 Armaduras (600)</button>
        <button class="pill-filter" data-filter="jewelry">💍 Joias & Acessórios (137)</button>
        <button class="pill-filter" data-filter="wings">🪽 Asas & Montarias (36)</button>
        <button class="pill-filter" data-filter="wings_costumes">👗 Modas & Trajes (334)</button>
        <button class="pill-filter" data-filter="pet">🐾 Pets (570)</button>
        <button class="pill-filter" data-filter="suits">👑 Conjuntos / Sets (248)</button>
      </div>

      <div class="modal-subfilter-pills hidden" id="wings-subfilter-pills">
        <span style="font-size: 11px; color: #88c0d0; font-weight: bold; margin-right: 4px;">Tipo:</span>
        <button class="pill-subfilter active" data-subfilter="all">🌟 Todas (36)</button>
        <button class="pill-subfilter" data-subfilter="wings">🪽 Asas Místicas (21)</button>
        <button class="pill-subfilter" data-subfilter="mounts">🧹 Montarias Voadoras (15)</button>
      </div>'''

old_pills = '''      <div class="modal-filter-pills" id="equipment-filter-pills">
        <button class="pill-filter active" data-filter="all">🌟 Todos (1865)</button>
        <button class="pill-filter" data-filter="weapons">⚔️ Armas Principais (123)</button>
        <button class="pill-filter" data-filter="offhand">🛡️ Armas Secundárias (101)</button>
        <button class="pill-filter" data-filter="armor">🥋 Armaduras (600)</button>
        <button class="pill-filter" data-filter="jewelry">💍 Joias & Acessórios (137)</button>
        <button class="pill-filter" data-filter="wings">🪽 Asas Animadas (36)</button>
        <button class="pill-filter" data-filter="wings_costumes">👗 Trajes & Visuais (334)</button>
        <button class="pill-filter" data-filter="pet">🐾 Pets (570)</button>
        <button class="pill-filter" data-filter="suits">👑 Conjuntos / Sets (248)</button>
      </div>'''

if old_pills in html:
    html = html.replace(old_pills, subfilter_html)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("SUCCESS: Updated index.html with wings subfilters")
else:
    print("WARNING: old_pills not matched in index.html")

# 2. Update style.css
css_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\style.css"
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

extra_css = '''
/* Fix para Cards de Habilidades & Efeitos Especiais (Anti-Espremimento) */
.modal-grid-container {
  grid-auto-rows: min-content !important;
  align-items: start !important;
}

.skill-card {
  min-height: fit-content !important;
  height: auto !important;
  box-sizing: border-box !important;
  padding: 12px 14px !important;
  overflow: visible !important;
}

.skill-card-desc {
  min-height: auto !important;
  line-height: 1.45 !important;
}

.modal-subfilter-pills {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 16px 8px 16px;
  overflow-x: auto;
  white-space: nowrap;
}
.modal-subfilter-pills.hidden {
  display: none !important;
}
.pill-subfilter {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 600;
  border-radius: 12px;
  border: 1px solid rgba(180, 142, 173, 0.35);
  background: rgba(180, 142, 173, 0.12);
  color: #d8bee5;
  cursor: pointer;
  transition: all 0.15s ease;
}
.pill-subfilter:hover {
  background: rgba(180, 142, 173, 0.25);
  border-color: #b48ead;
}
.pill-subfilter.active {
  background: #b48ead;
  color: #1e222b;
  font-weight: 700;
  border-color: #b48ead;
  box-shadow: 0 0 8px rgba(180, 142, 173, 0.4);
}
'''

if "/* Fix para Cards de Habilidades & Efeitos Especiais (Anti-Espremimento) */" not in css:
    css += extra_css
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print("SUCCESS: Appended anti-squish & subfilter css to style.css")
else:
    print("INFO: CSS rules already present")
