import os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
path = 'web/main.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update renderEquipmentGrid filtering to support 'wings'
old_filter_code = '''    // Filtro por categoria
    const filtered = equipmentList.filter(item => {
      if (selectedEquipmentFilter === "weapons" && item.category_group !== "weapons") return false;
      if (selectedEquipmentFilter === "offhand" && item.category_group !== "offhand") return false;
      if (selectedEquipmentFilter === "armor" && item.category_group !== "armor") return false;
      if (selectedEquipmentFilter === "jewelry" && item.category_group !== "jewelry") return false;
      if (selectedEquipmentFilter === "wings_costumes" && item.category_group !== "wings_costumes") return false;
      if (selectedEquipmentFilter === "pet" && item.category_group !== "pet") return false;
      if (selectedEquipmentFilter === "suits" && !item.suit_id) return false;'''

new_filter_code = '''    // Se filtro for 'wings' (Asas Animadas), usar o catálogo de asas
    let sourceList = equipmentList;
    if (selectedEquipmentFilter === "wings") {
      sourceList = Array.isArray(wingsCatalogData) && wingsCatalogData.length > 0 ? wingsCatalogData : [];
    }

    // Filtro por categoria
    const filtered = sourceList.filter(item => {
      if (selectedEquipmentFilter === "wings") return true;
      if (selectedEquipmentFilter === "weapons" && item.category_group !== "weapons") return false;
      if (selectedEquipmentFilter === "offhand" && item.category_group !== "offhand") return false;
      if (selectedEquipmentFilter === "armor" && item.category_group !== "armor") return false;
      if (selectedEquipmentFilter === "jewelry" && item.category_group !== "jewelry") return false;
      if (selectedEquipmentFilter === "wings_costumes" && item.category_group !== "wings_costumes") return false;
      if (selectedEquipmentFilter === "pet" && item.category_group !== "pet") return false;
      if (selectedEquipmentFilter === "suits" && !item.suit_id) return false;'''

if old_filter_code in text:
    text = text.replace(old_filter_code, new_filter_code)
    print("1. Updated filter logic in renderEquipmentGrid")
else:
    print("Warning: old_filter_code not found")

# 2. Add wing button in card footer
old_card_footer = '''          <div class="equipment-card-footer">
            <span class="equipment-durability">🛡️ Durabilidade: ${item.endure_max || '100%'}</span>
            ${item.category_group === "weapons" ? `
              <button class="btn-weapon-equip ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'active' : ''}" data-equip-id="${item.id}" title="${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'Clique para desempunhar' : 'Clique para empunhar na mão do personagem'}">
                ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? '⚔️ Equipado' : '🖐️ Empunhar'}
              </button>
            ` : ''}
            <span class="equipment-quality-badge" style="background: ${qualityColor}22; color: ${qualityColor}; border: 1px solid ${qualityColor}55;">'''

new_card_footer = '''          <div class="equipment-card-footer">
            <span class="equipment-durability">🛡️ Durabilidade: ${item.endure_max || '100%'}</span>
            ${item.category_group === "weapons" ? `
              <button class="btn-weapon-equip ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'active' : ''}" data-equip-id="${item.id}" title="${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'Clique para desempunhar' : 'Clique para empunhar na mão do personagem'}">
                ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? '⚔️ Equipado' : '🖐️ Empunhar'}
              </button>
            ` : ''}
            ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? `
              <button class="btn-wing-equip ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'active' : ''}" data-wing-id="${item.id}" title="${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'Clique para desequipar as asas' : 'Clique para equipar as asas nas costas do personagem'}">
                ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? '🪽 Equipado' : '🪽 Equipar'}
              </button>
            ` : ''}
            <span class="equipment-quality-badge" style="background: ${qualityColor}22; color: ${qualityColor}; border: 1px solid ${qualityColor}55;">'''

if old_card_footer in text:
    text = text.replace(old_card_footer, new_card_footer)
    print("2. Added wing equip button in card footer")
else:
    print("Warning: old_card_footer not found")

# 3. Bind events for .btn-wing-equip
old_bind_events = '''    equipmentGrid.querySelectorAll(".btn-weapon-equip").forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const equipId = parseInt(btn.dataset.equipId, 10);
        const item = equipmentList.find(x => x.id === equipId);
        if (!item) return;
        if (playerEquippedWeapon && playerEquippedWeapon.id === item.id) {
          equipWeapon(null);
        } else {
          equipWeapon(item);
        }
      };
    });'''

new_bind_events = '''    equipmentGrid.querySelectorAll(".btn-weapon-equip").forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const equipId = parseInt(btn.dataset.equipId, 10);
        const item = equipmentList.find(x => x.id === equipId);
        if (!item) return;
        if (playerEquippedWeapon && playerEquippedWeapon.id === item.id) {
          equipWeapon(null);
        } else {
          equipWeapon(item);
        }
      };
    });

    equipmentGrid.querySelectorAll(".btn-wing-equip").forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const wingId = btn.dataset.wingId;
        const item = (Array.isArray(wingsCatalogData) ? wingsCatalogData.find(x => String(x.id) === String(wingId)) : null) ||
                     equipmentList.find(x => String(x.id) === String(wingId));
        if (!item) return;
        if (playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id)) {
          equipWing(null);
        } else {
          equipWing(item);
        }
      };
    });'''

if old_bind_events in text:
    text = text.replace(old_bind_events, new_bind_events)
    print("3. Bound events for .btn-wing-equip")
else:
    print("Warning: old_bind_events not found")

# 4. Startup restoration for equipped wing
old_startup = '''  // Restaurar arma empunhada salva ou equipar inicial
  const savedWeaponId = localStorage.getItem("mc_equipped_weapon_id");
  if (savedWeaponId && equipmentList && equipmentList.length > 0) {
    const savedItem = equipmentList.find(x => String(x.id) === String(savedWeaponId));
    if (savedItem) equipWeapon(savedItem);
  } else if (equipmentList && equipmentList.length > 0) {
    const defItem = equipmentList.find(x => x.id === 170) || equipmentList.find(x => x.category_group === "weapons");
    if (defItem) equipWeapon(defItem);
  }'''

new_startup = '''  // Restaurar arma empunhada salva ou equipar inicial
  const savedWeaponId = localStorage.getItem("mc_equipped_weapon_id");
  if (savedWeaponId && equipmentList && equipmentList.length > 0) {
    const savedItem = equipmentList.find(x => String(x.id) === String(savedWeaponId));
    if (savedItem) equipWeapon(savedItem);
  } else if (equipmentList && equipmentList.length > 0) {
    const defItem = equipmentList.find(x => x.id === 170) || equipmentList.find(x => x.category_group === "weapons");
    if (defItem) equipWeapon(defItem);
  }

  // Restaurar asas equipadas salvas ou equipar inicial
  const savedWingId = localStorage.getItem("mc_equipped_wing_id");
  if (savedWingId) {
    const savedW = (Array.isArray(wingsCatalogData) ? wingsCatalogData.find(x => String(x.id) === String(savedWingId)) : null) ||
                   (equipmentList && equipmentList.find(x => String(x.id) === String(savedWingId)));
    if (savedW) equipWing(savedW);
  } else if (Array.isArray(wingsCatalogData) && wingsCatalogData.length > 0) {
    const defW = wingsCatalogData.find(x => x.model_id === "equip_wing_001001") || wingsCatalogData[0];
    if (defW) equipWing(defW);
  }'''

if old_startup in text:
    text = text.replace(old_startup, new_startup)
    print("4. Added wing startup restoration")
else:
    print("Warning: old_startup not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Part 2 of main.js updated successfully!")
