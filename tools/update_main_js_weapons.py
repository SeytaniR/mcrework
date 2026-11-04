import sys

with open('web/main.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add weaponSprite to playerContainer
target1 = '''  const charSprite = new PIXI.Sprite();
  charSprite.anchor.set(0.5, 110 / 150);
  charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
  charSprite.scale.set(0.70);
  playerContainer.addChild(charSprite);'''

replacement1 = '''  const charSprite = new PIXI.Sprite();
  charSprite.anchor.set(0.5, 110 / 150);
  charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
  charSprite.scale.set(0.70);
  playerContainer.addChild(charSprite);

  // Sprite animado da Arma Empunhada (sincronizada milimetricamente com o corpo)
  const weaponSprite = new PIXI.Sprite();
  weaponSprite.anchor.set(0.5, 110 / 150);
  weaponSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
  weaponSprite.scale.set(0.70);
  weaponSprite.visible = false;
  playerContainer.addChild(weaponSprite);'''

if target1 in code:
    code = code.replace(target1, replacement1, 1)
    print("1. Added weaponSprite to playerContainer.")
else:
    t1_norm = target1.replace('\r\n', '\n')
    c_norm = code.replace('\r\n', '\n')
    if t1_norm in c_norm:
        code = c_norm.replace(t1_norm, replacement1.replace('\r\n', '\n'), 1)
        print("1. Added weaponSprite with LF.")
    else:
        print("ERROR: target1 not found!")

# 2. Add weapon state variables & helper functions
target2 = '''  // 6. Entidade do Jogador & Parâmetros'''

replacement2 = '''  // Sistema de Arma Empunhada (Armaria & Combate Visual)
  let playerEquippedWeapon = null;
  let currentWeaponManifest = null;
  let currentWeaponModel = null;

  async function equipWeapon(item) {
    if (!item) {
      playerEquippedWeapon = null;
      currentWeaponModel = null;
      currentWeaponManifest = null;
      if (weaponSprite) weaponSprite.visible = false;
      localStorage.removeItem("mc_equipped_weapon_id");
      showWeaponToast("Arma desempunhada.");
      updateEquippedWeaponUI();
      if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
      return;
    }

    const modelId = item.active_weapon_model || item.model_id || "equip_mc1_000001";
    playerEquippedWeapon = item;
    currentWeaponModel = modelId;
    localStorage.setItem("mc_equipped_weapon_id", String(item.id));

    try {
      const manifestUrl = `assets/weapons/${modelId}/char_manifest.json?v=1.5.1`;
      const manifest = await fetch(manifestUrl).then(r => r.json());
      currentWeaponManifest = manifest;

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
      if (weaponSprite) weaponSprite.visible = true;
      showWeaponToast(`⚔️ Empunhado: ${item.name}!`);
    } catch (e) {
      console.warn("Erro ao carregar modelo da arma:", modelId, e);
      showWeaponToast(`⚔️ Arma selecionada: ${item.name}`);
    }

    updateEquippedWeaponUI();
    if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
  }

  function showWeaponToast(msg) {
    let toast = document.getElementById("toast-weapon");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "toast-weapon";
      toast.className = "toast-weapon-equip";
      document.body.appendChild(toast);
    }
    toast.innerText = msg;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2500);
  }

  function updateEquippedWeaponUI() {
    const drawerWeapon = document.getElementById("drawer-weapon");
    const btnUnequip = document.getElementById("btn-unequip-weapon");
    if (drawerWeapon) {
      if (playerEquippedWeapon) {
        drawerWeapon.innerText = `⚔️ ${playerEquippedWeapon.name}`;
        drawerWeapon.style.color = playerEquippedWeapon.quality_color || "#ebcb8b";
      } else {
        drawerWeapon.innerText = "Nenhuma (Desarmado)";
        drawerWeapon.style.color = "#94a3b8";
      }
    }
    if (btnUnequip) {
      btnUnequip.style.display = playerEquippedWeapon ? "inline-block" : "none";
      btnUnequip.onclick = () => equipWeapon(null);
    }
  }

  // 6. Entidade do Jogador & Parâmetros'''

if target2 in code:
    code = code.replace(target2, replacement2, 1)
    print("2. Added weapon state variables & helper functions.")
else:
    t2_norm = target2.replace('\r\n', '\n')
    c_norm = code.replace('\r\n', '\n')
    if t2_norm in c_norm:
        code = c_norm.replace(t2_norm, replacement2.replace('\r\n', '\n'), 1)
        print("2. Added weapon state variables with LF.")
    else:
        print("ERROR: target2 not found!")

# 3. Synchronize weaponSprite frame in updatePlayerAnimation
target3 = '''      const currentFrameData = animFrames[player.frameIdx % animFrames.length];
      const tex = textureCache[currentFrameData.file];
      if (tex) {
        charSprite.texture = tex;
        charSprite.anchor.set(0.5, 110 / 150);
        charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
      }
    }
  }'''

replacement3 = '''      const currentFrameData = animFrames[player.frameIdx % animFrames.length];
      const tex = textureCache[currentFrameData.file];
      if (tex) {
        charSprite.texture = tex;
        charSprite.anchor.set(0.5, 110 / 150);
        charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
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
    }
  }'''

if target3 in code:
    code = code.replace(target3, replacement3, 1)
    print("3. Added weapon animation sync in updatePlayerAnimation.")
else:
    t3_norm = target3.replace('\r\n', '\n')
    c_norm = code.replace('\r\n', '\n')
    if t3_norm in c_norm:
        code = c_norm.replace(t3_norm, replacement3.replace('\r\n', '\n'), 1)
        print("3. Added weapon animation sync with LF.")
    else:
        print("ERROR: target3 not found!")

# 4. Add equip button to weapon cards in renderEquipmentGrid
target4 = '''          <div class="equipment-card-footer">
            <span class="equipment-durability">🛡️ Durabilidade: ${item.endure_max || '100%'}</span>
            <span class="equipment-quality-badge" style="background: ${qualityColor}22; color: ${qualityColor}; border: 1px solid ${qualityColor}55;">
              ${item.quality}
            </span>
          </div>'''

replacement4 = '''          <div class="equipment-card-footer">
            <span class="equipment-durability">🛡️ Durabilidade: ${item.endure_max || '100%'}</span>
            ${item.category_group === "weapons" ? `
              <button class="btn-weapon-equip ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'active' : ''}" data-equip-id="${item.id}" title="${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'Clique para desempunhar' : 'Clique para empunhar na mão do personagem'}">
                ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? '⚔️ Equipado' : '🖐️ Empunhar'}
              </button>
            ` : ''}
            <span class="equipment-quality-badge" style="background: ${qualityColor}22; color: ${qualityColor}; border: 1px solid ${qualityColor}55;">
              ${item.quality}
            </span>
          </div>'''

if target4 in code:
    code = code.replace(target4, replacement4, 1)
    print("4. Added equip button to weapon cards in renderEquipmentGrid.")
else:
    t4_norm = target4.replace('\r\n', '\n')
    c_norm = code.replace('\r\n', '\n')
    if t4_norm in c_norm:
        code = c_norm.replace(t4_norm, replacement4.replace('\r\n', '\n'), 1)
        print("4. Added equip button with LF.")
    else:
        print("ERROR: target4 not found!")

# 5. Bind click events for .btn-weapon-equip in bindEquipmentGridEvents
target5 = '''    const btnLoadMore = document.getElementById("btn-equipment-load-more");'''

replacement5 = '''    equipmentGrid.querySelectorAll(".btn-weapon-equip").forEach(btn => {
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

    const btnLoadMore = document.getElementById("btn-equipment-load-more");'''

if target5 in code:
    code = code.replace(target5, replacement5, 1)
    print("5. Added click handler for .btn-weapon-equip.")
else:
    t5_norm = target5.replace('\r\n', '\n')
    c_norm = code.replace('\r\n', '\n')
    if t5_norm in c_norm:
        code = c_norm.replace(t5_norm, replacement5.replace('\r\n', '\n'), 1)
        print("5. Added click handler with LF.")
    else:
        print("ERROR: target5 not found!")

# 6. Initialize saved/default weapon after equipment catalog loads
target6 = '''    renderEquipmentGrid(true);
  }

  // Inicializar Skills & Efeitos após carregar tudo'''

replacement6 = '''    renderEquipmentGrid(true);

    // Restaurar arma empunhada salva ou equipar inicial
    const savedWeaponId = localStorage.getItem("mc_equipped_weapon_id");
    if (savedWeaponId && equipmentList.length > 0) {
      const savedItem = equipmentList.find(x => String(x.id) === String(savedWeaponId));
      if (savedItem) equipWeapon(savedItem);
    } else if (equipmentList.length > 0) {
      // Arma inicial padrão: Tiểu Mộc Maça (id 170)
      const defItem = equipmentList.find(x => x.id === 170) || equipmentList.find(x => x.category_group === "weapons");
      if (defItem) equipWeapon(defItem);
    }
  }

  // Inicializar Skills & Efeitos após carregar tudo'''

if target6 in code:
    code = code.replace(target6, replacement6, 1)
    print("6. Added startup equip initialization.")
else:
    t6_norm = target6.replace('\r\n', '\n')
    c_norm = code.replace('\r\n', '\n')
    if t6_norm in c_norm:
        code = c_norm.replace(t6_norm, replacement6.replace('\r\n', '\n'), 1)
        print("6. Added startup equip initialization with LF.")
    else:
        print("ERROR: target6 not found!")

with open('web/main.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("web/main.js updated successfully!")
