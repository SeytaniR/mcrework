import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_JS_PATH = os.path.join(BASE_DIR, "web", "main.js")

print("Reading web/main.js...")
with open(MAIN_JS_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update updateCamera to frame combat properly
old_camera = """  function updateCamera() {
    if (!cameraFollow) return;
    const screenWidth = app.screen.width;
    const screenHeight = app.screen.height;

    let camX = screenWidth / 2 - player.x * zoomLevel;
    let camY = screenHeight / 2 - player.y * zoomLevel;

    const minX = screenWidth - MAP_WIDTH * zoomLevel;
    const minY = screenHeight - MAP_HEIGHT * zoomLevel;"""

new_camera = """  function updateCamera() {
    if (!cameraFollow) return;
    const screenWidth = app.screen.width;
    const screenHeight = app.screen.height;

    let targetX = player.x;
    let targetY = player.y;
    let anchorYRatio = 0.5;

    // Em modo de combate, foca no ponto médio e ancora no terço superior (26% da tela)
    // para que os combatentes e suas animações fiquem 100% visíveis acima do painel de batalha
    if (isCombatTesting && typeof monster !== 'undefined') {
      targetX = (player.x + monster.x) / 2;
      targetY = (player.y + monster.y) / 2;
      anchorYRatio = screenHeight < 920 ? 0.26 : 0.32;
    }

    let camX = screenWidth / 2 - targetX * zoomLevel;
    let camY = screenHeight * anchorYRatio - targetY * zoomLevel;

    const minX = screenWidth - MAP_WIDTH * zoomLevel;
    const minY = screenHeight - MAP_HEIGHT * zoomLevel;"""

if old_camera in code:
    code = code.replace(old_camera, new_camera, 1)
    print("  [OK] Updated updateCamera for combat framing")
else:
    print("  [WARN] old_camera not found")

# 2. Add toggle minimize logic in openCombatTest and button listener
old_open_combat = """    if (combatTestPanel) combatTestPanel.classList.remove("hidden");
    if (mobileActionBar) mobileActionBar.style.display = "none";
    if (joystickContainer) joystickContainer.style.display = "none";

    setCombatStatus("⚔️ Modo de Combate Ativo! Toque em uma ação abaixo ou ative o Sparring Contínuo.");
  }"""

new_open_combat = """    if (combatTestPanel) {
      combatTestPanel.classList.remove("hidden");
      combatTestPanel.classList.remove("minimized");
      const btnToggle = document.getElementById("btn-toggle-combat-panel");
      if (btnToggle) btnToggle.textContent = "▼ Minimizar";
    }
    if (mobileActionBar) mobileActionBar.style.display = "none";
    if (joystickContainer) joystickContainer.style.display = "none";

    setCombatStatus("⚔️ Modo de Combate Ativo! Toque em uma ação abaixo ou ative o Sparring Contínuo.");
  }

  const btnToggleCombatPanel = document.getElementById("btn-toggle-combat-panel");
  if (btnToggleCombatPanel) {
    btnToggleCombatPanel.addEventListener("click", () => {
      if (!combatTestPanel) return;
      const isMin = combatTestPanel.classList.toggle("minimized");
      btnToggleCombatPanel.textContent = isMin ? "▲ Expandir" : "▼ Minimizar";
    });
  }"""

if old_open_combat in code:
    code = code.replace(old_open_combat, new_open_combat, 1)
    print("  [OK] Added btn-toggle-combat-panel listener and reset")
else:
    print("  [WARN] old_open_combat not found")

# 3. Add Costume / Modas System right after equipWing
old_wing_system = """  // Sistema de Asas Visuais Equipadas
  let playerEquippedWing = null;
  let currentWingManifest = null;
  let currentWingModel = null;"""

new_wing_system = """  // Sistema de Asas Visuais Equipadas
  let playerEquippedWing = null;
  let currentWingManifest = null;
  let currentWingModel = null;

  // Sistema de Modas, Trajes & Skins Visuais
  let playerEquippedCostume = null;
  const COSTUME_MODELS_POOL = [
    "PC_FEMALE_010017", // Traje Casual Estudante
    "PC_FEMALE_010005", // Costume de Gala / Festa
    "PC_FEMALE_010010", // Vestido Nupcial Real
    "PC_FEMALE_010012", // Quimono Oriental da Primavera
    "PC_FEMALE_010016", // Traje Angelical com Asas Divinas
    "PC_FEMALE_010018", // Armadura Valquíria da Alvorada
    "PC_FEMALE_010019", // Traje Festivo Celebração
    "PC_FEMALE_010020", // Armadura Rainha Dracônica
    "PC_FEMALE_010011"  // Armadura Cerimonial Dourada
  ];

  function getCostumeModelForItem(item) {
    const name = (item.name || "").toLowerCase();
    if (name.includes("học sinh") || name.includes("estudante") || name.includes("escola")) return "PC_FEMALE_010017";
    if (name.includes("cưới") || name.includes("nupcial") || name.includes("noiva")) return "PC_FEMALE_010010";
    if (name.includes("gala") || name.includes("festa") || name.includes("dạ hội") || name.includes("lễ phục")) return "PC_FEMALE_010005";
    if (name.includes("kimono") || name.includes("quimono") || name.includes("trung hoa") || name.includes("âu lạc")) return "PC_FEMALE_010012";
    if (name.includes("thiên sứ") || name.includes("anjo") || name.includes("angelical") || name.includes("divin")) return "PC_FEMALE_010016";
    if (name.includes("hoàng kim") || name.includes("valquíria") || name.includes("dourad")) return "PC_FEMALE_010018";
    if (name.includes("long") || name.includes("dracônica") || name.includes("dragão") || name.includes("rồng")) return "PC_FEMALE_010020";
    if (name.includes("giáng sinh") || name.includes("natal") || name.includes("năm mới") || name.includes("lễ hội") || name.includes("festivo")) return "PC_FEMALE_010019";
    if (name.includes("chiến binh") || name.includes("cerimonial")) return "PC_FEMALE_010011";

    return COSTUME_MODELS_POOL[Math.abs(Number(item.id) || 0) % COSTUME_MODELS_POOL.length];
  }

  async function equipCostume(item) {
    if (!item) {
      playerEquippedCostume = null;
      localStorage.removeItem("mc_equipped_costume_id");
      await setCharacterModel("PC_MALE_000011");
      showWeaponToast("Moda desequipada. Guerreiro Evoluído restaurado.");
      if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
      return;
    }

    const modelId = getCostumeModelForItem(item);
    playerEquippedCostume = item;
    localStorage.setItem("mc_equipped_costume_id", String(item.id));

    const targetMeta = Array.isArray(classesList) ? classesList.find(x => x.id === modelId) : null;
    await setCharacterModel(modelId, targetMeta);
    showWeaponToast(`👗 Moda Equipada: ${item.name}!`);
    if (typeof renderEquipmentGrid === 'function') renderEquipmentGrid(false);
  }"""

if old_wing_system in code:
    code = code.replace(old_wing_system, new_wing_system, 1)
    print("  [OK] Added Costume Equipping functions")
else:
    print("  [WARN] old_wing_system not found")

# 4. Add btn-costume-equip into renderEquipmentGrid and bindEquipmentGridEvents
old_card_footer = """            ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? `
              <button class="btn-wing-equip ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'active' : ''}" data-wing-id="${item.id}" title="${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'Clique para desequipar as asas' : 'Clique para equipar as asas nas costas do personagem'}">
                ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? '🪽 Equipado' : '🪽 Equipar'}
              </button>
            ` : ''}"""

new_card_footer = """            ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? `
              <button class="btn-wing-equip ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'active' : ''}" data-wing-id="${item.id}" title="${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? 'Clique para desequipar as asas' : 'Clique para equipar as asas nas costas do personagem'}">
                ${playerEquippedWing && (String(playerEquippedWing.id) === String(item.id) || playerEquippedWing.model_id === item.model_id) ? '🪽 Equipado' : '🪽 Equipar'}
              </button>
            ` : ''}
            ${(item.category_group === "wings_costumes" || item.position === 21) ? `
              <button class="btn-costume-equip ${playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id) ? 'active' : ''}" data-costume-id="${item.id}" title="${playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id) ? 'Clique para remover moda' : 'Clique para provar e vestir a skin no personagem'}">
                ${playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id) ? '👗 Vestindo' : '✨ Provar Traje'}
              </button>
            ` : ''}"""

if old_card_footer in code:
    code = code.replace(old_card_footer, new_card_footer, 1)
    print("  [OK] Added btn-costume-equip into equipment card footer")
else:
    print("  [WARN] old_card_footer not found")

# Bind events for costume button
old_bind_events = """    equipmentGrid.querySelectorAll(".btn-wing-equip").forEach(btn => {
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
    });"""

new_bind_events = """    equipmentGrid.querySelectorAll(".btn-wing-equip").forEach(btn => {
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
    });

    equipmentGrid.querySelectorAll(".btn-costume-equip").forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        const cid = btn.dataset.costumeId;
        const item = equipmentList.find(x => String(x.id) === String(cid));
        if (!item) return;
        if (playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id)) {
          equipCostume(null);
        } else {
          equipCostume(item);
        }
      };
    });"""

if old_bind_events in code:
    code = code.replace(old_bind_events, new_bind_events, 1)
    print("  [OK] Added btn-costume-equip event listeners")
else:
    print("  [WARN] old_bind_events not found")

# Add drawer button listener for costumes and restore saved costume
old_restore_wings = """  // Restaurar asas equipadas salvas ou equipar inicial
  const savedWingId = localStorage.getItem("mc_equipped_wing_id");
  if (savedWingId) {
    const savedW = (Array.isArray(wingsCatalogData) ? wingsCatalogData.find(x => String(x.id) === String(savedWingId)) : null) ||
                   (equipmentList && equipmentList.find(x => String(x.id) === String(savedWingId)));
    if (savedW) equipWing(savedW);
  } else if (Array.isArray(wingsCatalogData) && wingsCatalogData.length > 0) {
    const defW = wingsCatalogData.find(x => x.model_id === "equip_wing_001001") || wingsCatalogData[0];
    if (defW) equipWing(defW);
  }"""

new_restore_wings = """  // Restaurar asas equipadas salvas ou equipar inicial
  const savedWingId = localStorage.getItem("mc_equipped_wing_id");
  if (savedWingId) {
    const savedW = (Array.isArray(wingsCatalogData) ? wingsCatalogData.find(x => String(x.id) === String(savedWingId)) : null) ||
                   (equipmentList && equipmentList.find(x => String(x.id) === String(savedWingId)));
    if (savedW) equipWing(savedW);
  } else if (Array.isArray(wingsCatalogData) && wingsCatalogData.length > 0) {
    const defW = wingsCatalogData.find(x => x.model_id === "equip_wing_001001") || wingsCatalogData[0];
    if (defW) equipWing(defW);
  }

  // Atalho do drawer para Trajes & Modas
  const btnDrawerCostumes = document.getElementById("btn-drawer-all-costumes");
  if (btnDrawerCostumes) {
    btnDrawerCostumes.addEventListener("click", () => {
      closeDrawer();
      openEquipmentModal();
      selectedEquipmentFilter = "wings_costumes";
      if (equipmentFilterPills) {
        equipmentFilterPills.querySelectorAll(".pill-filter").forEach(b => {
          b.classList.toggle("active", b.dataset.filter === "wings_costumes");
        });
      }
      renderEquipmentGrid(true);
    });
  }

  // Restaurar traje equipado salvo
  const savedCostumeId = localStorage.getItem("mc_equipped_costume_id");
  if (savedCostumeId && equipmentList && equipmentList.length > 0) {
    const savedC = equipmentList.find(x => String(x.id) === String(savedCostumeId));
    if (savedC) equipCostume(savedC);
  }"""

if old_restore_wings in code:
    code = code.replace(old_restore_wings, new_restore_wings, 1)
    print("  [OK] Added drawer costume listener and saved costume restore")
else:
    print("  [WARN] old_restore_wings not found")

# 5. Update Skills & VFX rendering and Floating Bar
old_vfx_card = """            <div class="skill-card" data-effect-id="${eff.id}" onclick="window.__playVFXDirect(${eff.id})">
            <div class="skill-card-top">
              <div class="skill-icon-wrapper" style="background: radial-gradient(circle, #4c566a 20%, #2e3440 90%);">
                <span style="font-size: 20px;">⚡</span>
              </div>
              <div class="skill-card-meta">
                <div class="skill-title-row">
                  <h4 class="skill-card-name">Efeito #${eff.id}</h4>
                  <span class="skill-badge-level">${eff.frames} frames</span>
                </div>
                <div class="skill-tags-row">
                  <span class="skill-type-tag">VFX Animado</span>
                  <span class="skill-class-tag">${eff.width}x${eff.height}px</span>
                </div>
              </div>
            </div>
            <p class="skill-card-desc">Animação gráfica oficial em spritesheet WebP: ${eff.swf}. Duração: ~${eff.duration_ms}ms.</p>
            <div class="skill-card-stats">
              <span class="stat-pill sp">⏱️ ${eff.duration_ms}ms</span>
              <span class="stat-pill area">📐 ${eff.frames} Frames</span>
            </div>
            <button class="btn-cast-skill" onclick="event.stopPropagation(); window.__playVFXDirect(${eff.id})">
              ✨ Disparar Efeito (#${eff.id})
            </button>
          </div>"""

new_vfx_card = """            <div class="skill-card" data-effect-id="${eff.id}" onclick="window.__playVFXDirect(${eff.id})">
            <div class="skill-card-top">
              <div class="skill-icon-wrapper" style="background: radial-gradient(circle, #4c566a 20%, #2e3440 90%);">
                <img src="${eff.thumb || `assets/effects/${eff.id}/thumb.png`}" alt="VFX #${eff.id}" class="vfx-thumb-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" />
                <span style="display:none; font-size: 20px;">⚡</span>
              </div>
              <div class="skill-card-meta">
                <div class="skill-title-row">
                  <h4 class="skill-card-name">Efeito #${eff.id}</h4>
                  <span class="skill-badge-level">${eff.frames} frames</span>
                </div>
                <div class="skill-tags-row">
                  <span class="skill-type-tag">VFX Animado</span>
                  <span class="skill-class-tag">${eff.width}x${eff.height}px</span>
                </div>
              </div>
            </div>
            <p class="skill-card-desc">Animação gráfica oficial em spritesheet WebP: ${eff.swf}. Duração: ~${eff.duration_ms}ms.</p>
            <div class="skill-card-stats">
              <span class="stat-pill sp">⏱️ ${eff.duration_ms}ms</span>
              <span class="stat-pill area">📐 ${eff.frames} Frames</span>
            </div>
            <button class="btn-cast-skill" onclick="event.stopPropagation(); window.__playVFXDirect(${eff.id})">
              ✨ Disparar Efeito (#${eff.id})
            </button>
          </div>"""

if old_vfx_card in code:
    code = code.replace(old_vfx_card, new_vfx_card, 1)
    print("  [OK] Updated VFX cards with real thumbnail preview")
else:
    print("  [WARN] old_vfx_card not found")

# Replace window.__castSkillFromCard and window.__playVFXDirect with floating bar support
old_helpers = """  // Window helpers for click handlers
  window.__castSkillFromCard = (skillId) => {
    const s = skillsList.find(x => x.id === skillId);
    if (!s) return;
    executeSkill(s);
  };

  window.__playVFXDirect = (effId) => {
    setCombatStatus(`⚡ Disparando Efeito Especial #${effId}!`);
    setAction(activeManifest && activeManifest[`${player.dir}-10`] ? 10 : 7);
    playSkillVFX(effId, monster.x, monster.y - 30, { shake: true, speed: 0.45 });
    setMonsterAction(5);
    spawnCombatText(`⚡ VFX #${effId}`, monster.x, monster.y - 65, 0xebcb8b);
    setTimeout(() => {
      setAction(0);
      setMonsterAction(0);
    }, 450);
  };"""

new_helpers = """  // Controles da Barra Flutuante de Teste de Habilidade / VFX
  let lastTriggeredSkillOrVFX = null;
  const skillsFloatingBar = document.getElementById("skills-floating-bar");
  const skillsFloatingIcon = document.getElementById("skills-floating-icon");
  const skillsFloatingTitle = document.getElementById("skills-floating-title");
  const skillsFloatingSub = document.getElementById("skills-floating-sub");
  const btnFloatingRepeat = document.getElementById("btn-floating-repeat");
  const btnFloatingGrimorio = document.getElementById("btn-floating-grimorio");
  const btnFloatingClose = document.getElementById("btn-floating-close");
  const btnMinimizeSkillsModal = document.getElementById("btn-minimize-skills-modal");

  function showSkillsFloatingBar(title, sub, iconHtml, repeatFn) {
    if (!skillsFloatingBar) return;
    if (skillsFloatingTitle) skillsFloatingTitle.textContent = title;
    if (skillsFloatingSub) skillsFloatingSub.textContent = sub;
    if (skillsFloatingIcon) skillsFloatingIcon.innerHTML = iconHtml;
    skillsFloatingBar.classList.remove("hidden");
    lastTriggeredSkillOrVFX = repeatFn;
  }

  function hideSkillsFloatingBar() {
    if (skillsFloatingBar) skillsFloatingBar.classList.add("hidden");
  }

  if (btnFloatingRepeat) {
    btnFloatingRepeat.addEventListener("click", () => {
      if (typeof lastTriggeredSkillOrVFX === 'function') lastTriggeredSkillOrVFX();
    });
  }
  if (btnFloatingGrimorio) {
    btnFloatingGrimorio.addEventListener("click", () => {
      hideSkillsFloatingBar();
      openSkillsModal();
    });
  }
  if (btnFloatingClose) {
    btnFloatingClose.addEventListener("click", hideSkillsFloatingBar);
  }
  if (btnMinimizeSkillsModal) {
    btnMinimizeSkillsModal.addEventListener("click", () => {
      closeSkillsModal();
      showSkillsFloatingBar("Grimório Minimizado", "Toque em Grimório para reabrir", "🔮", null);
    });
  }

  // Window helpers for click handlers
  window.__castSkillFromCard = (skillId) => {
    const s = skillsList.find(x => x.id === skillId);
    if (!s) return;
    closeSkillsModal();
    executeSkill(s);
    const iconHtml = s.icon ? `<img src="${s.icon}" class="floating-vfx-img" onerror="this.replaceWith('🔮');" />` : "🔮";
    showSkillsFloatingBar(s.name, `Disparando no mapa (VFX #${s.effect_id})`, iconHtml, () => executeSkill(s));
  };

  window.__playVFXDirect = (effId) => {
    closeSkillsModal();
    const eff = effectsList.find(x => x.id === effId);
    const effTitle = eff ? `Efeito #${eff.id} (${eff.frames}f)` : `VFX #${effId}`;
    const effThumb = eff?.thumb || `assets/effects/${effId}/thumb.png`;
    const iconHtml = `<img src="${effThumb}" class="floating-vfx-img" onerror="this.replaceWith('⚡');" />`;

    const playFn = () => {
      setCombatStatus(`⚡ Disparando Efeito Especial #${effId}!`);
      setAction(activeManifest && activeManifest[`${player.dir}-10`] ? 10 : 7);
      playSkillVFX(effId, monster.x, monster.y - 30, { shake: true, speed: 0.45 });
      setMonsterAction(5);
      spawnCombatText(`⚡ VFX #${effId}`, monster.x, monster.y - 65, 0xebcb8b);
      setTimeout(() => {
        setAction(0);
        setMonsterAction(0);
      }, 450);
    };

    playFn();
    showSkillsFloatingBar(effTitle, "Executando efeito visual...", iconHtml, playFn);
  };"""

if old_helpers in code:
    code = code.replace(old_helpers, new_helpers, 1)
    print("  [OK] Updated skills & VFX execution with auto-minimize and floating bar")
else:
    print("  [WARN] old_helpers not found")

with open(MAIN_JS_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("web/main.js updated successfully.")
