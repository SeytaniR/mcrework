import os, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

new_code = '''  // ==========================================
  // MODAIS DE CATALOGO (CLASSES, MONSTROS/PETS, MONTARIAS & NPCS)
  // ==========================================
  const modalClasses = document.getElementById("modal-classes");
  const modalMonsters = document.getElementById("modal-monsters");
  const modalMounts = document.getElementById("modal-mounts");
  const modalNpcs = document.getElementById("modal-npcs");

  const classesGrid = document.getElementById("classes-grid-container");
  const monstersGrid = document.getElementById("monsters-grid-container");
  const mountsGrid = document.getElementById("mounts-grid-container");
  const npcsGrid = document.getElementById("npcs-grid-container");

  const classesSearchInput = document.getElementById("classes-search-input");
  const monstersSearchInput = document.getElementById("monsters-search-input");
  const mountsSearchInput = document.getElementById("mounts-search-input");
  const npcsSearchInput = document.getElementById("npcs-search-input");

  let classesList = classesCatalogData.classes || [];
  let monstersList = monstersCatalogData.monsters || [];
  let mountsList = mountsCatalogData.mounts || [];
  let npcsList = npcsCatalogData.npcs || [];

  let selectedClassFilter = "all";
  let selectedMonFilter = "all";
  let selectedMountFilter = "all";
  let selectedNpcFilter = "all";

  // 1. GRID DE CLASSES (46 Visuais)
  function renderClassesGrid() {
    if (!classesGrid) return;
    const q = (classesSearchInput ? classesSearchInput.value : "").trim().toLowerCase();

    const filtered = classesList.filter(c => {
      if (selectedClassFilter === "male" && c.gender !== "MALE") return false;
      if (selectedClassFilter === "female" && c.gender !== "FEMALE") return false;
      if (selectedClassFilter === "tier1" && c.tier !== 1) return false;
      if (selectedClassFilter === "tier2" && c.tier !== 2) return false;
      if (selectedClassFilter === "costume" && c.tier !== "costume") return false;
      if (selectedClassFilter === "mount" && c.tier !== "mount") return false;
      if (q) {
        const str = `${c.name} ${c.id} ${c.gender} tier${c.tier}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    classesGrid.innerHTML = filtered.map(c => {
      const isAct = currentModel === c.id;
      const genderBadge = c.gender === "MALE" ? `<span class="badge badge-male">♂ MASCULINO</span>` : `<span class="badge badge-female">♀ FEMININO</span>`;
      let tierBadge = `<span class="badge badge-tier1">TIER 1</span>`;
      if (c.tier === 2) tierBadge = `<span class="badge badge-tier2">⚡ TIER 2 (11 AÇÕES)</span>`;
      else if (c.tier === "costume") tierBadge = `<span class="badge badge-costume">👑 COSTUME</span>`;
      else if (c.tier === "mount") tierBadge = `<span class="badge badge-mount">🐎 MONTARIA</span>`;

      const actsText = c.actions && c.actions.includes(10) ? "⚡ 11 Ações (com Suprema 32f)" : `${c.actions ? c.actions.length : 8} Ações`;
      const thumbUrl = c.thumb || `assets/characters/${c.id}/thumb.webp`;

      return `
        <div class="asset-card ${isAct ? 'active-item' : ''}" data-class-id="${c.id}">
          <div class="asset-card-inner">
            <div class="asset-thumb-wrapper">
              <img src="${thumbUrl}" alt="${c.name}" class="asset-thumb" loading="lazy" />
            </div>
            <div class="asset-details">
              <div class="card-top-row">
                <h4 class="card-title">${c.name}</h4>
              </div>
              <div class="card-badges">
                ${genderBadge}
                ${tierBadge}
              </div>
              <div class="card-meta-text">
                <span><strong>ID:</strong> ${c.id}</span>
                <span><strong>Ações:</strong> ${actsText}</span>
                <span><strong>Tamanho:</strong> ${c.width}x${c.height}px</span>
              </div>
            </div>
          </div>
          <button class="card-btn-action" data-equip-class="${c.id}">
            ${isAct ? '✓ EQUIPADO' : '🎮 EQUIPAR ESTA CLASSE'}
          </button>
        </div>
      `;
    }).join("");

    classesGrid.querySelectorAll("[data-equip-class]").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const cid = btn.dataset.equipClass;
        const targetMeta = classesList.find(x => x.id === cid);
        await setCharacterModel(cid, targetMeta);
        renderClassesGrid();
        if (modalClasses) modalClasses.classList.add("hidden");
      });
    });
  }

  // 2. GRID DE MONSTROS E PETS (543 Criaturas: 106 Pets + 437 Monstros)
  function renderMonstersGrid() {
    if (!monstersGrid) return;
    const q = (monstersSearchInput ? monstersSearchInput.value : "").trim().toLowerCase();

    const filtered = monstersList.filter(m => {
      if (selectedMonFilter === "pets" && !m.is_pet) return false;
      if (selectedMonFilter === "monsters" && m.is_pet) return false;
      if (selectedMonFilter === "named" && m.name.startsWith("Criatura #")) return false;
      if (selectedMonFilter === "boss" && (!m.db_id || parseInt(m.db_id) < 100)) return false;
      if (q) {
        const str = `${m.name} ${m.id} ${m.db_id || ''} ${m.res_code_num} ${m.is_pet ? 'pet' : ''}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    }).slice(0, 160);

    monstersGrid.innerHTML = filtered.map(m => {
      const isAct = currentMonsterId === m.id;
      const lvl = m.db_id ? (parseInt(m.db_id) % 85 + 5) : 5;
      const thumbUrl = m.thumb || `assets/monsters/${m.id}/thumb.webp`;
      const isPet = !!m.is_pet;
      const petBadge = isPet ? `<span class="badge badge-pet">🐾 PET ${m.catchable ? 'CAPTURÁVEL' : 'COMPANHEIRO'}</span>` : '';
      const typeBadge = isPet ? '' : `<span class="badge badge-tier1">NV. ${lvl}</span>`;
      const descSnippet = m.desc ? `<span class="card-desc" style="font-size:10px; color:#a3be8c; font-style:italic;">"${m.desc.slice(0, 55)}..."</span>` : '';

      return `
        <div class="asset-card ${isAct ? 'active-item' : ''}" data-mon-id="${m.id}">
          <div class="asset-card-inner">
            <div class="asset-thumb-wrapper mon-thumb-bg">
              <img src="${thumbUrl}" alt="${m.name}" class="asset-thumb" loading="lazy" />
            </div>
            <div class="asset-details">
              <div class="card-top-row">
                <h4 class="card-title">${isPet ? '🐾' : '👾'} ${m.name}</h4>
              </div>
              <div class="card-badges">
                ${petBadge}
                ${typeBadge}
                <span class="badge badge-mount">${m.actions ? m.actions.length : 8} AÇÕES</span>
              </div>
              <div class="card-meta-text">
                <span><strong>ID:</strong> ${m.id} ${m.db_id ? `(DB: ${m.db_id})` : ''}</span>
                <span><strong>ResCode:</strong> ${m.res_code_num}</span>
                ${descSnippet}
              </div>
            </div>
          </div>
          <button class="card-btn-action btn-mon" data-fight-mon="${m.id}">
            ${isAct ? '⚔️ SELECIONADO AGORA' : (isPet ? '🐾 TESTAR / BATALHAR COM PET' : '⚔️ ENFRENTAR NO MAPA')}
          </button>
        </div>
      `;
    }).join("");

    monstersGrid.querySelectorAll("[data-fight-mon]").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const mid = btn.dataset.fightMon;
        const targetMeta = monstersList.find(x => x.id === mid);
        await setMapMonster(mid, targetMeta);
        renderMonstersGrid();
        if (modalMonsters) modalMonsters.classList.add("hidden");
        openCombatTest();
      });
    });
  }

  // 3. GRID DE MONTARIAS (20 Montarias)
  function renderMountsGrid() {
    if (!mountsGrid) return;
    const q = (mountsSearchInput ? mountsSearchInput.value : "").trim().toLowerCase();

    const filtered = mountsList.filter(m => {
      if (selectedMountFilter === "classic" && (m.tier > 6)) return false;
      if (selectedMountFilter === "divine" && (m.tier <= 6)) return false;
      if (selectedMountFilter === "male" && m.type !== "male_mount") return false;
      if (selectedMountFilter === "female" && m.type === "male_mount") return false;
      if (q) {
        const str = `${m.name} ${m.id} ${m.type} tier${m.tier}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    });

    mountsGrid.innerHTML = filtered.map(m => {
      const isAct = currentModel === m.id;
      const isDivine = m.tier >= 7;
      const tierBadge = isDivine
        ? `<span class="badge badge-divine">🔥 GRAU ${m.tier} (DIVINA)</span>`
        : `<span class="badge badge-mount">🐎 GRAU ${m.tier} (CLÁSSICA)</span>`;

      return `
        <div class="asset-card ${isAct ? 'active-item' : ''}" data-mount-id="${m.id}">
          <div class="asset-card-inner">
            <div class="asset-thumb-wrapper mount-thumb-bg">
              <img src="${m.thumb}" alt="${m.name}" class="asset-thumb" loading="lazy" />
            </div>
            <div class="asset-details">
              <div class="card-top-row">
                <h4 class="card-title">🐎 ${m.name}</h4>
              </div>
              <div class="card-badges">
                ${tierBadge}
                <span class="badge ${m.type === 'male_mount' ? 'badge-male' : 'badge-female'}">${m.type === 'male_mount' ? '♂ MONTARIA M' : '♀ MONTARIA F'}</span>
              </div>
              <div class="card-meta-text">
                <span><strong>ID:</strong> ${m.id}</span>
                <span><strong>Animações:</strong> Parado & Galope Veloz</span>
              </div>
            </div>
          </div>
          <button class="card-btn-action btn-mount" data-ride-mount="${m.id}">
            ${isAct ? '✓ CAVALGANDO AGORA' : '🏇 MONTAR / CAVALGAR'}
          </button>
        </div>
      `;
    }).join("");

    mountsGrid.querySelectorAll("[data-ride-mount]").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const mid = btn.dataset.rideMount;
        const targetMeta = mountsList.find(x => x.id === mid);
        await setCharacterModel(mid, targetMeta);
        renderMountsGrid();
        if (modalMounts) modalMounts.classList.add("hidden");
        spawnCombatText(`🐎 Montando em ${targetMeta.name}!`, player.x, player.y - 65, 0x88c0d0);
      });
    });
  }

  // 4. GRID DE NPCS (365 NPCs com Spawner no Mapa)
  function renderNpcsGrid() {
    if (!npcsGrid) return;
    const q = (npcsSearchInput ? npcsSearchInput.value : "").trim().toLowerCase();

    const filtered = npcsList.filter(n => {
      const nameLower = n.name.toLowerCase();
      if (selectedNpcFilter === "shops" && !(nameLower.includes("tiệm") || nameLower.includes("tạp hóa") || nameLower.includes("bảo quản") || nameLower.includes("thương gia") || nameLower.includes("loja") || nameLower.includes("mercador"))) return false;
      if (selectedNpcFilter === "masters" && !(nameLower.includes("đạo sư") || nameLower.includes("khảo quan") || nameLower.includes("hiền triết") || nameLower.includes("mestre") || nameLower.includes("instrutor"))) return false;
      if (selectedNpcFilter === "guards" && !(nameLower.includes("hộ vệ") || nameLower.includes("cận vệ") || nameLower.includes("trưởng") || nameLower.includes("tướng") || nameLower.includes("quân") || nameLower.includes("guarda"))) return false;
      if (selectedNpcFilter === "academy" && !(nameLower.includes("sứ giả") || nameLower.includes("học viện") || nameLower.includes("thôn") || nameLower.includes("chuyên viên"))) return false;
      if (q) {
        const str = `${n.name} ${n.id} ${n.res_code_num}`.toLowerCase();
        if (!str.includes(q)) return false;
      }
      return true;
    }).slice(0, 150);

    npcsGrid.innerHTML = filtered.map(n => {
      return `
        <div class="asset-card" data-npc-id="${n.id}">
          <div class="asset-card-inner">
            <div class="asset-thumb-wrapper npc-thumb-bg">
              <img src="${n.thumb}" alt="${n.name}" class="asset-thumb" loading="lazy" />
            </div>
            <div class="asset-details">
              <div class="card-top-row">
                <h4 class="card-title">👥 ${n.name}</h4>
              </div>
              <div class="card-badges">
                <span class="badge badge-npc">NPC FUNCIONAL</span>
                <span class="badge badge-tier1">MAPA ${n.map_id || 1}</span>
              </div>
              <div class="card-meta-text">
                <span><strong>ID:</strong> ${n.id}</span>
                <span><strong>ResCode:</strong> ${n.res_code_num}</span>
                <span><strong>Ocorrências:</strong> ${n.db_entries_count || 1} no jogo</span>
              </div>
            </div>
          </div>
          <button class="card-btn-action btn-npc" data-spawn-npc="${n.id}">
            📍 SPAWNAR NO MAPA
          </button>
        </div>
      `;
    }).join("");

    npcsGrid.querySelectorAll("[data-spawn-npc]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const nid = btn.dataset.spawnNpc;
        const targetNpc = npcsList.find(x => x.id === nid);
        if (targetNpc) {
          spawnNPCAtPlayer(targetNpc);
          if (modalNpcs) modalNpcs.classList.add("hidden");
        }
      });
    });
  }

  // Spawner de NPC no mapa ao lado do jogador
  function spawnNPCAtPlayer(npc) {
    const spawnX = Math.round(player.x + 45);
    const spawnY = Math.round(player.y + 15);

    const npcGroup = new PIXI.Container();
    npcGroup.x = spawnX;
    npcGroup.y = spawnY;
    npcGroup.zIndex = Math.round(spawnY);

    const shadow = new PIXI.Graphics();
    shadow.beginFill(0x000000, 0.38);
    shadow.drawEllipse(0, 0, 16, 8);
    shadow.endFill();
    npcGroup.addChild(shadow);

    const thumbTexture = PIXI.Texture.from(npc.thumb);
    const sprite = new PIXI.Sprite(thumbTexture);
    sprite.anchor.set(0.5, 1.0);
    sprite.scale.set(0.70, 0.70);
    npcGroup.addChild(sprite);

    const text = new PIXI.Text(npc.name, {
      fontFamily: "system-ui, -apple-system, sans-serif",
      fontSize: 11,
      fontWeight: "bold",
      fill: "#ffeb3b",
      stroke: "#111625",
      strokeThickness: 3
    });
    text.anchor.set(0.5, 1.0);
    text.y = - Math.round(sprite.height * 0.70) - 4;
    npcGroup.addChild(text);

    npcGroup.eventMode = "static";
    npcGroup.cursor = "pointer";
    npcGroup.hitArea = new PIXI.Circle(0, -35, 40);
    npcGroup.on("pointertap", (e) => {
      e.stopPropagation();
      showNPCDialog({
        name: npc.name,
        dialog: `Olá aventureiro! Eu sou ${npc.name} (ID: ${npc.id}). Em breve estarei pronto para lhe conceder missões, forjar itens e ensinar novas magias!`
      });
    });

    entitiesContainer.addChild(npcGroup);
    entitiesContainer.sortChildren();
    spawnCombatText(`👥 NPC ${npc.name} Spawnado!`, spawnX, spawnY - 50, 0xebcb8b);
  }

  // Handlers de Abertura / Fechamento dos Modais
  function openClassesModal() {
    if (modalClasses) {
      modalClasses.classList.remove("hidden");
      renderClassesGrid();
    }
  }
  function closeClassesModal() {
    if (modalClasses) modalClasses.classList.add("hidden");
  }

  function openMonstersModal() {
    if (modalMonsters) {
      modalMonsters.classList.remove("hidden");
      renderMonstersGrid();
    }
  }
  function closeMonstersModal() {
    if (modalMonsters) modalMonsters.classList.add("hidden");
  }

  function openMountsModal() {
    if (modalMounts) {
      modalMounts.classList.remove("hidden");
      renderMountsGrid();
    }
  }
  function closeMountsModal() {
    if (modalMounts) modalMounts.classList.add("hidden");
  }

  function openNpcsModal() {
    if (modalNpcs) {
      modalNpcs.classList.remove("hidden");
      renderNpcsGrid();
    }
  }
  function closeNpcsModal() {
    if (modalNpcs) modalNpcs.classList.add("hidden");
  }

  // Top Nav Buttons (Classes, Pets/Monstros, Montarias, NPCs)
  const btnTopClasses = document.getElementById("btn-open-classes-modal");
  const btnTopMonsters = document.getElementById("btn-open-monsters-modal");
  const btnTopMounts = document.getElementById("btn-open-mounts-modal");
  const btnTopNpcs = document.getElementById("btn-open-npcs-modal");

  if (btnTopClasses) btnTopClasses.addEventListener("click", openClassesModal);
  if (btnTopMonsters) btnTopMonsters.addEventListener("click", openMonstersModal);
  if (btnTopMounts) btnTopMounts.addEventListener("click", openMountsModal);
  if (btnTopNpcs) btnTopNpcs.addEventListener("click", openNpcsModal);

  // Drawer Buttons
  const btnDrawerClasses = document.getElementById("btn-drawer-all-classes");
  const btnDrawerMonsters = document.getElementById("btn-drawer-all-monsters");
  const btnDrawerMounts = document.getElementById("btn-drawer-all-mounts");
  const btnDrawerNpcs = document.getElementById("btn-drawer-all-npcs");

  if (btnDrawerClasses) btnDrawerClasses.addEventListener("click", () => { closeDrawer(); openClassesModal(); });
  if (btnDrawerMonsters) btnDrawerMonsters.addEventListener("click", () => { closeDrawer(); openMonstersModal(); });
  if (btnDrawerMounts) btnDrawerMounts.addEventListener("click", () => { closeDrawer(); openMountsModal(); });
  if (btnDrawerNpcs) btnDrawerNpcs.addEventListener("click", () => { closeDrawer(); openNpcsModal(); });

  // Combat Switch Monster Button
  const btnCbSwitchMon = document.getElementById("btn-combat-switch-mon");
  if (btnCbSwitchMon) btnCbSwitchMon.addEventListener("click", openMonstersModal);

  // Modal Close Buttons
  const btnCloseClasses = document.getElementById("btn-close-classes-modal");
  const btnCloseMonsters = document.getElementById("btn-close-monsters-modal");
  const btnCloseMounts = document.getElementById("btn-close-mounts-modal");
  const btnCloseNpcs = document.getElementById("btn-close-npcs-modal");

  if (btnCloseClasses) btnCloseClasses.addEventListener("click", closeClassesModal);
  if (btnCloseMonsters) btnCloseMonsters.addEventListener("click", closeMonstersModal);
  if (btnCloseMounts) btnCloseMounts.addEventListener("click", closeMountsModal);
  if (btnCloseNpcs) btnCloseNpcs.addEventListener("click", closeNpcsModal);

  // Backdrop click to close
  [
    { modal: modalClasses, close: closeClassesModal },
    { modal: modalMonsters, close: closeMonstersModal },
    { modal: modalMounts, close: closeMountsModal },
    { modal: modalNpcs, close: closeNpcsModal }
  ].forEach(item => {
    if (item.modal) {
      item.modal.addEventListener("click", (e) => {
        if (e.target === item.modal) item.close();
      });
    }
  });

  // Search Inputs
  if (classesSearchInput) classesSearchInput.addEventListener("input", renderClassesGrid);
  if (monstersSearchInput) monstersSearchInput.addEventListener("input", renderMonstersGrid);
  if (mountsSearchInput) mountsSearchInput.addEventListener("input", renderMountsGrid);
  if (npcsSearchInput) npcsSearchInput.addEventListener("input", renderNpcsGrid);

  // Filter Pills: Classes
  document.querySelectorAll("#classes-filter-pills .pill-filter").forEach(p => {
    p.addEventListener("click", () => {
      document.querySelectorAll("#classes-filter-pills .pill-filter").forEach(b => b.classList.remove("active"));
      p.classList.add("active");
      selectedClassFilter = p.dataset.filter;
      renderClassesGrid();
    });
  });

  // Filter Pills: Monsters & Pets
  document.querySelectorAll("#monsters-filter-pills .pill-filter").forEach(p => {
    p.addEventListener("click", () => {
      document.querySelectorAll("#monsters-filter-pills .pill-filter").forEach(b => b.classList.remove("active"));
      p.classList.add("active");
      selectedMonFilter = p.dataset.filter;
      renderMonstersGrid();
    });
  });

  // Filter Pills: Mounts
  document.querySelectorAll("#mounts-filter-pills .pill-filter").forEach(p => {
    p.addEventListener("click", () => {
      document.querySelectorAll("#mounts-filter-pills .pill-filter").forEach(b => b.classList.remove("active"));
      p.classList.add("active");
      selectedMountFilter = p.dataset.filter;
      renderMountsGrid();
    });
  });

  // Filter Pills: NPCs
  document.querySelectorAll("#npcs-filter-pills .pill-filter").forEach(p => {
    p.addEventListener("click", () => {
      document.querySelectorAll("#npcs-filter-pills .pill-filter").forEach(b => b.classList.remove("active"));
      p.classList.add("active");
      selectedNpcFilter = p.dataset.filter;
      renderNpcsGrid();
    });
  });

  // Drawer Quick Monster Buttons
  document.querySelectorAll(".mon-quick-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
      const mid = btn.dataset.monster;
      await setMapMonster(mid);
    });
  });
'''

with open('web/main.js', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = "  // ==========================================\n  // MODAIS DE CATALOGO (CLASSES & MONSTROS)\n  // =========================================="
end_marker = "  // Expor para debug e inspeção"

idx1 = text.find(start_marker)
idx2 = text.find(end_marker)

if idx1 == -1 or idx2 == -1:
    print("Error: could not find markers in web/main.js")
    sys.exit(1)

updated_text = text[:idx1] + new_code + "\n" + text[idx2:]
with open('web/main.js', 'w', encoding='utf-8') as f:
    f.write(updated_text)

print("web/main.js successfully updated!")
