import sys, os, re

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('web/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Promise.all destructuring and fetch
old_promise = '''  const [npcsData, masksData, colArrayBuffer, initialMonsterMeta, initialMonsterSheet, classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] }))
  ]);'''

new_promise = '''  const [
    npcsData, masksData, colArrayBuffer, initialMonsterMeta, initialMonsterSheet,
    classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData,
    skillsCatalogData, effectsCatalogData
  ] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] })),
    fetch("assets/skills/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ([])),
    fetch("assets/effects/catalog.json?v=1.3.2").then(r => r.json()).catch(() => ([]))
  ]);'''

if old_promise in content:
    content = content.replace(old_promise, new_promise, 1)
    print("Updated Promise.all in main.js!")
else:
    print("Warning: old_promise not matched exactly, checking variants...")
    # Try normalized whitespace
    # Look for Promise.all
    m = re.search(r'const \[npcsData.*?\] = await Promise\.all\(\[.*?fetch\("assets/maps/catalog\.json.*?\]\);', content, re.DOTALL)
    if m:
        content = content[:m.start()] + new_promise + content[m.end():]
        print("Updated Promise.all via regex in main.js!")
    else:
        print("Error: Could not find Promise.all block!")

# 2. Add VFX and Skill Execution System
vfx_system_code = '''
  // ==========================================
  // SISTEMA DE EFEITOS ESPECIAIS & VFX (128 Efeitos)
  // ==========================================
  const loadedEffectSheets = new Map();

  async function playSkillVFX(effectId, targetX, targetY, options = {}) {
    if (!effectId) effectId = 10008;
    const effIdStr = String(effectId);
    let sheet = loadedEffectSheets.get(effIdStr);

    if (!sheet) {
      try {
        sheet = await PIXI.Assets.load(`assets/effects/${effIdStr}/atlas.json`);
        loadedEffectSheets.set(effIdStr, sheet);
      } catch (err) {
        console.warn(`[VFX] Erro ao carregar efeito #${effIdStr}, usando fallback 10008:`, err);
        try {
          sheet = await PIXI.Assets.load(`assets/effects/10008/atlas.json`);
        } catch (e2) {
          return null;
        }
      }
    }

    if (!sheet) return null;

    let animFrames = sheet.animations && sheet.animations['play'] ? sheet.animations['play'] : Object.values(sheet.textures);
    if (!animFrames || animFrames.length === 0) return null;

    const vfxSprite = new PIXI.AnimatedSprite(animFrames);
    vfxSprite.anchor.set(0.5, 0.5);
    vfxSprite.position.set(targetX, targetY);
    vfxSprite.loop = false;
    vfxSprite.animationSpeed = options.speed || 0.45;

    // Blend mode aditivo para efeitos mágicos e brilhantes
    const isAdditive = options.additive !== undefined ? options.additive : true;
    if (isAdditive) {
      vfxSprite.blendMode = PIXI.BLEND_MODES.ADD;
    }

    vfxSprite.zIndex = (options.zIndex !== undefined) ? options.zIndex : 999999;
    entitiesContainer.addChild(vfxSprite);
    vfxSprite.play();

    if (options.shake) {
      shakeScreen(5, 130);
    }

    vfxSprite.onComplete = () => {
      entitiesContainer.removeChild(vfxSprite);
      vfxSprite.destroy();
    };

    return vfxSprite;
  }

  function shakeScreen(intensity = 5, durationMs = 120) {
    const origX = app.stage.position.x;
    const origY = app.stage.position.y;
    const startTime = Date.now();

    function doShake() {
      const elapsed = Date.now() - startTime;
      if (elapsed < durationMs) {
        const factor = 1 - (elapsed / durationMs);
        app.stage.position.x = origX + (Math.random() - 0.5) * intensity * 2 * factor;
        app.stage.position.y = origY + (Math.random() - 0.5) * intensity * 2 * factor;
        requestAnimationFrame(doShake);
      } else {
        app.stage.position.x = origX;
        app.stage.position.y = origY;
      }
    }
    doShake();
  }

  async function executeSkill(skill) {
    if (isActionExecuting) return;
    isActionExecuting = true;

    const sName = skill.name || "Habilidade";
    const effId = skill.effect_id || 10008;
    setCombatStatus(`🔮 Disparando: ${sName} (VFX #${effId})!`);

    let actionId = 7;
    let isMelee = false;
    let targetIsPlayer = (skill.target_type === 1 || skill.target_type === 2 || skill.target_type === 3 || skill.kind === 3);

    if (skill.type === 1) {
      actionId = 3;
      isMelee = true;
    } else if (skill.type === 2) {
      actionId = (activeManifest && activeManifest[`${player.dir}-9`]) ? 9 : 3;
    } else if (skill.type === 5 || skill.type === 9) {
      actionId = (activeManifest && activeManifest[`${player.dir}-8`]) ? 8 : 7;
    } else if (skill.type === 6 || skill.type === 7) {
      actionId = (activeManifest && activeManifest[`${player.dir}-8`]) ? 8 : 7;
    } else if (skill.category === "class" && activeManifest && activeManifest[`${player.dir}-10`]) {
      actionId = 10;
    }

    setAction(actionId);

    let targetX = monster.x;
    let targetY = monster.y - 30;

    if (targetIsPlayer) {
      targetX = player.x;
      targetY = player.y - 30;
    } else if (isMelee) {
      playerContainer.x = player.x + 18;
    }

    await new Promise(r => setTimeout(r, isMelee ? 150 : 250));

    playSkillVFX(effId, targetX, targetY, {
      shake: !targetIsPlayer,
      speed: 0.45
    });

    if (!targetIsPlayer) {
      setMonsterAction(5);
      const dmg = Math.floor(Math.random() * 850) + 420;
      spawnCombatText(`💥 -${dmg}`, targetX, targetY - 40, 0xffe066);
    } else {
      const heal = Math.floor(Math.random() * 400) + 250;
      spawnCombatText(`💚 +${heal}`, targetX, targetY - 40, 0x88c0d0);
    }

    await new Promise(r => setTimeout(r, 450));
    playerContainer.x = player.x;
    setAction(0);
    setMonsterAction(0);
    isActionExecuting = false;
    setCombatStatus("Pronto para o próximo teste de ação.");
  }
'''

# 3. Enhance testPlayerAttack, testPlayerSkill, testPlayerUltimate with real VFX
old_attack = '''    setAction(3); // Golpe Físico
    playerContainer.x = player.x + 18; // Avanço

    await new Promise(r => setTimeout(r, 260));
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("💥 GOLPE!", monster.x, monster.y - 65, 0xffe066);'''

new_attack = '''    setAction(3); // Golpe Físico
    playerContainer.x = player.x + 18; // Avanço

    await new Promise(r => setTimeout(r, 200));
    playSkillVFX(10008, monster.x, monster.y - 30, { shake: true, speed: 0.5 });
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("💥 GOLPE! -540", monster.x, monster.y - 65, 0xffe066);'''

content = content.replace(old_attack, new_attack, 1)

old_skill = '''    setAction(7); // Magia

    await new Promise(r => setTimeout(r, 350));
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("🔮 MAGIA!", monster.x, monster.y - 65, 0xb48ead);'''

new_skill = '''    setAction(7); // Magia

    await new Promise(r => setTimeout(r, 280));
    playSkillVFX(302, monster.x, monster.y - 30, { shake: true, speed: 0.45 });
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("🔮 EXPLOSÃO ARCANA! -780", monster.x, monster.y - 65, 0xb48ead);'''

content = content.replace(old_skill, new_skill, 1)

old_ult = '''    setAction(activeManifest[`${player.dir}-10`] ? 10 : 3);
    player.frameDuration = 0.05;
    playerContainer.x = player.x + 22;

    await new Promise(r => setTimeout(r, 280));
    spawnCombatText("⚡ COMBO!", monster.x, monster.y - 70, 0xebcb8b);

    await new Promise(r => setTimeout(r, 280));
    spawnCombatText("⚡ HIT 2!", monster.x, monster.y - 80, 0xebcb8b);

    await new Promise(r => setTimeout(r, 320));
    setMonsterAction(5);
    spawnCombatText("💥 FINALIZADOR!", monster.x, monster.y - 90, 0xff3333);'''

new_ult = '''    setAction(activeManifest[`${player.dir}-10`] ? 10 : 3);
    player.frameDuration = 0.05;
    playerContainer.x = player.x + 22;

    await new Promise(r => setTimeout(r, 240));
    playSkillVFX(10001, monster.x, monster.y - 30, { shake: false, speed: 0.5 });
    spawnCombatText("⚡ COMBO!", monster.x, monster.y - 70, 0xebcb8b);

    await new Promise(r => setTimeout(r, 280));
    playSkillVFX(410, monster.x, monster.y - 30, { shake: true, speed: 0.5 });
    spawnCombatText("⚡ GOLPE FINAL! -1250", monster.x, monster.y - 80, 0xebcb8b);

    await new Promise(r => setTimeout(r, 320));
    setMonsterAction(5);
    spawnCombatText("💥 CRÍTICO!", monster.x, monster.y - 90, 0xff3333);'''

content = content.replace(old_ult, new_ult, 1)

# Insert VFX code right before resetCombatPoses
if 'function resetCombatPoses()' in content and 'playSkillVFX(' not in content:
    content = content.replace('function resetCombatPoses()', vfx_system_code + '\n  function resetCombatPoses()', 1)
    print("Inserted VFX system functions into main.js!")

# 4. Add Skills Modal Controller & Event Listeners
skills_modal_code = '''
  // ==========================================
  // MODAL 6: GRIMÓRIO DE HABILIDADES & EFEITOS ESPECIAIS (1.923 Habilidades / 128 VFX)
  // ==========================================
  const modalSkills = document.getElementById("modal-skills");
  const skillsGrid = document.getElementById("skills-grid-container");
  const skillsSearchInput = document.getElementById("skills-search-input");
  const skillsFilterPills = document.getElementById("skills-filter-pills");

  let skillsList = Array.isArray(skillsCatalogData) ? skillsCatalogData : [];
  let effectsList = Array.isArray(effectsCatalogData) ? effectsCatalogData : [];
  let selectedSkillFilter = "all";
  let skillsRenderCount = 36; // Paginação virtual para alta performance no DOM mobile

  function renderSkillsGrid(resetPagination = true) {
    if (!skillsGrid) return;
    if (resetPagination) skillsRenderCount = 36;

    const q = (skillsSearchInput ? skillsSearchInput.value : "").trim().toLowerCase();

    // Se estiver no filtro 'vfx', mostra diretamente o catálogo de 128 animações VFX
    if (selectedSkillFilter === "vfx") {
      const filteredEffects = effectsList.filter(eff => {
        if (!q) return true;
        return `${eff.id} ${eff.num} ${eff.swf} ${eff.frames}`.toLowerCase().includes(q);
      });

      const slice = filteredEffects.slice(0, skillsRenderCount);
      let html = slice.map(eff => {
        return `
          <div class="skill-card" data-effect-id="${eff.id}" onclick="window.__playVFXDirect(${eff.id})">
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
          </div>
        `;
      }).join("");

      if (filteredEffects.length > skillsRenderCount) {
        html += `
          <div style="grid-column: 1 / -1; text-align: center; padding: 15px;">
            <button id="btn-skills-load-more" class="btn" style="padding: 10px 24px; border-radius: 20px; background: rgba(180, 142, 173, 0.3); border: 1px solid #b48ead; color: #eceff4; font-weight: bold; cursor: pointer;">
              Carregar Mais Efeitos (+36) ➔
            </button>
          </div>
        `;
      }
      skillsGrid.innerHTML = html;
      bindSkillsGridEvents();
      return;
    }

    // Filtro padrão de Habilidades
    const filteredSkills = skillsList.filter(s => {
      if (selectedSkillFilter === "class" && s.category !== "class") return false;
      if (selectedSkillFilter === "warrior" && (!s.req_class_ids || !s.req_class_ids.includes(1))) return false;
      if (selectedSkillFilter === "bard" && (!s.req_class_ids || !s.req_class_ids.includes(2))) return false;
      if (selectedSkillFilter === "priest" && (!s.req_class_ids || !s.req_class_ids.includes(3))) return false;
      if (selectedSkillFilter === "gunner" && (!s.req_class_ids || !s.req_class_ids.includes(4))) return false;
      if (selectedSkillFilter === "hunter" && (!s.req_class_ids || !s.req_class_ids.includes(5))) return false;
      if (selectedSkillFilter === "paladin" && (!s.req_class_ids || !s.req_class_ids.includes(6))) return false;
      if (selectedSkillFilter === "pet" && s.category !== "pet") return false;
      if (selectedSkillFilter === "buff" && s.kind !== 3 && s.type !== 5 && s.type !== 6 && s.type !== 7 && s.type !== 9) return false;

      if (q) {
        const str = `${s.name} ${s.code_name} ${s.type_name} ${s.kind_name} ${s.description} ${s.id}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    const slice = filteredSkills.slice(0, skillsRenderCount);
    let html = slice.map(s => {
      const iconImg = s.icon ? `<img src="${s.icon}" alt="${s.name}" class="skill-icon-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';" /><span style="display:none; font-size: 18px;">🔮</span>` : `<span style="font-size: 18px;">🔮</span>`;
      const classNames = s.req_classes && s.req_classes.length > 0 ? s.req_classes.join(', ') : 'Geral';
      return `
        <div class="skill-card" data-skill-id="${s.id}" onclick="window.__castSkillFromCard(${s.id})">
          <div class="skill-card-top">
            <div class="skill-icon-wrapper">
              ${iconImg}
            </div>
            <div class="skill-card-meta">
              <div class="skill-title-row">
                <h4 class="skill-card-name">${s.name}</h4>
                <span class="skill-badge-level">Nv. Max ${s.max_level}</span>
              </div>
              <div class="skill-tags-row">
                <span class="skill-type-tag">${s.type_name}</span>
                <span class="skill-class-tag">${classNames}</span>
              </div>
            </div>
          </div>
          <p class="skill-card-desc">${s.description || 'Habilidade oficial do Magic Campus.'}</p>
          <div class="skill-card-stats">
            ${s.use_mp ? `<span class="stat-pill mp">💧 MP: ${s.use_mp}</span>` : ''}
            ${s.use_sp ? `<span class="stat-pill sp">⚡ SP: ${s.use_sp}</span>` : ''}
            <span class="stat-pill target">🎯 ${s.target_name} (${s.target_num})</span>
            <span class="stat-pill area">📐 ${s.area_name}</span>
          </div>
          <button class="btn-cast-skill" onclick="event.stopPropagation(); window.__castSkillFromCard(${s.id})">
            ✨ Disparar Habilidade (VFX #${s.effect_id})
          </button>
        </div>
      `;
    }).join("");

    if (filteredSkills.length > skillsRenderCount) {
      html += `
        <div style="grid-column: 1 / -1; text-align: center; padding: 15px;">
          <button id="btn-skills-load-more" class="btn" style="padding: 10px 24px; border-radius: 20px; background: rgba(180, 142, 173, 0.3); border: 1px solid #b48ead; color: #eceff4; font-weight: bold; cursor: pointer;">
            Carregar Mais Habilidades (${slice.length} de ${filteredSkills.length}) ➔
          </button>
        </div>
      `;
    }
    skillsGrid.innerHTML = html;
    bindSkillsGridEvents();
  }

  function bindSkillsGridEvents() {
    const btnLoadMore = document.getElementById("btn-skills-load-more");
    if (btnLoadMore) {
      btnLoadMore.onclick = () => {
        skillsRenderCount += 36;
        renderSkillsGrid(false);
      };
    }
  }

  // Window helpers for click handlers
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
  };

  function openSkillsModal() {
    if (modalSkills) {
      modalSkills.classList.remove("hidden");
      renderSkillsGrid();
    }
  }
  function closeSkillsModal() {
    if (modalSkills) modalSkills.classList.add("hidden");
  }

  const btnTopSkills = document.getElementById("btn-open-skills-modal");
  const btnDrawerSkills = document.getElementById("btn-drawer-all-skills");
  const btnCloseSkills = document.getElementById("btn-close-skills-modal");

  if (btnTopSkills) btnTopSkills.addEventListener("click", openSkillsModal);
  if (btnDrawerSkills) btnDrawerSkills.addEventListener("click", () => { closeDrawer(); openSkillsModal(); });
  if (btnCloseSkills) btnCloseSkills.addEventListener("click", closeSkillsModal);

  if (skillsSearchInput) {
    skillsSearchInput.addEventListener("input", () => {
      renderSkillsGrid(true);
    });
  }

  if (skillsFilterPills) {
    skillsFilterPills.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill-filter");
      if (!btn) return;
      skillsFilterPills.querySelectorAll(".pill-filter").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      selectedSkillFilter = btn.dataset.filter || "all";
      renderSkillsGrid(true);
    });
  }
'''

# Append skills modal code before the final updateCamera or at end
content += '\n' + skills_modal_code

with open('web/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated web/main.js successfully!")
