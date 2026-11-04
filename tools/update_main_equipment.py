import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

path = r'web\main.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Promise.all to fetch equipment/catalog.json
old_promise = '''    classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData,
    skillsCatalogData, effectsCatalogData
  ] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] })),
    fetch("assets/skills/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ([])),
    fetch("assets/effects/catalog.json?v=1.4.0").then(r => r.json()).catch(() => ([]))
  ]);'''

new_promise = '''    classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData,
    skillsCatalogData, effectsCatalogData, equipmentCatalogData
  ] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] })),
    fetch("assets/skills/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ([])),
    fetch("assets/effects/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ([])),
    fetch("assets/equipment/catalog.json?v=1.5.0").then(r => r.json()).catch(() => ({ items: [] }))
  ]);'''

if old_promise in code:
    code = code.replace(old_promise, new_promise)
else:
    # try normalized CRLF
    code = code.replace(old_promise.replace('\r\n', '\n'), new_promise.replace('\r\n', '\n'))
    code = code.replace(old_promise.replace('\n', '\r\n'), new_promise.replace('\n', '\r\n'))

# 2. Add Modal 7 logic
modal_7_js = '''
  // ==========================================
  // MODAL 7: ARMARIA DE EQUIPAMENTOS & ARMAS (1.865 Itens & 248 Sets)
  // ==========================================
  const modalEquipment = document.getElementById("modal-equipment");
  const equipmentGrid = document.getElementById("equipment-grid-container");
  const equipmentSearchInput = document.getElementById("equipment-search-input");
  const equipmentFilterPills = document.getElementById("equipment-filter-pills");

  let equipmentList = Array.isArray(equipmentCatalogData?.items) ? equipmentCatalogData.items : (Array.isArray(equipmentCatalogData) ? equipmentCatalogData : []);
  let suitsMap = equipmentCatalogData?.suits || {};
  let selectedEquipmentFilter = "all";
  let equipmentRenderCount = 36; // Paginação virtual de 36 itens por bloco

  function renderEquipmentGrid(resetPagination = true) {
    if (!equipmentGrid) return;
    if (resetPagination) equipmentRenderCount = 36;

    const q = (equipmentSearchInput ? equipmentSearchInput.value : "").trim().toLowerCase();

    // Filtro por categoria
    const filtered = equipmentList.filter(item => {
      if (selectedEquipmentFilter === "weapons" && item.category_group !== "weapons") return false;
      if (selectedEquipmentFilter === "offhand" && item.category_group !== "offhand") return false;
      if (selectedEquipmentFilter === "armor" && item.category_group !== "armor") return false;
      if (selectedEquipmentFilter === "jewelry" && item.category_group !== "jewelry") return false;
      if (selectedEquipmentFilter === "wings_costumes" && item.category_group !== "wings_costumes") return false;
      if (selectedEquipmentFilter === "pet" && item.category_group !== "pet") return false;
      if (selectedEquipmentFilter === "suits" && !item.suit_id) return false;

      if (q) {
        const queryStr = `${item.name} ${item.name_orig} ${item.position_name} ${item.type_name} ${item.quality} ${item.suit_name || ''} ${item.description} ${item.id}`.toLowerCase();
        if (!queryStr.includes(q)) return false;
      }
      return true;
    });

    const slice = filtered.slice(0, equipmentRenderCount);
    let html = slice.map(item => {
      const iconImg = item.icon ? `<img src="${item.icon}" alt="${item.name}" class="equipment-card-icon" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" /><span style="display:none; font-size: 20px;">🛡️</span>` : `<span style="font-size: 20px;">🛡️</span>`;
      const classText = item.req_classes && item.req_classes.length > 0 ? item.req_classes.join(', ') : 'Todas';
      
      let statsHtml = '';
      if (item.stats && item.stats.length > 0) {
        statsHtml = item.stats.slice(0, 4).map(st => {
          let cls = 'equipment-stat-pill';
          if (st.label.includes('Ataque')) cls += ' atk';
          else if (st.label.includes('Defesa') || st.label.includes('HP')) cls += ' def';
          else if (st.label.includes('Velocidade') || st.label.includes('Agilidade') || st.label.includes('Crítico')) cls += ' spd';
          return `<span class="${cls}">${st.label}: ${st.value}</span>`;
        }).join('');
      }

      const suitBadge = item.suit_name ? `<span class="equipment-suit-tag">👑 ${item.suit_name}</span>` : '';
      const qualityColor = item.quality_color || '#eceff4';

      return `
        <div class="equipment-card" data-equip-id="${item.id}" style="border-left: 3px solid ${qualityColor};">
          <div class="equipment-card-header">
            <div class="equipment-card-icon-wrap" style="border-color: ${qualityColor}55;">
              ${iconImg}
            </div>
            <div class="equipment-card-title-col">
              <div class="equipment-title-row">
                <h4 class="equipment-card-name" style="color: ${qualityColor};" title="${item.name}">${item.name}</h4>
                <span class="skill-badge-level">Nv. ${item.req_level || 1}</span>
              </div>
              <span class="equipment-card-orig">${item.name_orig}</span>
              <div class="equipment-tags-row">
                <span class="equipment-slot-tag">${item.position_name}</span>
                <span class="equipment-type-tag">${item.type_name}</span>
                <span class="equipment-class-tag">${classText}</span>
                ${suitBadge}
              </div>
            </div>
          </div>
          <p class="equipment-card-desc">${item.description || 'Equipamento oficial do Magic Campus.'}</p>
          ${statsHtml ? `<div class="equipment-card-stats">${statsHtml}</div>` : ''}
          <div class="equipment-card-footer">
            <span class="equipment-durability">🛡️ Durabilidade: ${item.endure_max || '100%'}</span>
            <span class="equipment-quality-badge" style="background: ${qualityColor}22; color: ${qualityColor}; border: 1px solid ${qualityColor}55;">
              ${item.quality}
            </span>
          </div>
        </div>
      `;
    }).join("");

    if (filtered.length > equipmentRenderCount) {
      html += `
        <div style="grid-column: 1 / -1; text-align: center; padding: 15px;">
          <button id="btn-equipment-load-more" class="btn" style="padding: 10px 24px; border-radius: 20px; background: rgba(235, 203, 139, 0.25); border: 1px solid #ebcb8b; color: #eceff4; font-weight: bold; cursor: pointer;">
            Carregar Mais Equipamentos (${slice.length} de ${filtered.length}) ➔
          </button>
        </div>
      `;
    }
    equipmentGrid.innerHTML = html;
    bindEquipmentGridEvents();
  }

  function bindEquipmentGridEvents() {
    const btnLoadMore = document.getElementById("btn-equipment-load-more");
    if (btnLoadMore) {
      btnLoadMore.onclick = () => {
        equipmentRenderCount += 36;
        renderEquipmentGrid(false);
      };
    }
  }

  function openEquipmentModal() {
    if (modalEquipment) {
      modalEquipment.classList.remove("hidden");
      renderEquipmentGrid();
    }
  }
  function closeEquipmentModal() {
    if (modalEquipment) modalEquipment.classList.add("hidden");
  }

  const btnTopEquipment = document.getElementById("btn-open-equipment-modal");
  const btnDrawerEquipment = document.getElementById("btn-drawer-all-equipment");
  const btnCloseEquipment = document.getElementById("btn-close-equipment-modal");

  if (btnTopEquipment) btnTopEquipment.addEventListener("click", openEquipmentModal);
  if (btnDrawerEquipment) btnDrawerEquipment.addEventListener("click", () => { closeDrawer(); openEquipmentModal(); });
  if (btnCloseEquipment) btnCloseEquipment.addEventListener("click", closeEquipmentModal);

  if (equipmentSearchInput) {
    equipmentSearchInput.addEventListener("input", () => {
      renderEquipmentGrid(true);
    });
  }

  if (equipmentFilterPills) {
    equipmentFilterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill-filter");
      if (!btn) return;
      equipmentFilterPills.querySelectorAll(".pill-filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedEquipmentFilter = btn.dataset.filter || "all";
      renderEquipmentGrid(true);
    });
  }
'''

target_anchor = 'console.log("Magic Campus Mobile Engine inicializado com sucesso!");'
if target_anchor in code and 'MODAL 7: ARMARIA' not in code:
    code = code.replace(target_anchor, modal_7_js + '\n  ' + target_anchor)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated web/main.js successfully!")
