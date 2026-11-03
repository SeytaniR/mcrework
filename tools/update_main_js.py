import re

with open('C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/main.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update Promise.all to fetch maps catalog
old_promise = """  const [npcsData, masksData, colArrayBuffer, initialMonsterMeta, initialMonsterSheet, classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] }))
  ]);"""

new_promise = """  const [npcsData, masksData, colArrayBuffer, initialMonsterMeta, initialMonsterSheet, classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.3.0").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.3.0").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.3.0").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.3.0").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.3.0").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] }))
  ]);

  let mapsCatalog = mapsCatalogData || { total_maps: 0, maps: [] };
  let currentMapId = 1;
  let currentMapMeta = mapsCatalog.maps ? mapsCatalog.maps.find(m => m.id === 1) : null;
  let currentMapPortals = currentMapMeta ? (currentMapMeta.portals || []) : [];
  let teleportCooldown = 0;
  let portalPulseTimer = 0;"""

assert old_promise in code, "old_promise not found!"
code = code.replace(old_promise, new_promise)

# 2. Update collision variables and isWalkable
old_col = """  // 3. Malha de Colisão Binária (Uint8Array de 388.683 bytes, 2031x1531)
  const colBytes = new Uint8Array(colArrayBuffer);
  const COL_WIDTH = 2031;
  const COL_HEIGHT = 1531;
  console.log(`Malha de colisão binária carregada: ${colBytes.length} bytes (${COL_WIDTH}x${COL_HEIGHT})`);

  function isWalkable(x, y) {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    if (ix < 0 || ix >= COL_WIDTH || iy < 0 || iy >= COL_HEIGHT) return false;
    const idx = iy * COL_WIDTH + ix;
    return (colBytes[idx >> 3] & (1 << (idx & 7))) !== 0;
  }"""

new_col = """  // 3. Malha de Colisão Binária (Uint8Array de 388.683 bytes, 2031x1531)
  let colBytes = new Uint8Array(colArrayBuffer);
  let COL_WIDTH = 2031;
  let COL_HEIGHT = 1531;
  let MAP_WIDTH = 2000;
  let MAP_HEIGHT = 1500;
  console.log(`Malha de colisão binária carregada: ${colBytes.length} bytes (${COL_WIDTH}x${COL_HEIGHT})`);

  function isWalkable(x, y) {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    if (ix < 0 || ix >= MAP_WIDTH || iy < 0 || iy >= MAP_HEIGHT) return false;
    if (!colBytes || COL_WIDTH <= 0 || COL_HEIGHT <= 0) return true;
    if (ix >= COL_WIDTH || iy >= COL_HEIGHT) return false;
    const idx = iy * COL_WIDTH + ix;
    return (colBytes[idx >> 3] & (1 << (idx & 7))) !== 0;
  }"""

assert old_col in code, "old_col not found!"
code = code.replace(old_col, new_col)

# 3. Replace const MAP_WIDTH with portalsContainer
old_map = """  // Camada 1: Terreno / Mapa Base
  const mapTexture = await PIXI.Assets.load("assets/map1/map1.jpg");
  const mapSprite = new PIXI.Sprite(mapTexture);
  mapSprite.eventMode = "static";
  world.addChild(mapSprite);

  const MAP_WIDTH = 2000;
  const MAP_HEIGHT = 1500;"""

new_map = """  // Camada 1: Terreno / Mapa Base
  const mapTexture = await PIXI.Assets.load("assets/map1/map1.jpg");
  const mapSprite = new PIXI.Sprite(mapTexture);
  mapSprite.eventMode = "static";
  world.addChild(mapSprite);

  // Camada 1.5: Portais de Interligação de Mapas
  const portalsContainer = new PIXI.Container();
  world.addChild(portalsContainer);"""

assert old_map in code, "old_map not found!"
code = code.replace(old_map, new_map)

# 4. Insert renderMapPortals, showMapToast, switchMap
portal_helpers = """
  // ==========================================================================
  // SISTEMA DE PORTAIS, TELEPORTE & TROCA DE MAPAS (76 MAPAS)
  // ==========================================================================

  let toastTimeout = null;
  function showMapToast(text) {
    let toast = document.getElementById("map-toast-notification");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "map-toast-notification";
      document.body.appendChild(toast);
    }
    toast.textContent = text;
    toast.style.display = "flex";
    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      if (toast) toast.style.display = "none";
    }, 2800);
  }

  function renderMapPortals(portals) {
    portalsContainer.removeChildren();
    if (!portals || portals.length === 0) return;

    portals.forEach(portal => {
      const portalGroup = new PIXI.Container();
      portalGroup.x = portal.x;
      portalGroup.y = portal.y;
      portalGroup.eventMode = "static";
      portalGroup.cursor = "pointer";

      // Base glowing aura
      const glow = new PIXI.Graphics();
      glow.name = "glow";
      glow.beginFill(0x00e5ff, 0.28);
      glow.drawEllipse(0, 0, 36, 18);
      glow.endFill();
      portalGroup.addChild(glow);

      // Outer rotating rune ring
      const outerRing = new PIXI.Graphics();
      outerRing.name = "outerRing";
      outerRing.lineStyle(2.5, 0x00e5ff, 0.9);
      outerRing.drawEllipse(0, 0, 30, 15);
      outerRing.lineStyle(2, 0xffffff, 0.95);
      outerRing.moveTo(0, -15); outerRing.lineTo(0, -19);
      outerRing.moveTo(0, 15); outerRing.lineTo(0, 19);
      outerRing.moveTo(-30, 0); outerRing.lineTo(-36, 0);
      outerRing.moveTo(30, 0); outerRing.lineTo(36, 0);
      portalGroup.addChild(outerRing);

      // Inner bright luminous core
      const innerCore = new PIXI.Graphics();
      innerCore.name = "innerCore";
      innerCore.beginFill(0x80deea, 0.45);
      innerCore.drawEllipse(0, 0, 16, 8);
      innerCore.endFill();
      portalGroup.addChild(innerCore);

      // Floating text label
      const labelContainer = new PIXI.Container();
      labelContainer.y = -32;

      const labelBg = new PIXI.Graphics();
      const portalTitle = `🌀 ${portal.target_name} (#${portal.target_map_id})`;
      const labelText = new PIXI.Text(portalTitle, {
        fontFamily: "system-ui, -apple-system, sans-serif",
        fontSize: 10.5,
        fontWeight: "bold",
        fill: "#00e5ff",
        stroke: "#0b121e",
        strokeThickness: 3,
        align: "center"
      });
      labelText.anchor.set(0.5, 0.5);

      const padX = 8;
      const padY = 3;
      const w = labelText.width + padX * 2;
      const h = labelText.height + padY * 2;

      labelBg.beginFill(0x0a101d, 0.88);
      labelBg.lineStyle(1.2, 0x00e5ff, 0.7);
      labelBg.drawRoundedRect(-w / 2, -h / 2, w, h, 6);
      labelBg.endFill();

      labelContainer.addChild(labelBg);
      labelContainer.addChild(labelText);
      portalGroup.addChild(labelContainer);

      portalGroup.on("pointerdown", (e) => {
        e.stopPropagation();
        const dist = Math.hypot(player.x - portal.x, player.y - portal.y);
        if (dist <= 60 && teleportCooldown <= 0) {
          teleportCooldown = 2.5;
          switchMap(portal.target_map_id, portal.dest_x, portal.dest_y);
        } else {
          movePlayerTo(portal.x, portal.y);
        }
      });

      portalsContainer.addChild(portalGroup);
    });
  }

  // Renderizar portais iniciais do Mapa 1
  renderMapPortals(currentMapPortals);

  async function switchMap(targetMapId, spawnX, spawnY) {
    const mapMeta = mapsCatalog.maps.find(m => m.id === targetMapId);
    if (!mapMeta) {
      console.warn(`Mapa ID ${targetMapId} não encontrado no catálogo.`);
      return;
    }

    showMapToast(`🌀 Viajando para ${mapMeta.name} (#${mapMeta.id})...`);

    try {
      // 1. Carregar textura do novo mapa
      const newTexture = await PIXI.Assets.load(mapMeta.bg_image);
      mapSprite.texture = newTexture;
      mapSprite.width = mapMeta.width;
      mapSprite.height = mapMeta.height;

      // 2. Atualizar limites de dimensões
      MAP_WIDTH = mapMeta.width;
      MAP_HEIGHT = mapMeta.height;

      // 3. Carregar malha de colisão binária se existir
      if (mapMeta.has_collision && mapMeta.collision_bin) {
        try {
          const colBuf = await fetch(mapMeta.collision_bin).then(r => r.arrayBuffer());
          colBytes = new Uint8Array(colBuf);
          COL_WIDTH = mapMeta.col_width;
          COL_HEIGHT = mapMeta.col_height;
        } catch (e) {
          console.warn("Erro ao carregar colisão binária do mapa:", e);
        }
      } else {
        COL_WIDTH = 0;
        COL_HEIGHT = 0;
      }

      currentMapId = targetMapId;
      currentMapMeta = mapMeta;
      currentMapPortals = mapMeta.portals || [];

      // 4. Posicionar jogador nas coordenadas seguras
      const targetX = (spawnX !== undefined && spawnX !== null) ? spawnX : (mapMeta.safe_x || Math.round(MAP_WIDTH / 2));
      const targetY = (spawnY !== undefined && spawnY !== null) ? spawnY : (mapMeta.safe_y || Math.round(MAP_HEIGHT / 2));
      const safePos = findClosestWalkable(targetX, targetY, 120) || { x: targetX, y: targetY };

      player.x = safePos.x;
      player.y = safePos.y;
      player.targetX = null;
      player.targetY = null;
      if (playerContainer) {
        playerContainer.x = player.x;
        playerContainer.y = player.y;
        playerContainer.zIndex = Math.round(player.y);
      }
      if (targetMarker) targetMarker.visible = false;

      // 5. Renderizar portais deste mapa
      renderMapPortals(currentMapPortals);

      // 6. Atualizar HUD de Mapa
      const mapNameEl = document.querySelector(".map-name");
      if (mapNameEl) mapNameEl.textContent = `${mapMeta.name} (#${mapMeta.id})`;

      const worldCurrentLocEl = document.getElementById("worldmap-current-loc");
      if (worldCurrentLocEl) worldCurrentLocEl.textContent = `${mapMeta.name} (#${mapMeta.id})`;

      // 7. Visibilidade de elementos específicos do Mapa 1
      const isMap1 = (targetMapId === 1);
      if (maskSprites) {
        maskSprites.forEach(m => { if (m.sprite) m.sprite.visible = isMap1; });
      }
      if (npcList) {
        npcList.forEach(n => { n.visible = isMap1; });
      }
      if (mapMonsterGroup) {
        mapMonsterGroup.visible = isMap1;
      }

      // 8. Atualizar câmera imediatamente
      updateCamera();

      // 9. Feedback de chegada
      showMapToast(`📍 Chegou em: ${mapMeta.name} (#${mapMeta.id})`);
      spawnCombatText(`📍 ${mapMeta.name}`, player.x, player.y - 65, 0xa3be8c);

      // 10. Atualizar pin ativo no mapa mundi caso esteja aberto
      updateActiveWorldMapPin();

    } catch (err) {
      console.error(`Erro ao trocar para o mapa ${targetMapId}:`, err);
      showMapToast(`❌ Erro ao carregar mapa #${targetMapId}`);
    }
  }
"""

marker_target = """  // Camada 3: Marcador de Destino (Tap-to-move)"""
assert marker_target in code, "marker_target not found!"
code = code.replace(marker_target, portal_helpers + "\n  " + marker_target)

# 5. In ticker loop: add portal animation and contact check
ticker_target = """    // 4. Transparência Dinâmica dos Telhados e Árvores (Máscaras de Sobreposição)"""
ticker_addition = """    // 3.8 Animação e Detecção de Portais de Teleporte
    if (portalsContainer && portalsContainer.children.length > 0) {
      portalPulseTimer += deltaSeconds * 3;
      portalsContainer.children.forEach(pg => {
        const glow = pg.getChildByName("glow");
        const outerRing = pg.getChildByName("outerRing");
        const innerCore = pg.getChildByName("innerCore");
        if (glow) glow.alpha = 0.22 + Math.sin(portalPulseTimer) * 0.14;
        if (outerRing) outerRing.scale.set(1.0 + Math.sin(portalPulseTimer * 1.5) * 0.05);
        if (innerCore) innerCore.alpha = 0.35 + Math.cos(portalPulseTimer * 2) * 0.18;
      });
    }

    if (teleportCooldown > 0) {
      teleportCooldown -= deltaSeconds;
    } else if (currentMapPortals && currentMapPortals.length > 0 && !isCombatTesting) {
      for (const portal of currentMapPortals) {
        const dist = Math.hypot(player.x - portal.x, player.y - portal.y);
        if (dist <= 48) {
          teleportCooldown = 2.5;
          switchMap(portal.target_map_id, portal.dest_x, portal.dest_y);
          break;
        }
      }
    }

"""
assert ticker_target in code, "ticker_target not found!"
code = code.replace(ticker_target, ticker_addition + ticker_target)

# 6. Add World Map Modal logic and wiring before window.game
worldmap_controller = """
  // ==========================================================================
  // CONTROLLER DO MAPA GERAL DO MUNDO & BUSCA DE MAPAS (76 MAPAS)
  // ==========================================================================

  const modalWorldmap = document.getElementById("modal-worldmap");
  const btnOpenWorldmap = document.getElementById("btn-open-worldmap-modal");
  const btnCloseWorldmap = document.getElementById("btn-close-worldmap-modal");
  const btnDrawerWorldmap = document.getElementById("btn-drawer-worldmap");

  const worldmapBgImg = document.getElementById("worldmap-bg-img");
  const worldmapPinsLayer = document.getElementById("worldmap-pins-layer");
  const worldmapInteractiveView = document.getElementById("worldmap-interactive-view");
  const worldmapListView = document.getElementById("worldmap-list-view");

  const pinCard = document.getElementById("worldmap-pin-card");
  const btnClosePinCard = document.getElementById("btn-close-pin-card");
  const btnTeleportPin = document.getElementById("btn-teleport-pin");

  const mapsSearchInput = document.getElementById("maps-search-input");
  const mapsGridContainer = document.getElementById("maps-grid-container");

  let currentWorldmapTab = "continent-1";
  let selectedPinMap = null;
  let selectedMapFilter = "all";

  function openWorldMapModal() {
    if (modalWorldmap) {
      modalWorldmap.classList.remove("hidden");
      switchWorldmapTab(currentWorldmapTab);
    }
  }

  function closeWorldMapModal() {
    if (modalWorldmap) modalWorldmap.classList.add("hidden");
    if (pinCard) pinCard.classList.add("hidden");
  }

  function switchWorldmapTab(tabKey) {
    currentWorldmapTab = tabKey;

    document.querySelectorAll(".worldmap-tab-btn").forEach(btn => {
      btn.classList.toggle("active", btn.dataset.tab === tabKey);
    });

    if (tabKey === "continent-1") {
      worldmapInteractiveView.classList.remove("hidden");
      worldmapListView.classList.add("hidden");
      worldmapBgImg.src = "assets/worldmap/world_map_1.jpg";
      renderWorldMapPins(1);
    } else if (tabKey === "continent-2") {
      worldmapInteractiveView.classList.remove("hidden");
      worldmapListView.classList.add("hidden");
      worldmapBgImg.src = "assets/worldmap/world_map_2.jpg";
      renderWorldMapPins(2);
    } else if (tabKey === "list") {
      worldmapInteractiveView.classList.add("hidden");
      worldmapListView.classList.remove("hidden");
      renderMapsGrid();
    }
  }

  function renderWorldMapPins(continentId) {
    worldmapPinsLayer.innerHTML = "";
    if (pinCard) pinCard.classList.add("hidden");
    if (!mapsCatalog || !mapsCatalog.maps) return;

    const pinnedMaps = mapsCatalog.maps.filter(m => m.continent === continentId && m.world_x !== null && m.world_y !== null);

    pinnedMaps.forEach(m => {
      const pin = document.createElement("div");
      pin.className = "worldmap-pin";
      if (m.name.includes("Thành") || m.name.includes("Thôn")) pin.classList.add("is-town");
      if (m.id === currentMapId) pin.classList.add("is-current-location");

      pin.style.left = `${m.world_x}px`;
      pin.style.top = `${m.world_y}px`;
      pin.dataset.mapId = m.id;

      pin.innerHTML = `
        ${m.id === currentMapId ? '<div class="radar-ring"></div>' : ''}
        <div class="pin-icon">${m.name.includes("Thành") ? '🏰' : (m.name.includes("Thôn") ? '🏡' : '📍')}</div>
        <div class="pin-needle"></div>
        <div class="pin-label-pill">${m.name}</div>
      `;

      pin.addEventListener("click", (e) => {
        e.stopPropagation();
        showPinCard(m);
      });

      worldmapPinsLayer.appendChild(pin);
    });
  }

  function updateActiveWorldMapPin() {
    document.querySelectorAll(".worldmap-pin").forEach(pin => {
      const mid = parseInt(pin.dataset.mapId, 10);
      const isCur = (mid === currentMapId);
      pin.classList.toggle("is-current-location", isCur);
      const existingRadar = pin.querySelector(".radar-ring");
      if (isCur && !existingRadar) {
        const ring = document.createElement("div");
        ring.className = "radar-ring";
        pin.prepend(ring);
      } else if (!isCur && existingRadar) {
        existingRadar.remove();
      }
    });
  }

  function showPinCard(mapObj) {
    selectedPinMap = mapObj;
    if (!pinCard) return;
    pinCard.classList.remove("hidden");

    const imgEl = document.getElementById("pin-card-img");
    if (imgEl) imgEl.src = mapObj.thumb || `assets/maps/map_${mapObj.id}/thumb.webp`;

    const lvlEl = document.getElementById("pin-card-level-badge");
    if (lvlEl) lvlEl.textContent = `Lv. ${mapObj.level || 1}+`;

    const nameEl = document.getElementById("pin-card-name");
    if (nameEl) nameEl.textContent = mapObj.name;

    const idEl = document.getElementById("pin-card-id");
    if (idEl) idEl.textContent = `#${mapObj.id}`;

    const descEl = document.getElementById("pin-card-desc");
    if (descEl) descEl.textContent = mapObj.info || "Área explorável do mundo de Magic Campus.";

    const sizeEl = document.getElementById("pin-card-size");
    if (sizeEl) sizeEl.textContent = `📏 ${mapObj.width} x ${mapObj.height}`;

    const portalsEl = document.getElementById("pin-card-portals");
    if (portalsEl) portalsEl.textContent = `🌀 ${mapObj.portals ? mapObj.portals.length : 0} Portais`;

    const portalsListEl = document.getElementById("pin-card-portals-list");
    if (portalsListEl) {
      if (mapObj.portals && mapObj.portals.length > 0) {
        portalsListEl.innerHTML = mapObj.portals.map(p => `
          <span class="portal-link-pill">➔ ${p.target_name} (#${p.target_map_id})</span>
        `).join("");
      } else {
        portalsListEl.innerHTML = '<span class="portal-link-pill" style="opacity:0.6;">Sem portais diretos</span>';
      }
    }
  }

  function renderMapsGrid() {
    if (!mapsCatalog || !mapsCatalog.maps || !mapsGridContainer) return;

    const query = (mapsSearchInput ? mapsSearchInput.value : "").trim().toLowerCase();
    const filtered = mapsCatalog.maps.filter(m => {
      if (selectedMapFilter === "cont1" && m.continent !== 1) return false;
      if (selectedMapFilter === "cont2" && m.continent !== 2) return false;
      if (selectedMapFilter === "town" && !m.name.includes("Thành") && !m.name.includes("Thôn")) return false;
      if (selectedMapFilter === "dungeon" && (m.name.includes("Thành") || m.name.includes("Thôn"))) return false;

      if (query) {
        const matchName = m.name.toLowerCase().includes(query);
        const matchId = String(m.id) === query || String(m.id).includes(query);
        const matchInfo = (m.info || "").toLowerCase().includes(query);
        if (!matchName && !matchId && !matchInfo) return false;
      }
      return true;
    });

    mapsGridContainer.innerHTML = filtered.map(m => {
      const isCur = (m.id === currentMapId);
      const contName = (m.continent === 1) ? "🌐 Vô Ưu" : "✨ Thần Thánh";
      return `
        <div class="asset-card ${isCur ? 'active' : ''}">
          <div class="asset-card-inner">
            <div class="asset-thumb-wrapper" style="width: 80px; height: 60px; min-width: 80px;">
              <img class="asset-thumb" src="${m.thumb}" alt="${m.name}" loading="lazy" />
            </div>
            <div class="asset-details">
              <div class="asset-card-header">
                <span class="asset-title">${m.name}</span>
                <span class="asset-id">#${m.id}</span>
              </div>
              <div class="asset-meta-row">
                <span class="asset-tag">${contName}</span>
                <span class="asset-tag">Lv. ${m.level}+</span>
                <span class="asset-tag">🌀 ${m.portals ? m.portals.length : 0}p</span>
              </div>
              <button class="card-btn-action btn-map-tp" data-tp-map="${m.id}">
                ${isCur ? '📍 AQUI AGORA' : '🚀 TELEPORTAR'}
              </button>
            </div>
          </div>
        </div>
      `;
    }).join("");

    mapsGridContainer.querySelectorAll("[data-tp-map]").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const mid = parseInt(btn.dataset.tpMap, 10);
        closeWorldMapModal();
        switchMap(mid);
      });
    });
  }

  // Event Listeners: World Map
  if (btnOpenWorldmap) btnOpenWorldmap.addEventListener("click", openWorldMapModal);
  if (btnCloseWorldmap) btnCloseWorldmap.addEventListener("click", closeWorldMapModal);
  if (btnDrawerWorldmap) btnDrawerWorldmap.addEventListener("click", () => { closeDrawer(); openWorldMapModal(); });

  const gameBadgeEl = document.querySelector(".game-badge");
  if (gameBadgeEl) {
    gameBadgeEl.style.cursor = "pointer";
    gameBadgeEl.title = "Clique para abrir o Mapa Geral do Mundo";
    gameBadgeEl.addEventListener("click", openWorldMapModal);
  }

  if (btnClosePinCard) btnClosePinCard.addEventListener("click", () => {
    if (pinCard) pinCard.classList.add("hidden");
  });

  if (btnTeleportPin) btnTeleportPin.addEventListener("click", () => {
    if (selectedPinMap) {
      closeWorldMapModal();
      switchMap(selectedPinMap.id, selectedPinMap.safe_x, selectedPinMap.safe_y);
    }
  });

  document.querySelectorAll(".worldmap-tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      switchWorldmapTab(btn.dataset.tab);
    });
  });

  if (mapsSearchInput) mapsSearchInput.addEventListener("input", renderMapsGrid);

  document.querySelectorAll("#maps-filter-pills .pill-filter").forEach(p => {
    p.addEventListener("click", () => {
      document.querySelectorAll("#maps-filter-pills .pill-filter").forEach(b => b.classList.remove("active"));
      p.classList.add("active");
      selectedMapFilter = p.dataset.filter;
      renderMapsGrid();
    });
  });

  if (modalWorldmap) {
    modalWorldmap.addEventListener("click", (e) => {
      if (e.target === modalWorldmap) closeWorldMapModal();
    });
  }
"""

window_game_target = """  // Expor para debug e inspeção
  window.game = {"""

assert window_game_target in code, "window_game_target not found!"
code = code.replace(window_game_target, worldmap_controller + "\n" + window_game_target)

# Add switchMap, mapsCatalog, openWorldMapModal to window.game
game_exp_target = """  window.game = {
    setMapMonster,"""
game_exp_new = """  window.game = {
    switchMap,
    openWorldMapModal,
    mapsCatalog,
    currentMapId: () => currentMapId,
    setMapMonster,"""
assert game_exp_target in code, "game_exp_target not found!"
code = code.replace(game_exp_target, game_exp_new)

with open('C:/Users/Dell/.gemini/antigravity/scratch/magic-campus-pixi/web/main.js', 'w', encoding='utf-8') as f:
    f.write(code)

print('web/main.js updated successfully!')
