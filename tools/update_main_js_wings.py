import os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
path = 'web/main.js'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Promise.all unpacking and fetch
old_promise = '''    classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData,
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

new_promise = '''    classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData,
    skillsCatalogData, effectsCatalogData, equipmentCatalogData, wingsCatalogData
  ] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] })),
    fetch("assets/skills/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ([])),
    fetch("assets/effects/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ([])),
    fetch("assets/equipment/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ({ items: [] })),
    fetch("assets/wings/catalog.json?v=1.5.2").then(r => r.json()).catch(() => ([]))
  ]);'''

if old_promise in text:
    text = text.replace(old_promise, new_promise)
    print("1. Updated Promise.all with wingsCatalogData")
else:
    print("Warning: old_promise not found")

# 2. Add wingSprite in playerContainer
old_weapon_sprite = '''  // Sprite animado da Arma Empunhada (sincronizada milimetricamente com o corpo)
  const weaponSprite = new PIXI.Sprite();
  weaponSprite.anchor.set(0.5, 110 / 150);
  weaponSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
  weaponSprite.scale.set(0.70);
  weaponSprite.visible = false;
  playerContainer.addChild(weaponSprite);'''

new_weapon_and_wing_sprite = '''  // Sprite animado das Asas (Renderizado atrás do corpo ou à frente nas costas)
  const wingSprite = new PIXI.Sprite();
  wingSprite.anchor.set(0.5, 0.5);
  wingSprite.position.set(0, PLAYER_GROUND_OFFSET_Y - 38);
  wingSprite.scale.set(0.70);
  wingSprite.visible = false;
  playerContainer.addChildAt(wingSprite, 0);

  // Sprite animado da Arma Empunhada (sincronizada milimetricamente com o corpo)
  const weaponSprite = new PIXI.Sprite();
  weaponSprite.anchor.set(0.5, 110 / 150);
  weaponSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
  weaponSprite.scale.set(0.70);
  weaponSprite.visible = false;
  playerContainer.addChild(weaponSprite);'''

if old_weapon_sprite in text:
    text = text.replace(old_weapon_sprite, new_weapon_and_wing_sprite)
    print("2. Added wingSprite to playerContainer")
else:
    print("Warning: old_weapon_sprite not found")

# 3. Add wing state and equipWing functions
old_weapon_state = '''  // Sistema de Arma Empunhada (Armaria & Combate Visual)
  let playerEquippedWeapon = null;
  let currentWeaponManifest = null;
  let currentWeaponModel = null;'''

new_weapon_and_wing_state = '''  // Sistema de Arma Empunhada (Armaria & Combate Visual)
  let playerEquippedWeapon = null;
  let currentWeaponManifest = null;
  let currentWeaponModel = null;

  // Sistema de Asas Visuais Equipadas
  let playerEquippedWing = null;
  let currentWingManifest = null;
  let currentWingModel = null;

  async function equipWing(item) {
    if (!item) {
      playerEquippedWing = null;
      currentWingModel = null;
      currentWingManifest = null;
      if (wingSprite) wingSprite.visible = false;
      localStorage.removeItem("mc_equipped_wing_id");
      showWeaponToast("Asas desequipadas.");
      updateEquippedWingUI();
      if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
      return;
    }

    const modelId = item.active_wing_model || item.model_id || "equip_wing_001001";
    playerEquippedWing = item;
    currentWingModel = modelId;
    localStorage.setItem("mc_equipped_wing_id", String(item.id));

    try {
      const manifestUrl = `assets/wings/${modelId}/char_manifest.json?v=1.5.2`;
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
    }

    updateEquippedWingUI();
    if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
  }

  function updateEquippedWingUI() {
    const drawerWing = document.getElementById("drawer-wing");
    const btnUnequipWing = document.getElementById("btn-unequip-wing");
    if (drawerWing) {
      if (playerEquippedWing) {
        drawerWing.innerText = `🪽 ${playerEquippedWing.name}`;
        drawerWing.style.color = "#88c0d0";
      } else {
        drawerWing.innerText = "Nenhuma (Sem Asas)";
        drawerWing.style.color = "#94a3b8";
      }
    }
    if (btnUnequipWing) {
      btnUnequipWing.style.display = playerEquippedWing ? "inline-block" : "none";
      btnUnequipWing.onclick = () => equipWing(null);
    }
  }'''

if old_weapon_state in text:
    text = text.replace(old_weapon_state, new_weapon_and_wing_state)
    print("3. Added equipWing state and logic")
else:
    print("Warning: old_weapon_state not found")

# 4. Update updatePlayerAnimation with wingSprite sync
old_anim_sync = '''    // Sincronizar arma empunhada na mesma direção e frame de ação
    if (weaponSprite) {
      if (currentWeaponManifest) {
        const weaponFrames = currentWeaponManifest[animKey] ||
                             currentWeaponManifest[`${player.dir}-0`] ||
                             currentWeaponManifest["0-0"];
        if (weaponFrames && weaponFrames.length > 0) {
          const wFrameData = weaponFrames[player.frameIdx % weaponFrames.length];
          const wTex = textureCache[wFrameData.file];
          if (wTex) {
            weaponSprite.texture = wTex;
            weaponSprite.anchor.set(0.5, 110 / 150);
            weaponSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
            weaponSprite.visible = true;
          }
        }
      } else {
        weaponSprite.visible = false;
      }
    }'''

new_anim_sync = '''    // Sincronizar asas na mesma direção e frame de ação
    if (wingSprite) {
      if (currentWingManifest) {
        const wingFrames = currentWingManifest[animKey] ||
                           currentWingManifest[`${player.dir}-0`] ||
                           currentWingManifest[`0-${player.dir}`] ||
                           currentWingManifest["0-0"];
        if (wingFrames && wingFrames.length > 0) {
          const wfData = wingFrames[player.frameIdx % wingFrames.length];
          const wfTex = textureCache[wfData.file];
          if (wfTex) {
            wingSprite.texture = wfTex;
            wingSprite.anchor.set(0.5, 0.5);
            wingSprite.position.set(0, PLAYER_GROUND_OFFSET_Y - 38);
            wingSprite.visible = true;

            // Z-Order: se estiver virado de costas (Norte: dirs 3, 4, 5), asas ficam na frente do corpo
            // Caso contrário (Frente/Sul/Lados: dirs 0, 1, 2, 6, 7), asas ficam atrás do corpo
            if (player.dir === 3 || player.dir === 4 || player.dir === 5) {
              const bodyIdx = playerContainer.getChildIndex(charSprite);
              const curWingIdx = playerContainer.getChildIndex(wingSprite);
              if (curWingIdx < bodyIdx) {
                playerContainer.setChildIndex(wingSprite, bodyIdx);
              }
            } else {
              const curWingIdx = playerContainer.getChildIndex(wingSprite);
              if (curWingIdx > 0) {
                playerContainer.setChildIndex(wingSprite, 0);
              }
            }
          }
        }
      } else {
        wingSprite.visible = false;
      }
    }

    // Sincronizar arma empunhada na mesma direção e frame de ação
    if (weaponSprite) {
      if (currentWeaponManifest) {
        const weaponFrames = currentWeaponManifest[animKey] ||
                             currentWeaponManifest[`${player.dir}-0`] ||
                             currentWeaponManifest["0-0"];
        if (weaponFrames && weaponFrames.length > 0) {
          const wFrameData = weaponFrames[player.frameIdx % weaponFrames.length];
          const wTex = textureCache[wFrameData.file];
          if (wTex) {
            weaponSprite.texture = wTex;
            weaponSprite.anchor.set(0.5, 110 / 150);
            weaponSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
            weaponSprite.visible = true;
          }
        }
      } else {
        weaponSprite.visible = false;
      }
    }'''

if old_anim_sync in text:
    text = text.replace(old_anim_sync, new_anim_sync)
    print("4. Added wingSprite animation synchronization")
else:
    print("Warning: old_anim_sync not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print("Part 1 of main.js updated!")
