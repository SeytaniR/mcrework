import os

main_js_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\main.js"
with open(main_js_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update equipWing toast
old_equip_wing = '''    try {
      const manifestUrl = `assets/wings/${modelId}/char_manifest.json?v=1.5.3`;
      const manifest = await fetch(manifestUrl).then(r => r.json());
      currentWingManifest = manifest;

      const loadPromises = [];
      for (const animKey in manifest) {
        for (const frameInfo of manifest[animKey]) {
          if (!textureCache[frameInfo.file]) {
            loadPromises.push(
              PIXI.Assets.load(frameInfo.file).then(tex => {
                textureCache[frameInfo.file] = tex;
              }).catch(() => {})
            );
          }
        }
      }
      await Promise.all(loadPromises);
      if (wingSprite) wingSprite.visible = true;
      showWeaponToast(`🪽 Asas Equipadas: ${item.name}!`);
    } catch (e) {
      console.warn("Erro ao carregar modelo das asas:", modelId, e);
      showWeaponToast(`🪽 Asas selecionadas: ${item.name}`);
    }'''

new_equip_wing = '''    try {
      const manifestUrl = `assets/wings/${modelId}/char_manifest.json?v=1.5.4`;
      const manifest = await fetch(manifestUrl).then(r => r.json());
      currentWingManifest = manifest;

      const loadPromises = [];
      for (const animKey in manifest) {
        for (const frameInfo of manifest[animKey]) {
          if (!textureCache[frameInfo.file]) {
            loadPromises.push(
              PIXI.Assets.load(frameInfo.file).then(tex => {
                textureCache[frameInfo.file] = tex;
              }).catch(() => {})
            );
          }
        }
      }
      await Promise.all(loadPromises);
      if (wingSprite) wingSprite.visible = true;
      const isFly = item.is_fly_mount || (modelId && modelId.startsWith("equip_fly_"));
      showWeaponToast(isFly ? `🧹 Montaria Voadora Ativada: ${item.name}!` : `🪽 Asas Equipadas: ${item.name}!`);
    } catch (e) {
      console.warn("Erro ao carregar modelo das asas:", modelId, e);
      showWeaponToast(`🪽 Selecionado: ${item.name}`);
    }'''

old_unequip_wing = '''    if (!item) {
      playerEquippedWing = null;
      currentWingModel = null;
      currentWingManifest = null;
      if (wingSprite) wingSprite.visible = false;
      localStorage.removeItem("mc_equipped_wing_id");
      showWeaponToast("Asas desequipadas.");
      updateEquippedWingUI();
      if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
      return;
    }'''

new_unequip_wing = '''    if (!item) {
      const wasFly = playerEquippedWing && (playerEquippedWing.is_fly_mount || (currentWingModel && currentWingModel.startsWith("equip_fly_")));
      playerEquippedWing = null;
      currentWingModel = null;
      currentWingManifest = null;
      if (wingSprite) wingSprite.visible = false;
      localStorage.removeItem("mc_equipped_wing_id");
      showWeaponToast(wasFly ? "🧹 Montaria voadora recolhida." : "🪽 Asas desequipadas.");
      updateEquippedWingUI();
      if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
      return;
    }'''

# 2. Update renderEquipmentGrid
old_grid_filter = '''  let selectedEquipmentFilter = "all";
  let equipmentRenderCount = 36; // Paginação virtual de 36 itens por bloco

  function renderEquipmentGrid(resetPagination = true) {
    if (!equipmentGrid) return;
    if (resetPagination) equipmentRenderCount = 36;

    const q = (equipmentSearchInput ? equipmentSearchInput.value : "").trim().toLowerCase();

    // Se filtro for 'wings' (Asas Animadas), usar o catálogo de asas
    let sourceList = equipmentList;
    if (selectedEquipmentFilter === "wings") {
      sourceList = Array.isArray(wingsCatalogData) && wingsCatalogData.length > 0 ? wingsCatalogData : [];
    }

    // Filtro por categoria
    const filtered = sourceList.filter(item => {
      if (selectedEquipmentFilter === "wings") return true;'''

new_grid_filter = '''  let selectedEquipmentFilter = "all";
  let selectedWingSubFilter = "all";
  let equipmentRenderCount = 36; // Paginação virtual de 36 itens por bloco

  function renderEquipmentGrid(resetPagination = true) {
    if (!equipmentGrid) return;
    if (resetPagination) equipmentRenderCount = 36;

    const subFilterWrap = document.getElementById("wings-subfilter-pills");
    if (subFilterWrap) {
      subFilterWrap.classList.toggle("hidden", selectedEquipmentFilter !== "wings");
    }

    const q = (equipmentSearchInput ? equipmentSearchInput.value : "").trim().toLowerCase();

    // Se filtro for 'wings' (Asas & Montarias Voadoras), usar o catálogo de asas
    let sourceList = equipmentList;
    if (selectedEquipmentFilter === "wings") {
      sourceList = Array.isArray(wingsCatalogData) && wingsCatalogData.length > 0 ? wingsCatalogData : [];
    }

    // Filtro por categoria
    const filtered = sourceList.filter(item => {
      if (selectedEquipmentFilter === "wings") {
        const isFly = !!(item.is_fly_mount || (item.model_id && item.model_id.startsWith("equip_fly_")));
        if (selectedWingSubFilter === "wings" && isFly) return false;
        if (selectedWingSubFilter === "mounts" && !isFly) return false;
        return true;
      }'''

old_card_tags = '''              <div class="equipment-tags-row">
                <span class="equipment-slot-tag">${item.position_name}</span>
                <span class="equipment-type-tag">${item.type_name}</span>
                <span class="equipment-class-tag">${classText}</span>
                ${suitBadge}
              </div>'''

new_card_tags = '''              <div class="equipment-tags-row">
                ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? (
                  (item.is_fly_mount || (item.model_id && item.model_id.startsWith("equip_fly_")))
                    ? `<span class="equipment-slot-tag" style="background: rgba(180, 142, 173, 0.25); border: 1px solid #b48ead; color: #d8bee5;">🧹 Montaria Voadora</span>`
                    : `<span class="equipment-slot-tag" style="background: rgba(136, 192, 208, 0.25); border: 1px solid #88c0d0; color: #88c0d0;">🪽 Asa Mística</span>`
                ) : `<span class="equipment-slot-tag">${item.position_name}</span>`}
                <span class="equipment-type-tag">${item.type_name}</span>
                <span class="equipment-class-tag">${classText}</span>
                ${suitBadge}
              </div>'''

old_wing_btn = '''            ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? `
              <button class="btn-wing-equip ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'active' : ''}" data-wing-id="${item.id}" title="${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'Clique para desequipar as asas' : 'Clique para equipar as asas nas costas do personagem'}">
                ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? '🪽 Equipado' : '🪽 Equipar'}
              </button>
            ` : ''}'''

new_wing_btn = '''            ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? (() => {
              const isFly = !!(item.is_fly_mount || (item.model_id && item.model_id.startsWith("equip_fly_")));
              const isEquipped = !!(playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id));
              const activeClass = isEquipped ? 'active' : '';
              const btnLabel = isEquipped 
                ? (isFly ? '🧹 Montado' : '🪽 Voando') 
                : (isFly ? '🧹 Montar / Voar' : '🪽 Equipar Asa');
              const btnTitle = isEquipped ? 'Clique para desequipar' : (isFly ? 'Clique para voar nesta montaria' : 'Clique para equipar asas');
              return `
                <button class="btn-wing-equip ${activeClass}" data-wing-id="${item.id}" title="${btnTitle}">
                  ${btnLabel}
                </button>
              `;
            })() : ''}'''

old_pills_bind = '''  if (equipmentFilterPills) {
    equipmentFilterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill-filter");
      if (!btn) return;
      equipmentFilterPills.querySelectorAll(".pill-filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedEquipmentFilter = btn.dataset.filter || "all";
      renderEquipmentGrid(true);
    });
  }'''

new_pills_bind = '''  if (equipmentFilterPills) {
    equipmentFilterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill-filter");
      if (!btn) return;
      equipmentFilterPills.querySelectorAll(".pill-filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedEquipmentFilter = btn.dataset.filter || "all";
      renderEquipmentGrid(true);
    });
  }

  const wingsSubfilterPills = document.getElementById("wings-subfilter-pills");
  if (wingsSubfilterPills) {
    wingsSubfilterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill-subfilter");
      if (!btn) return;
      wingsSubfilterPills.querySelectorAll(".pill-subfilter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedWingSubFilter = btn.dataset.subfilter || "all";
      renderEquipmentGrid(true);
    });
  }'''

text_norm = text.replace('\r\n', '\n')

replacements = [
    (old_equip_wing, new_equip_wing, "equipWing toast"),
    (old_unequip_wing, new_unequip_wing, "unequipWing toast"),
    (old_grid_filter, new_grid_filter, "grid filter"),
    (old_card_tags, new_card_tags, "card tags"),
    (old_wing_btn, new_wing_btn, "wing btn"),
    (old_pills_bind, new_pills_bind, "pills bind")
]

all_success = True
for old, new, label in replacements:
    old_n = old.replace('\r\n', '\n')
    new_n = new.replace('\r\n', '\n')
    if old_n in text_norm:
        text_norm = text_norm.replace(old_n, new_n)
        print(f"SUCCESS: Replaced {label}")
    else:
        print(f"ERROR: Could not find block for {label}")
        all_success = False

if all_success:
    with open(main_js_path, 'w', encoding='utf-8') as f:
        f.write(text_norm)
    print("ALL REPLACEMENTS APPLIED SUCCESSFULLY TO MAIN.JS!")
