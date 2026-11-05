// Magic Campus - Pixi.js Mobile Engine (Mapa 1 & Char 1)
// Arquitetura moderna de renderização 2.5D com preservação de pivô, colisão e transparência

async function initGame() {
  const container = document.getElementById("game-container");

  // 1. Inicializar PixiJS Application
  const app = new PIXI.Application({
    resizeTo: window,
    backgroundColor: 0x0f1117,
    antialias: true,
    resolution: Math.min(window.devicePixelRatio || 1, 2),
    autoDensity: true
  });
  container.appendChild(app.view);

  // 2. Carregar Metadados do Mapa, Monstro e Catálogos (Spritesheets WebP)
  const [
    npcsData, masksData, colArrayBuffer, initialMonsterMeta, initialMonsterSheet,
    classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData, mapsCatalogData,
    skillsCatalogData, effectsCatalogData, equipmentCatalogData, wingsCatalogData
  ] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] })),
    fetch("assets/maps/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ({ total_maps: 0, maps: [] })),
    fetch("assets/skills/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ([])),
    fetch("assets/effects/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ([])),
    fetch("assets/equipment/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ({ items: [] })),
    fetch("assets/wings/catalog.json?v=1.6.0").then(r => r.json()).catch(() => ([]))
  ]);

  let mapsCatalog = mapsCatalogData || { total_maps: 0, maps: [] };
  let currentMapId = 1;
  let currentMapMeta = mapsCatalog.maps ? mapsCatalog.maps.find(m => m.id === 1) : null;
  let currentMapPortals = currentMapMeta ? (currentMapMeta.portals || []) : [];
  let teleportCooldown = 0;
  let portalPulseTimer = 0;

  let monsterMeta = initialMonsterMeta;
  let monsterSheet = initialMonsterSheet;
  let currentMonsterId = "mushroom";
  let currentSpritesheet = null;
  let currentMeta = null;

  // 3. Malha de Colisão Binária Calibrada
  let colBytes = new Uint8Array(colArrayBuffer);
  let COL_WIDTH = (currentMapMeta && currentMapMeta.col_width) ? currentMapMeta.col_width : 2031;
  let COL_HEIGHT = (currentMapMeta && currentMapMeta.col_height) ? currentMapMeta.col_height : 1530;
  let MAP_WIDTH = (currentMapMeta && currentMapMeta.width) ? currentMapMeta.width : 2000;
  let MAP_HEIGHT = (currentMapMeta && currentMapMeta.height) ? currentMapMeta.height : 1500;
  console.log(`Malha de colisão binária inicial carregada: ${colBytes.length} bytes (stride ${COL_WIDTH}x${COL_HEIGHT})`);

  function isWalkable(x, y) {
    const ix = Math.floor(x);
    const iy = Math.floor(y);
    if (ix < 0 || ix >= MAP_WIDTH || iy < 0 || iy >= MAP_HEIGHT) return false;
    if (!colBytes || COL_WIDTH <= 0 || COL_HEIGHT <= 0) return true;
    if (ix >= COL_WIDTH || iy >= COL_HEIGHT) return false;
    const idx = iy * COL_WIDTH + ix;
    const byteIdx = idx >> 3;
    if (byteIdx >= colBytes.length) return false;
    return (colBytes[byteIdx] & (1 << (idx & 7))) !== 0;
  }

  function canStand(x, y) {
    if (!isWalkable(x, y)) return false;
    // Pequeno footprint de 2px para máxima fluidez em caminhos e pontes estreitas
    if (!isWalkable(x - 2, y) || !isWalkable(x + 2, y)) return false;
    if (!isWalkable(x, y - 2) || !isWalkable(x, y + 2)) return false;
    return true;
  }

  function findClosestWalkable(tx, ty, maxRadius = 150) {
    if (canStand(tx, ty)) return { x: tx, y: ty };
    if (isWalkable(tx, ty)) return { x: tx, y: ty };
    for (let r = 2; r <= maxRadius; r += 2) {
      for (let ang = 0; ang < Math.PI * 2; ang += Math.PI / 8) {
        const testX = Math.round(tx + Math.cos(ang) * r);
        const testY = Math.round(ty + Math.sin(ang) * r);
        if (canStand(testX, testY)) {
          return { x: testX, y: testY };
        }
      }
    }
    return null;
  }

  // 4. Containers de Camadas no Mundo 2.5D
  const world = new PIXI.Container();
  app.stage.addChild(world);

  // Camada 1: Terreno / Mapa Base
  const mapTexture = await PIXI.Assets.load("assets/map1/map1.jpg");
  const mapSprite = new PIXI.Sprite(mapTexture);
  mapSprite.eventMode = "static";
  world.addChild(mapSprite);

  // Camada 1.5: Portais de Interligação de Mapas
  const portalsContainer = new PIXI.Container();
  world.addChild(portalsContainer);

  // Camada 2: Overlay Visual da Colisão (Inspecionável / Debug)
  const colOverlayTexture = await PIXI.Assets.load("assets/map1/collision_overlay.png");
  const colOverlaySprite = new PIXI.Sprite(colOverlayTexture);
  colOverlaySprite.visible = false;
  world.addChild(colOverlaySprite);


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

      // 1. Base glowing aura (suave elipse luminosa no solo)
      const glow = new PIXI.Graphics();
      glow.name = "glow";
      glow.beginFill(0x00e5ff, 0.32);
      glow.drawEllipse(0, 0, 42, 22);
      glow.endFill();
      portalGroup.addChild(glow);

      // 2. Anel Rúnico Externo com marcas cardeais luminosas
      const outerRing = new PIXI.Graphics();
      outerRing.name = "outerRing";
      outerRing.lineStyle(2.5, 0x00e5ff, 0.92);
      outerRing.drawEllipse(0, 0, 34, 17);
      outerRing.lineStyle(2, 0xffffff, 0.95);
      outerRing.moveTo(0, -17); outerRing.lineTo(0, -23);
      outerRing.moveTo(0, 17); outerRing.lineTo(0, 23);
      outerRing.moveTo(-34, 0); outerRing.lineTo(-40, 0);
      outerRing.moveTo(34, 0); outerRing.lineTo(40, 0);
      portalGroup.addChild(outerRing);

      // 3. Anel Rúnico Interno giratório dourado/ciano
      const innerRing = new PIXI.Graphics();
      innerRing.name = "innerRing";
      innerRing.lineStyle(1.8, 0x80deea, 0.85);
      innerRing.drawEllipse(0, 0, 22, 11);
      innerRing.lineStyle(1.5, 0xffd54f, 0.9);
      innerRing.moveTo(-16, -8); innerRing.lineTo(-12, -6);
      innerRing.moveTo(16, 8); innerRing.lineTo(12, 6);
      portalGroup.addChild(innerRing);

      // 4. Vórtice de luz central pulsante
      const innerCore = new PIXI.Graphics();
      innerCore.name = "innerCore";
      innerCore.beginFill(0x00ffff, 0.55);
      innerCore.drawEllipse(0, 0, 14, 7);
      innerCore.endFill();
      portalGroup.addChild(innerCore);

      // 5. Placa de Destino com Subtítulo Interativo
      const labelContainer = new PIXI.Container();
      labelContainer.name = "labelContainer";
      labelContainer.y = -36;

      const labelBg = new PIXI.Graphics();
      const portalTitle = `🌀 ${portal.target_name} (#${portal.target_map_id})`;
      const labelText = new PIXI.Text(portalTitle, {
        fontFamily: "system-ui, -apple-system, sans-serif",
        fontSize: 10.5,
        fontWeight: "bold",
        fill: "#00e5ff",
        stroke: "#0b121e",
        strokeThickness: 3.5,
        align: "center"
      });
      labelText.anchor.set(0.5, 0.5);

      const subText = new PIXI.Text("👉 Toque para viajar", {
        fontFamily: "system-ui, -apple-system, sans-serif",
        fontSize: 8.5,
        fontWeight: "600",
        fill: "#ffd54f",
        stroke: "#0b121e",
        strokeThickness: 2.5,
        align: "center"
      });
      subText.anchor.set(0.5, 0.5);
      subText.y = 12;

      const padX = 10;
      const padY = 5;
      const w = Math.max(labelText.width, subText.width) + padX * 2;
      const h = labelText.height + subText.height + padY * 2;

      labelBg.beginFill(0x0a101d, 0.90);
      labelBg.lineStyle(1.5, 0x00e5ff, 0.85);
      labelBg.drawRoundedRect(-w / 2, -h / 2 + 5, w, h, 6);
      labelBg.endFill();

      labelContainer.addChild(labelBg);
      labelContainer.addChild(labelText);
      labelContainer.addChild(subText);
      portalGroup.addChild(labelContainer);

      portalGroup.on("pointerdown", (e) => {
        e.stopPropagation();
        const dist = Math.hypot(player.x - portal.x, player.y - portal.y);
        if (dist <= 65 && teleportCooldown <= 0) {
          teleportCooldown = 2.5;
          switchMap(portal.target_map_id, portal.dest_x, portal.dest_y);
        } else {
          movePlayerTo(portal.x, portal.y);
          showMapToast(`🚶 Indo para o portal de ${portal.target_name}...`);
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
          const colBuf = await fetch(`${mapMeta.collision_bin}?v=1.3.2`).then(r => r.arrayBuffer());
          colBytes = new Uint8Array(colBuf);
          COL_WIDTH = mapMeta.col_width;
          COL_HEIGHT = mapMeta.col_height;
          console.log(`Malha carregada para Mapa ${targetMapId} (${mapMeta.name}): ${colBytes.length} bytes, stride ${COL_WIDTH}x${COL_HEIGHT}`);
        } catch (e) {
          console.warn("Erro ao carregar colisão binária do mapa:", e);
        }
      } else {
        colBytes = null;
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

      // 6. Carregar dinamicamente as máscaras de transparência deste mapa
      await loadMapMasks(targetMapId);

      // 7. Atualizar HUD de Mapa
      const mapNameEl = document.querySelector(".map-name");
      if (mapNameEl) mapNameEl.textContent = `${mapMeta.name} (#${mapMeta.id})`;

      const worldCurrentLocEl = document.getElementById("worldmap-current-loc");
      if (worldCurrentLocEl) worldCurrentLocEl.textContent = `${mapMeta.name} (#${mapMeta.id})`;

      // 8. Visibilidade de elementos específicos do Mapa 1
      const isMap1 = (targetMapId === 1);
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

    // Camada 3: Marcador de Destino (Tap-to-move)
  const targetMarker = new PIXI.Graphics();
  targetMarker.visible = false;
  world.addChild(targetMarker);
  let targetPulseTimer = 0;

  // Função centralizada para mover o jogador até um ponto (Map Tap ou NPC Click)
  function movePlayerTo(targetX, targetY) {
    if (joystickActive) return;
    const validTarget = findClosestWalkable(targetX, targetY, 60);

    if (validTarget) {
      player.targetX = validTarget.x;
      player.targetY = validTarget.y;

      const dx = player.targetX - player.x;
      const dy = player.targetY - player.y;
      setDirection(calculateDirection(dx, dy));
      setAction(2); // Correr Rápido (Ação 2)

      // Mostrar Marcador de Destino
      targetMarker.x = validTarget.x;
      targetMarker.y = validTarget.y;
      targetMarker.visible = true;
      targetPulseTimer = 0;
    }
  }

  // Função para abrir o diálogo do NPC
  function showNPCDialog(npc) {
    const dlg = document.getElementById("npc-dialog");
    if (!dlg) return;
    document.getElementById("npc-dialog-name").textContent = npc.name;
    const greetings = {
      "Tân Thủ Sứ": "Chào mừng bạn đến với Làng Tân Thủ! Hãy bắt đầu hành trình của mình.",
      "Trưởng Thôn Stoff": "Ta là Trưởng thôn Stoff. Có việc gì cần ta giúp đỡ chăng?",
      "Tiệm Vũ Khí A Nhị": "Vũ khí sắc bén nhất vùng, ngươi muốn xem thử chứ?",
      "Tiệm Trang Bị Isla": "Trang bị phòng thủ kiên cố cho mọi chiến binh!",
      "Tiệm Pet Mỡ Mỡ": "Những bé Pet dễ thương và trung thành nhất đang chờ ngươi!",
      "Cây Thông Giáng Sinh": "Chúc mừng Giáng Sinh an lành và may mắn!",
      "Y Tá Loli": "Để ta hồi phục sinh lực và tinh thần cho bạn nhé!",
      "Võ Sư Xuất Vận": "Đoàn vận tiêu sẵn sàng xuất phát bất cứ lúc nào!",
      "Thủ Kho": "Kho đồ an toàn tuyệt đối, gửi gắm bảo vật tại đây.",
      "Tiệm Tạp Hóa Ông Triệu": "Đầy đủ vật phẩm thiết yếu cho chuyến phiêu lưu.",
      "Tiệm Thuốc Ông Vương": "Dược thảo và thần dược trị bách bệnh!",
      "Thùng Thư Xuất Vân": "Bảng thông báo nhiệm vụ và thư từ chuyển phát.",
      "Người Tiền Sử": "Ugg... đá cổ và bí mật từ ngàn xưa...",
      "Vận Đội": "Đoàn xe vận tiêu đang kiểm tra hàng hóa trước giờ lên đường."
    };
    document.getElementById("npc-dialog-text").textContent = greetings[npc.name] || "Xin chào nhà thám hiểm dũng cảm!";
    dlg.classList.remove("hidden");
  }

  // Camada 4 & 5: Entidades Dinâmicas (NPCs e Jogador) com Depth Sorting (Z-Order 2.5D)
  const entitiesContainer = new PIXI.Container();
  entitiesContainer.sortableChildren = true;
  world.addChild(entitiesContainer);

  const npcList = [];

  // Instanciação dos Modelos Reais de NPCs
  npcsData.forEach(npc => {
    const npcGroup = new PIXI.Container();
    npcGroup.x = npc.x;
    npcGroup.y = npc.y;
    npcGroup.zIndex = Math.round(npc.y);

    // Sombra suave calibrada nos pés
    const sRadiusX = Math.round((npc.shadow_radius_x || 16) * 0.70);
    const sRadiusY = Math.round((npc.shadow_radius_y || 8) * 0.70);
    const shadow = new PIXI.Graphics();
    shadow.beginFill(0x000000, 0.38);
    shadow.drawEllipse(0, 0, sRadiusX, sRadiusY);
    shadow.endFill();
    npcGroup.addChild(shadow);

    // Sprite animado ou estático
    let sprite;
    if (npc.is_animated && npc.frames && npc.frames.length > 1) {
      const textures = npc.frames.map(f => PIXI.Texture.from(f));
      sprite = new PIXI.AnimatedSprite(textures);
      sprite.animationSpeed = 0.08;
      sprite.play();
    } else if (npc.frames && npc.frames.length > 0) {
      sprite = new PIXI.Sprite(PIXI.Texture.from(npc.frames[0]));
    } else {
      sprite = new PIXI.Sprite();
    }

    // Âncora nos pés (bottom center: 0.5, 1.0)
    sprite.anchor.set(0.5, 1.0);

    // Escala 0.70 (30% de redução, proporcional ao jogador)
    // Direção 7 é invertida horizontalmente (scaleX = -0.70)
    const dirScaleX = (npc.dir === 7) ? -0.70 : 0.70;
    sprite.scale.set(dirScaleX, 0.70);
    npcGroup.addChild(sprite);

    // Nome do NPC em tom dourado com contorno escuro
    const text = new PIXI.Text(npc.name, {
      fontFamily: "system-ui, -apple-system, sans-serif",
      fontSize: 11,
      fontWeight: "bold",
      fill: 0xfff070,
      stroke: 0x000000,
      strokeThickness: 3,
      align: "center"
    });
    text.anchor.set(0.5, 1.0);
    text.y = - Math.round(npc.height * 0.70) - 4;
    npcGroup.addChild(text);

    // Interação de Clique/Toque no NPC
    npcGroup.eventMode = "static";
    npcGroup.cursor = "pointer";
    npcGroup.on("pointerdown", (e) => {
      e.stopPropagation();
      movePlayerTo(npc.x, npc.y + 16);
      showNPCDialog(npc);
    });

    entitiesContainer.addChild(npcGroup);
    npcList.push(npcGroup);
  });

  // Spawn do Monstro no Mapa 1 (Área aberta na praça)
  const mapMonsterGroup = new PIXI.Container();
  mapMonsterGroup.x = 1080;
  mapMonsterGroup.y = 950;
  mapMonsterGroup.zIndex = 950;

  // Sombra nos pés do monstro
  const monsterShadow = new PIXI.Graphics();
  monsterShadow.beginFill(0x000000, 0.38);
  monsterShadow.drawEllipse(0, 0, 16, 7);
  monsterShadow.endFill();
  mapMonsterGroup.addChild(monsterShadow);

  // Sprite dinâmico do Monstro no Mapa (controlado por animações completas)
  const mapMonsterSprite = new PIXI.Sprite();
  mapMonsterSprite.anchor.set(0.5, 1.0);
  mapMonsterSprite.scale.set(0.70); // Proporcional ao jogador (-30%)
  mapMonsterGroup.addChild(mapMonsterSprite);

  // Etiqueta com Nome e Nível do Monstro (vermelho de criatura agressiva)
  const mapMonsterName = new PIXI.Text("⚔️ Cogumelo Selvagem [Nv. 5]", {
    fontFamily: "system-ui, -apple-system, sans-serif",
    fontSize: 11,
    fontWeight: "bold",
    fill: 0xff6b6b,
    stroke: 0x000000,
    strokeThickness: 3,
    align: "center"
  });
  mapMonsterName.anchor.set(0.5, 1.0);
  mapMonsterName.y = - Math.round(monsterMeta.height * 0.70) - 4;
  mapMonsterGroup.addChild(mapMonsterName);

  // Entidade Monstro & Funções de Ação/Direção
  const monster = {
    x: 1080,
    y: 950,
    dir: 6, // Vira para a esquerda (encarando o jogador)
    action: 0,
    frameIdx: 0,
    frameTimer: 0,
    frameDuration: 0.08,
    offsetX: 0,
    offsetY: 0
  };

  function setMonsterAction(newAction) {
    monster.action = newAction;
    monster.frameIdx = 0;
    monster.frameTimer = 0;
    if (newAction === 4) {
      mapMonsterName.y = -18;
      monsterShadow.clear();
      monsterShadow.beginFill(0x000000, 0.38);
      monsterShadow.drawEllipse(0, 0, 24, 7);
      monsterShadow.endFill();
      mapMonsterSprite.tint = 0xffffff;
    } else if (newAction === 5) {
      mapMonsterSprite.tint = 0xff6666;
      mapMonsterName.y = - Math.round(monsterMeta.height * 0.70) - 4;
    } else {
      mapMonsterSprite.tint = 0xffffff;
      mapMonsterName.y = - Math.round(monsterMeta.height * 0.70) - 4;
      monsterShadow.clear();
      monsterShadow.beginFill(0x000000, 0.38);
      monsterShadow.drawEllipse(0, 0, 16, 7);
      monsterShadow.endFill();
    }
  }

  function setMonsterDirection(newDir) {
    monster.dir = newDir;
    monster.frameIdx = 0;
    monster.frameTimer = 0;
  }

  async function setMapMonster(monsterId, customMeta = null) {
    currentMonsterId = monsterId;
    console.log(`Carregando monstro ${monsterId}...`);

    let metaPath = `assets/monsters/${monsterId}/visual_meta.json`;
    let atlasPath = `assets/monsters/${monsterId}/atlas.json`;

    try {
      const [newMeta, newSheet] = await Promise.all([
        customMeta ? Promise.resolve(customMeta) : fetch(metaPath).then(r => r.json()),
        PIXI.Assets.load(atlasPath)
      ]);

      monsterMeta = newMeta;
      monsterSheet = newSheet;

      const lvl = newMeta.db_id ? (parseInt(newMeta.db_id) % 85 + 5) : 5;
      mapMonsterName.text = `⚔️ ${newMeta.name} [Nv. ${lvl}]`;
      mapMonsterName.y = - Math.round(newMeta.height * 0.70) - 4;

      const cbVersus = document.getElementById("combat-versus-text");
      if (cbVersus) {
        cbVersus.textContent = `${playerName.text} vs ${newMeta.name}`;
      }

      setMonsterAction(0);
      spawnCombatText(`👾 Monstro: ${newMeta.name}!`, monster.x, monster.y - 60, 0xff7777);

      document.querySelectorAll(".mon-quick-btn").forEach(b => {
        b.classList.toggle("active", b.dataset.monster === monsterId);
      });
      console.log(`Monstro ${newMeta.name} ativado com sucesso!`);
    } catch(err) {
      console.error(`Erro ao carregar monstro ${monsterId}:`, err);
    }
  }

  function updateMonsterVisual(deltaSeconds) {
    const animKey = `${monster.dir}-${monster.action}`;
    let animFrames = (monsterSheet.animations && monsterSheet.animations[animKey]) ||
                     (monsterSheet.animations && monsterSheet.animations[`${monster.dir}-0`]) ||
                     (monsterSheet.animations && monsterSheet.animations["0-0"]);
    if (!animFrames || animFrames.length === 0) return;

    monster.frameTimer += deltaSeconds;
    if (monster.frameTimer >= monster.frameDuration) {
      monster.frameTimer = 0;
      monster.frameIdx = (monster.frameIdx + 1) % animFrames.length;

      if (monster.action === 4) {
        monster.frameIdx = animFrames.length - 1; // Trava caído no chão
      } else if (monster.action >= 3 && monster.frameIdx === 0) {
        setMonsterAction(0);
        return;
      }
    }

    const currentTexture = animFrames[monster.frameIdx % animFrames.length];
    if (currentTexture) {
      mapMonsterSprite.texture = currentTexture;
      const monAnchorY = monsterMeta && monsterMeta.anchor ? monsterMeta.anchor[1] : 1.0;
      mapMonsterSprite.anchor.set(0.5, monAnchorY);
      mapMonsterSprite.position.set(0, MONSTER_GROUND_OFFSET_Y);
    }

    mapMonsterGroup.x = monster.x + monster.offsetX;
    mapMonsterGroup.y = monster.y + monster.offsetY;
    mapMonsterGroup.zIndex = Math.round(monster.y);
  }

  // Interação de Clique/Toque no Monstro para Iniciar Modo de Teste de Combate
  mapMonsterGroup.eventMode = "static";
  mapMonsterGroup.cursor = "pointer";
  mapMonsterGroup.on("pointerdown", (e) => {
    e.stopPropagation();
    openCombatTest();
  });

  entitiesContainer.addChild(mapMonsterGroup);

  // Textos Flutuantes de Combate no Mundo 2.5D
  const combatTextContainer = new PIXI.Container();
  combatTextContainer.zIndex = 9999;
  world.addChild(combatTextContainer);
  const combatFloatingTexts = [];

  function spawnCombatText(text, wx, wy, color = 0xffe066) {
    const txt = new PIXI.Text(text, {
      fontFamily: "system-ui, -apple-system, sans-serif",
      fontSize: 13,
      fontWeight: "900",
      fill: color,
      stroke: 0x000000,
      strokeThickness: 3,
      align: "center",
      dropShadow: true,
      dropShadowColor: 0x000000,
      dropShadowDistance: 2
    });
    txt.anchor.set(0.5, 1.0);
    txt.x = wx;
    txt.y = wy;
    combatTextContainer.addChild(txt);
    combatFloatingTexts.push({
      sprite: txt,
      life: 0.9,
      maxLife: 0.9,
      vy: -40
    });
  }

  function updateCombatTexts(deltaSeconds) {
    for (let i = combatFloatingTexts.length - 1; i >= 0; i--) {
      const ft = combatFloatingTexts[i];
      ft.life -= deltaSeconds;
      ft.sprite.y += ft.vy * deltaSeconds;
      ft.sprite.alpha = Math.max(0, ft.life / ft.maxLife);
      if (ft.life <= 0) {
        combatTextContainer.removeChild(ft.sprite);
        combatFloatingTexts.splice(i, 1);
      }
    }
  }

  // Camada 5: Jogador (Entidade Dinâmica)
  // ORIGEM (0, 0) são os pés do personagem!
  const playerContainer = new PIXI.Container();
  playerContainer.x = 1000;
  playerContainer.y = 1000;
  playerContainer.zIndex = 1000;

  // Calibração de Solo & Contato com a Sombra (Pés no Chão)
  const PLAYER_GROUND_OFFSET_Y = 5; // Baixa o personagem 8px para assentar as solas dos pés firmemente na elipse de sombra
  const MONSTER_GROUND_OFFSET_Y = 4; // Baixa o monstro 6px para assentar sobre o piso

  // Sombra nos pés (0, 0) - proporção calibrada para escala 0.70 (-30%)
  const shadow = new PIXI.Graphics();
  shadow.beginFill(0x000000, 0.4);
  shadow.drawEllipse(0, 0, 16, 7);
  shadow.endFill();
  playerContainer.addChild(shadow);

  // Sprite animado do Jogador
  // Cada frame PNG é 200x150. Pés estão no centro horizontal (100) e Y=110.
  // Escala reduzida em 30% conforme feedback do usuário -> scale = 0.70!
  const charSprite = new PIXI.Sprite();
  charSprite.anchor.set(0.5, 110 / 150);
  charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
  charSprite.scale.set(0.70);
  playerContainer.addChild(charSprite);

  // Sprite animado das Asas (Renderizado atrás do corpo ou à frente nas costas)
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
  playerContainer.addChild(weaponSprite);

  // Nome do Jogador centralizado acima da cabeça (calibrado para escala 0.70)
  const playerName = new PIXI.Text("Guerreiro Evoluído", {
    fontFamily: "sans-serif",
    fontSize: 11,
    fontWeight: "bold",
    fill: 0xa3be8c,
    stroke: 0x000000,
    strokeThickness: 3
  });
  playerName.anchor.set(0.5, 1);
  playerName.y = -70;
  playerContainer.addChild(playerName);

  entitiesContainer.addChild(playerContainer);

  // Camada 6: Máscaras de Telhado / Árvores (Foreground / Sobreposição Universal 76 Mapas)
  const maskContainer = new PIXI.Container();
  world.addChild(maskContainer);

  const maskSprites = [];

  async function loadMapMasks(mapId) {
    if (maskContainer) maskContainer.removeChildren();
    maskSprites.length = 0;

    const masksUrl = (mapId === 1) ? "assets/map1/masks.json" : `assets/maps/map_${mapId}/masks.json`;

    try {
      const resp = await fetch(`${masksUrl}?v=1.6.0`);
      if (!resp.ok) return;
      const mData = await resp.json();
      if (!Array.isArray(mData)) return;

      for (const maskInfo of mData) {
        try {
          const tex = await PIXI.Assets.load(maskInfo.file);
          const mSprite = new PIXI.Sprite(tex);
          mSprite.x = maskInfo.x;
          mSprite.y = maskInfo.y;
          if (maskInfo.w) mSprite.width = maskInfo.w;
          if (maskInfo.h) mSprite.height = maskInfo.h;
          maskContainer.addChild(mSprite);
          maskSprites.push({ sprite: mSprite, info: maskInfo });
        } catch (errTex) {
          console.warn(`Aviso ao carregar textura de máscara ${maskInfo.file}:`, errTex);
        }
      }
      console.log(`Carregadas ${maskSprites.length} sobreposições de primeiro plano para o mapa #${mapId}.`);
    } catch (e) {
      console.log(`Nenhuma sobreposição de primeiro plano para o mapa #${mapId}.`);
    }
  }

  // Carregar máscaras de primeiro plano do mapa inicial
  await loadMapMasks(currentMapId);

  // 5. Gerenciamento e Carregamento Dinâmico de Personagens (Classes & Evoluções)
  let activeManifest = {};
  const textureCache = {};
  let currentModel = "char11";

  const modelLabels = {
    "char11": "Guerreiro Evoluído (Tier 2)",
    "char1": "Guerreiro Base (Tier 1)",
    "char2": "Mago Base",
    "char_mount": "Montaria (Pose)"
  };

  async function setCharacterModel(modelId, metaInfo = null) {
    currentModel = modelId;
    console.log(`Carregando modelo de personagem ${modelId}...`);

    if (modelId.startsWith("PC_") || modelId.startsWith("mount_")) {
      try {
        const basePath = modelId.startsWith("mount_") ? `assets/mounts/${modelId}` : `assets/characters/${modelId}`;
        const [sheet, meta] = await Promise.all([
          PIXI.Assets.load(`${basePath}/atlas.json`),
          metaInfo ? Promise.resolve(metaInfo) : fetch(`${basePath}/visual_meta.json`).then(r => r.json())
        ]);
        currentSpritesheet = sheet;
        currentMeta = meta;

        playerName.text = meta.name || modelId;
        playerName.y = - Math.round((meta.height || 100) * 0.70) - 8;

        const acts = meta.actions || [];
        const has8 = acts.includes(8);
        const has9 = acts.includes(9);
        const has10 = acts.includes(10);
        const btn8 = document.getElementById("btn-act8");
        const btn9 = document.getElementById("btn-act9");
        const btn10 = document.getElementById("btn-act10");
        const btnUlt = document.getElementById("btn-act-ultimate");
        if (btn8) btn8.style.display = has8 ? "block" : "none";
        if (btn9) btn9.style.display = has9 ? "block" : "none";
        if (btn10) btn10.style.display = has10 ? "block" : "none";
        if (btnUlt) btnUlt.style.display = has10 ? "flex" : "none";

        const cbVersus = document.getElementById("combat-versus-text");
        if (cbVersus && monsterMeta) {
          cbVersus.textContent = `${meta.name} vs ${monsterMeta.name}`;
        }

        spawnCombatText(`✨ Classe: ${meta.name}!`, player.x, player.y - 60, 0xebcb8b);
      } catch(e) {
        console.error(`Erro ao carregar classe ${modelId}:`, e);
      }
    } else {
      currentSpritesheet = null;
      currentMeta = null;
      playerName.text = modelLabels[modelId] || "Personagem";
      playerName.y = -70;
      activeManifest = await fetch(`assets/${modelId}/char_manifest.json`).then(r => r.json());

      const loadPromises = [];
      for (const animKey in activeManifest) {
        for (const frameInfo of activeManifest[animKey]) {
          if (!textureCache[frameInfo.file]) {
            loadPromises.push(
              PIXI.Assets.load(frameInfo.file).then(tex => {
                textureCache[frameInfo.file] = tex;
              })
            );
          }
        }
      }
      await Promise.all(loadPromises);

      const has8 = !!activeManifest[`0-8`];
      const has9 = !!activeManifest[`0-9`];
      const has10 = !!activeManifest[`0-10`];
      const btn8 = document.getElementById("btn-act8");
      const btn9 = document.getElementById("btn-act9");
      const btn10 = document.getElementById("btn-act10");
      const btnUlt = document.getElementById("btn-act-ultimate");
      if (btn8) btn8.style.display = has8 ? "block" : "none";
      if (btn9) btn9.style.display = has9 ? "block" : "none";
      if (btn10) btn10.style.display = has10 ? "block" : "none";
      if (btnUlt) btnUlt.style.display = has10 ? "flex" : "none";
    }

    document.querySelectorAll(".model-btn").forEach(b => {
      b.classList.toggle("active", b.dataset.model === modelId);
    });

    player.frameIdx = 0;
    player.frameTimer = 0;
    updateHUD();
  }

  // Sistema de Arma Empunhada (Armaria & Combate Visual)
  let playerEquippedWeapon = null;
  let currentWeaponManifest = null;
  let currentWeaponModel = null;

  // Sistema de Asas Visuais Equipadas
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
  }

  async function equipWing(item) {
    if (!item) {
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
    }

    const modelId = item.active_wing_model || item.model_id || "equip_wing_001001";
    playerEquippedWing = item;
    currentWingModel = modelId;
    localStorage.setItem("mc_equipped_wing_id", String(item.id));

    try {
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
  }

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
      const manifestUrl = `assets/weapons/${modelId}/char_manifest.json?v=1.5.4`;
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

  // 6. Entidade do Jogador & Parâmetros
  const player = {
    x: 1000,
    y: 1000,
    targetX: null,
    targetY: null,
    speed: 140, // pixels por segundo (ajustado para escala 0.70)
    dir: 0,     // 0: Sul, 1: Sudeste, 2: Leste, 3: Nordeste, 4: Norte, 5: Noroeste, 6: Oeste, 7: Sudoeste
    action: 0,  // 0: Stand
    frameIdx: 0,
    frameTimer: 0,
    frameDuration: 0.08
  };

  // 7. Fórmula Matemática Exata de Direção (0..7)
  function calculateDirection(dx, dy) {
    const angle = Math.atan2(dy, dx) * (180 / Math.PI); // -180 a 180 (dy positivo para baixo)
    let sector = Math.round((90 - angle) / 45);
    return ((sector % 8) + 8) % 8;
  }

  const dirNames = [
    "0 (Sul / Frente)",
    "1 (Sudeste / Baixo-Dir)",
    "2 (Leste / Direita)",
    "3 (Nordeste / Cima-Dir)",
    "4 (Norte / Costas)",
    "5 (Noroeste / Cima-Esq)",
    "6 (Oeste / Esquerda)",
    "7 (Sudoeste / Baixo-Esq)"
  ];

  const actionNames = {
    0: "0: Parado (Stand / Breath)",
    1: "1: Caminhada (Walk)",
    2: "2: Corrida Rápida (Run / Rush)",
    3: "3: Golpe / Ataque Físico",
    4: "4: Caído / Morto (Dead)",
    5: "5: Dano / Levando Golpe (Hurt)",
    6: "6: Defesa / Guarda (Block)",
    7: "7: Conjuração / Magia (Cast)",
    8: "8: Buff / Postura de Combate",
    9: "9: Golpe Pesado (Heavy Slash)",
    10: "10: Habilidade Suprema (Ultimate 32f)"
  };

  // 8. Atualização do HUD (Mobile & Drawer)
  const posDisplay = document.getElementById("pos-display");
  const dirDisplay = document.getElementById("dir-display");
  const drawerPos = document.getElementById("drawer-pos");
  const drawerDir = document.getElementById("drawer-dir");
  const drawerAnim = document.getElementById("drawer-anim");
  const drawerWalkable = document.getElementById("drawer-walkable");
  const drawerOccluded = document.getElementById("drawer-occluded");

  function updateHUD() {
    const px = Math.round(player.x);
    const py = Math.round(player.y);
    if (posDisplay) posDisplay.innerText = `${px}, ${py}`;
    if (dirDisplay) dirDisplay.innerText = dirNames[player.dir] || player.dir;

    if (drawerPos) drawerPos.innerText = `X: ${px} | Y: ${py}`;
    if (drawerDir) drawerDir.innerText = dirNames[player.dir] || player.dir;

    const animKey = `${player.dir}-${player.action}`;
    let totalFrames = 1;
    if (currentSpritesheet && currentSpritesheet.animations && currentSpritesheet.animations[animKey]) {
      totalFrames = currentSpritesheet.animations[animKey].length;
    } else if (activeManifest && activeManifest[animKey]) {
      totalFrames = activeManifest[animKey].length;
    }
    if (drawerAnim) drawerAnim.innerText = `${animKey} [${player.frameIdx + 1}/${totalFrames}] - ${actionNames[player.action] || 'Ação'}`;

    const walkable = canStand(player.x, player.y);
    if (drawerWalkable) {
      drawerWalkable.innerText = walkable ? "LIVRE (Walkable)" : "BLOQUEADO!";
      drawerWalkable.style.color = walkable ? "#a3be8c" : "#bf616a";
    }
  }

  function setAction(newAction) {
    if (player.action !== newAction) {
      player.action = newAction;
      player.frameIdx = 0;
      player.frameTimer = 0;

      // Feedback visual e ajustes específicos de cada ação
      if (newAction === 4) {
        // Derrotado / Caído: posiciona o nome rente ao corpo no chão e alarga a sombra
        playerName.y = -28;
        shadow.clear();
        shadow.beginFill(0x000000, 0.4);
        shadow.drawEllipse(0, 0, 24, 7);
        shadow.endFill();
        charSprite.tint = 0xffffff;
      } else if (newAction === 5) {
        // Dano / Hurt: flash avermelhado no impacto
        playerName.y = -70;
        shadow.clear();
        shadow.beginFill(0x000000, 0.4);
        shadow.drawEllipse(0, 0, 16, 7);
        shadow.endFill();
        charSprite.tint = 0xff7777;
      } else {
        // Demais ações normais
        playerName.y = -70;
        shadow.clear();
        shadow.beginFill(0x000000, 0.4);
        shadow.drawEllipse(0, 0, 16, 7);
        shadow.endFill();
        charSprite.tint = 0xffffff;
      }

      // Atualizar botões de ação na gaveta (0 a 10)
      document.querySelectorAll(".action-btn-test").forEach(b => {
        b.classList.toggle("active", parseInt(b.dataset.action) === newAction);
      });

      updateHUD();
    }
  }

  function setDirection(newDir) {
    player.dir = newDir;
    player.frameIdx = 0;
    player.frameTimer = 0;
    document.querySelectorAll(".dir-btn[data-dir]").forEach(b => {
      b.classList.toggle("active", b.dataset.dir == newDir);
    });
    updateHUD();
  }

  // 9. Atualização Visual do Sprite
  // O sprite tem âncora fixa (0.5, 110/150) e posição (0, 0), garantindo 100% de
  // alinhamento com a sombra e nome sob qualquer direção e ação.
  function updatePlayerVisual(deltaSeconds) {
    const animKey = `${player.dir}-${player.action}`;
    let animFrames = null;
    let isSpritesheet = false;

    if (currentSpritesheet && currentSpritesheet.animations) {
      animFrames = currentSpritesheet.animations[animKey] ||
                   currentSpritesheet.animations[`${player.dir}-0`] ||
                   currentSpritesheet.animations["0-0"];
      isSpritesheet = true;
    } else if (activeManifest) {
      animFrames = activeManifest[animKey] ||
                   activeManifest[`${player.dir}-0`] ||
                   activeManifest["0-0"];
      isSpritesheet = false;
    }

    if (!animFrames || animFrames.length === 0) return;

    player.frameTimer += deltaSeconds;
    if (player.frameTimer >= player.frameDuration) {
      player.frameTimer = 0;
      player.frameIdx = (player.frameIdx + 1) % animFrames.length;

      if (player.action === 4) {
        player.frameIdx = animFrames.length - 1;
      } else if (player.action >= 3 && player.frameIdx === 0) {
        setAction(0);
        return;
      }
      updateHUD();
    }

    // Verificação de Montaria Voadora (tapetes, vassouras, pranchas, nuvens)
    const isFlyingMount = !!(playerEquippedWing && (
      playerEquippedWing.is_fly_mount ||
      (currentWingModel && currentWingModel.startsWith("equip_fly_")) ||
      (playerEquippedWing.model_id && playerEquippedWing.model_id.startsWith("equip_fly_"))
    ));

    // Flutuação suave e elevação dinâmica em montarias voadoras
    let hoverBob = 0;
    let charOffsetY = PLAYER_GROUND_OFFSET_Y;
    if (isFlyingMount) {
      hoverBob = Math.sin(performance.now() * 0.003) * 6;
      // Elevação expressiva do herói: fica a -62px do solo, pousado perfeitamente no convés da montaria
      charOffsetY = -52 + hoverBob;
      if (shadow) {
        shadow.scale.set(0.70, 0.70); // Sombra menor no solo para refletir a alta altitude
        shadow.alpha = 0.55;
      }
      if (typeof playerName !== 'undefined' && playerName) {
        playerName.y = charOffsetY - 62;
      }
    } else {
      if (shadow) {
        shadow.scale.set(1.0, 1.0);
        shadow.alpha = 0.85;
      }
      if (typeof playerName !== 'undefined' && playerName) {
        playerName.y = -70;
      }
    }

    if (isSpritesheet) {
      const tex = animFrames[player.frameIdx % animFrames.length];
      if (tex) {
        charSprite.texture = tex;
        const anchorY = currentMeta && currentMeta.anchor ? currentMeta.anchor[1] : 1.0;
        charSprite.anchor.set(0.5, anchorY);
        charSprite.position.set(0, charOffsetY);
      }
    } else {
      const currentFrameData = animFrames[player.frameIdx % animFrames.length];
      const tex = textureCache[currentFrameData.file];
      if (tex) {
        charSprite.texture = tex;
        charSprite.anchor.set(0.5, 110 / 150);
        charSprite.position.set(0, charOffsetY);
      }
    }

    // Sincronizar asas / montarias voadoras na mesma direção e frame de ação
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

            if (isFlyingMount) {
              // Montaria voadora posicionada sob os pés do personagem (flutua a -38px do solo):
              wingSprite.position.set(0, -36 + hoverBob);
              wingSprite.visible = true;

              // O herói deve sempre cavalgar EM CIMA da montaria voadora (renderizar por trás/sob o corpo)
              const bodyIdx = playerContainer.getChildIndex(charSprite);
              const curWingIdx = playerContainer.getChildIndex(wingSprite);
              if (curWingIdx > bodyIdx) {
                playerContainer.setChildIndex(wingSprite, Math.max(0, bodyIdx - 1));
              }
            } else {
              // Asas normais equipadas nas costas:
              wingSprite.position.set(0, PLAYER_GROUND_OFFSET_Y - 38);
              wingSprite.visible = true;

              // Z-Order: se virado de costas (Norte: dirs 3, 4, 5), asas na frente do corpo
              // Caso contrário (Frente/Sul/Lados: dirs 0, 1, 2, 6, 7), asas atrás do corpo
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
        }
      } else {
        wingSprite.visible = false;
      }
    }

    // Sincronizar arma empunhada na mesma direção e frame de ação (acompanha elevação do corpo)
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
            weaponSprite.position.set(0, charOffsetY);
            weaponSprite.visible = true;
          }
        }
      } else {
        weaponSprite.visible = false;
      }
    }
  }

  // 10. Resolução de Movimento com Colisão e Deslize (Wall Sliding)
  function tryStep(fromX, fromY, stepDx, stepDy) {
    const nextX = fromX + stepDx;
    const nextY = fromY + stepDy;

    // 1. Passo direto
    if (canStand(nextX, nextY)) {
      return { x: nextX, y: nextY, hit: false };
    }

    // 2. Deslizar no eixo X (apenas se havia componente de movimento em X)
    if (Math.abs(stepDx) > 0.01 && canStand(nextX, fromY)) {
      return { x: nextX, y: fromY, hit: true };
    }

    // 3. Deslizar no eixo Y (apenas se havia componente de movimento em Y)
    if (Math.abs(stepDy) > 0.01 && canStand(fromX, nextY)) {
      return { x: fromX, y: nextY, hit: true };
    }

    // 4. Bloqueado em ambos os eixos
    return { x: fromX, y: fromY, hit: true };
  }

  function movePlayer(deltaX, deltaY) {
    const dist = Math.hypot(deltaX, deltaY);
    if (dist <= 0) return false;

    // Sub-steps a cada ~2.5 pixels para máxima precisão
    const steps = Math.ceil(dist / 2.5);
    const stepDx = deltaX / steps;
    const stepDy = deltaY / steps;

    let hitWall = false;
    for (let i = 0; i < steps; i++) {
      const res = tryStep(player.x, player.y, stepDx, stepDy);
      player.x = res.x;
      player.y = res.y;
      if (res.hit) hitWall = true;
    }

    playerContainer.x = player.x;
    playerContainer.y = player.y;
    return hitWall;
  }

  // 11. Joystick Virtual Analógico Mobile
  const joystickContainer = document.getElementById("joystick-container");
  const joystickBase = document.getElementById("joystick-base");
  const joystickHandle = document.getElementById("joystick-handle");
  let joystickActive = false;
  let joyVectorX = 0;
  let joyVectorY = 0;
  const JOY_MAX_DIST = 40;

  function onJoyStart(clientX, clientY) {
    joystickActive = true;
    pendingBattleMonster = null;
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;
    onJoyMove(clientX, clientY);
  }

  function onJoyMove(clientX, clientY) {
    if (!joystickActive) return;
    const rect = joystickBase.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;

    const dx = clientX - centerX;
    const dy = clientY - centerY;
    const dist = Math.hypot(dx, dy);

    if (dist > 5) {
      const clamped = Math.min(dist, JOY_MAX_DIST);
      joyVectorX = (dx / dist) * (clamped / JOY_MAX_DIST);
      joyVectorY = (dy / dist) * (clamped / JOY_MAX_DIST);

      joystickHandle.style.transform = `translate(${(dx / dist) * clamped}px, ${(dy / dist) * clamped}px)`;

      // Atualizar direção e ação de movimento (Corrida Rápida: Ação 2)
      const newDir = calculateDirection(dx, dy);
      setDirection(newDir);
      setAction(2); // Correr Rápido
    }
  }

  function onJoyEnd() {
    if (!joystickActive) return;
    joystickActive = false;
    joyVectorX = 0;
    joyVectorY = 0;
    joystickHandle.style.transform = `translate(0px, 0px)`;
    setAction(0); // Stand
  }

  joystickContainer.addEventListener("pointerdown", (e) => {
    joystickContainer.setPointerCapture(e.pointerId);
    onJoyStart(e.clientX, e.clientY);
  });
  joystickContainer.addEventListener("pointermove", (e) => {
    if (joystickActive) onJoyMove(e.clientX, e.clientY);
  });
  joystickContainer.addEventListener("pointerup", () => onJoyEnd());
  joystickContainer.addEventListener("pointercancel", () => onJoyEnd());

  // 12. Tap / Clique no Mapa para Andar
  mapSprite.on("pointerdown", (e) => {
    if (joystickActive) return;
    pendingBattleMonster = null;
    const worldPoint = e.getLocalPosition(mapSprite);
    movePlayerTo(worldPoint.x, worldPoint.y);
  });

  // 13. Câmera e Zoom
  let cameraFollow = true;
  let zoomLevel = 1.0;

  function updateCamera() {
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
    const minY = screenHeight - MAP_HEIGHT * zoomLevel;

    if (minX < 0) camX = Math.max(minX, Math.min(0, camX));
    else camX = (screenWidth - MAP_WIDTH * zoomLevel) / 2;

    if (minY < 0) camY = Math.max(minY, Math.min(0, camY));
    else camY = (screenHeight - MAP_HEIGHT * zoomLevel) / 2;

    world.scale.set(zoomLevel);
    world.x = camX;
    world.y = camY;
  }

  // 13.5 Sistema de Teste de Animações em Combate (Direto no Mapa)
  let isCombatTesting = false;
  let sparringLoopActive = false;
  let sparringTimer = null;
  let sparringStep = 0;
  let isActionExecuting = false;

  const combatTestPanel = document.getElementById("combat-test-panel");
  const combatStatusText = document.getElementById("combat-status-text");
  const mobileActionBar = document.getElementById("mobile-action-bar");

  function setCombatStatus(msg) {
    if (combatStatusText) combatStatusText.textContent = msg;
  }

  function openCombatTest() {
    closeDrawer();
    closeNpcDlg();

    isCombatTesting = true;
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;

    // Posiciona o jogador a 60px à esquerda do monstro
    player.x = 1020;
    player.y = 950;
    playerContainer.x = player.x;
    playerContainer.y = player.y;

    // Jogador olha para o leste (em direção ao monstro)
    setDirection(2);
    setAction(0);

    // Monstro olha para o oeste (em direção ao jogador)
    monster.x = 1080;
    monster.y = 950;
    monster.offsetX = 0;
    monster.offsetY = 0;
    setMonsterDirection(6);
    setMonsterAction(0);

    // Foca câmera entre os dois combatentes
    applyZoom(1.2);
    updateCamera();

    if (combatTestPanel) {
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
  }

  function closeCombatTest() {
    isCombatTesting = false;
    stopSparring();
    resetCombatPoses();

    if (combatTestPanel) combatTestPanel.classList.add("hidden");
    if (mobileActionBar) mobileActionBar.style.display = "";
    if (joystickContainer) joystickContainer.style.display = "";

    updateCamera();
  }

  
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

  function resetCombatPoses() {
    stopSparring();
    setAction(0);
    setMonsterAction(0);
    playerContainer.x = player.x;
    monster.offsetX = 0;
    charSprite.tint = 0xffffff;
    mapMonsterSprite.tint = 0xffffff;
    setCombatStatus("🧍 Poses resetadas para Parado / Idle.");
  }

  // Ações do Jogador
  async function testPlayerAttack() {
    if (isActionExecuting) return;
    isActionExecuting = true;
    setCombatStatus("⚔️ Jogador avança com Golpe Físico (Ação 3)!");

    setAction(3); // Golpe Físico
    playerContainer.x = player.x + 18; // Avanço

    await new Promise(r => setTimeout(r, 200));
    playSkillVFX(10008, monster.x, monster.y - 30, { shake: true, speed: 0.5 });
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("💥 GOLPE! -540", monster.x, monster.y - 65, 0xffe066);

    await new Promise(r => setTimeout(r, 280));
    playerContainer.x = player.x;
    setAction(0);
    setMonsterAction(0);
    isActionExecuting = false;
    setCombatStatus("Pronto para o próximo teste de ação.");
  }

  async function testPlayerSkill() {
    if (isActionExecuting) return;
    isActionExecuting = true;
    setCombatStatus("🔮 Jogador conjura Magia Arcana (Ação 7)!");

    setAction(7); // Magia

    await new Promise(r => setTimeout(r, 280));
    playSkillVFX(302, monster.x, monster.y - 30, { shake: true, speed: 0.45 });
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("🔮 EXPLOSÃO ARCANA! -780", monster.x, monster.y - 65, 0xb48ead);

    await new Promise(r => setTimeout(r, 350));
    setAction(0);
    setMonsterAction(0);
    isActionExecuting = false;
    setCombatStatus("Pronto para o próximo teste de ação.");
  }

  async function testPlayerUltimate() {
    if (isActionExecuting) return;
    isActionExecuting = true;
    setCombatStatus("⚡ Jogador executa Habilidade Suprema (Ação 10: 32 frames)!");

    setAction(activeManifest[`${player.dir}-10`] ? 10 : 3);
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
    spawnCombatText("💥 CRÍTICO!", monster.x, monster.y - 90, 0xff3333);

    await new Promise(r => setTimeout(r, 450));
    player.frameDuration = 0.08;
    playerContainer.x = player.x;
    setAction(0);
    setMonsterAction(0);
    isActionExecuting = false;
    setCombatStatus("Pronto para o próximo teste de ação.");
  }

  function testPlayerDefend() {
    setCombatStatus("🛡️ Jogador assume Postura de Guarda / Defesa (Ação 6)!");
    setAction(6);
    spawnCombatText("🛡️ GUARDA", player.x, player.y - 70, 0x88c0d0);
  }

  function testPlayerHurt() {
    setCombatStatus("💥 Jogador executando animação de Tomar Dano (Ação 5)!");
    setAction(5);
    spawnCombatText("💥 DANO", player.x, player.y - 70, 0xbf616a);
  }

  function testPlayerDead() {
    setCombatStatus("💀 Jogador caído no chão (Ação 4)! Toque em 'Resetar Poses' para levantar.");
    setAction(4);
    spawnCombatText("💀 CAÍDO", player.x, player.y - 35, 0xbf616a);
  }

  // Ações do Monstro
  async function testMonsterAttack() {
    if (isActionExecuting) return;
    isActionExecuting = true;
    setCombatStatus("🍄 Cogumelo avança com Cabeçada (Ação 3)!");

    setMonsterAction(3); // Ataque
    monster.offsetX = -18; // Avanço

    await new Promise(r => setTimeout(r, 260));
    if (player.action === 6) {
      spawnCombatText("🛡️ BLOQUEADO!", player.x, player.y - 70, 0x88c0d0);
    } else {
      setAction(5); // Hurt do Jogador
      spawnCombatText("🍄 CABEÇADA!", player.x, player.y - 70, 0xbf616a);
    }

    await new Promise(r => setTimeout(r, 300));
    monster.offsetX = 0;
    setMonsterAction(0);
    if (player.action === 5) setAction(0);
    isActionExecuting = false;
    setCombatStatus("Pronto para o próximo teste de ação.");
  }

  async function testMonsterSkill() {
    if (isActionExecuting) return;
    isActionExecuting = true;
    setCombatStatus("☠️ Cogumelo libera Nuvem de Esporos (Ação 7)!");

    setMonsterAction(7); // Magia

    await new Promise(r => setTimeout(r, 350));
    setAction(5); // Hurt do Jogador
    charSprite.tint = 0x86efac;
    spawnCombatText("☠️ ESPOROS!", player.x, player.y - 70, 0xa3be8c);

    await new Promise(r => setTimeout(r, 380));
    setMonsterAction(0);
    setAction(0);
    charSprite.tint = 0xffffff;
    isActionExecuting = false;
    setCombatStatus("Pronto para o próximo teste de ação.");
  }

  function testMonsterDefend() {
    setCombatStatus("🛡️ Cogumelo endurece sua cúpula (Ação 6)!");
    setMonsterAction(6);
    spawnCombatText("🛡️ DEFESA", monster.x, monster.y - 65, 0x88c0d0);
  }

  function testMonsterHurt() {
    setCombatStatus("💥 Cogumelo executando animação de Tomar Dano (Ação 5)!");
    setMonsterAction(5);
    spawnCombatText("💥 DANO", monster.x, monster.y - 65, 0xff5555);
  }

  function testMonsterDead() {
    setCombatStatus("💀 Cogumelo derrotado e caído no chão (Ação 4)! Toque em 'Resetar Poses' para levantar.");
    setMonsterAction(4);
    spawnCombatText("💀 CAÍDO", monster.x, monster.y - 35, 0xff5555);
  }

  // Sparring em Loop (Duelo Contínuo sem interrupções)
  function stopSparring() {
    sparringLoopActive = false;
    if (sparringTimer) {
      clearTimeout(sparringTimer);
      sparringTimer = null;
    }
    const btnSpar = document.getElementById("btn-combat-sparring");
    if (btnSpar) btnSpar.classList.remove("active");
  }

  function toggleSparring() {
    sparringLoopActive = !sparringLoopActive;
    const btnSpar = document.getElementById("btn-combat-sparring");
    if (btnSpar) btnSpar.classList.toggle("active", sparringLoopActive);

    if (sparringLoopActive) {
      setCombatStatus("🔄 Sparring Contínuo ATIVADO! Trocando golpes em loop...");
      sparringStep = 0;
      runSparringStep();
    } else {
      stopSparring();
      resetCombatPoses();
    }
  }

  async function runSparringStep() {
    if (!sparringLoopActive || !isCombatTesting) return;

    if (sparringStep === 0) {
      await testPlayerAttack();
    } else if (sparringStep === 1) {
      await testMonsterAttack();
    } else if (sparringStep === 2) {
      await testPlayerSkill();
    } else if (sparringStep === 3) {
      await testMonsterSkill();
    } else if (sparringStep === 4) {
      await testPlayerUltimate();
    } else if (sparringStep === 5) {
      await testMonsterAttack();
    }

    sparringStep = (sparringStep + 1) % 6;

    if (sparringLoopActive && isCombatTesting) {
      sparringTimer = setTimeout(() => {
        runSparringStep();
      }, 700);
    }
  }

  // 14. Game Loop Principal
  let enableTransparency = true;
  let fpsTimer = 0;
  let frameCount = 0;
  const fpsDisplay = document.getElementById("pill-fps");

  app.ticker.add((delta) => {
    const deltaSeconds = delta / 60;

    // FPS Counter
    fpsTimer += deltaSeconds;
    frameCount++;
    if (fpsTimer >= 0.5) {
      const fps = Math.round(frameCount / fpsTimer);
      fpsDisplay.innerText = `${fps} FPS`;
      fpsTimer = 0;
      frameCount = 0;
    }

    // Se estiver em modo de teste de combate no mapa
    if (isCombatTesting) {
      updatePlayerVisual(deltaSeconds);
      updateMonsterVisual(deltaSeconds);
      updateCombatTexts(deltaSeconds);
      return;
    }

    // 1. Movimento pelo Joystick
    if (joystickActive) {
      const moveDist = player.speed * deltaSeconds;
      movePlayer(joyVectorX * moveDist, joyVectorY * moveDist);
      updateHUD();
    }
    // 2. Movimento pelo Clique no Mapa (Target Point)
    else if (player.targetX !== null && player.targetY !== null) {
      if (pendingBattleMonster && Math.hypot(player.x - 1080, player.y - 950) <= 90) {
        const mon = pendingBattleMonster;
        pendingBattleMonster = null;
        player.targetX = null;
        player.targetY = null;
        targetMarker.visible = false;
        startBattle(mon);
        return;
      }
      const dx = player.targetX - player.x;
      const dy = player.targetY - player.y;
      const dist = Math.hypot(dx, dy);

      if (dist < 4) {
        player.x = player.targetX;
        player.y = player.targetY;
        player.targetX = null;
        player.targetY = null;
        targetMarker.visible = false;
        playerContainer.x = player.x;
        playerContainer.y = player.y;
        setAction(0); // Chegou -> Stand
      } else {
        const moveDist = player.speed * deltaSeconds;
        const ratio = Math.min(1, moveDist / dist);
        const hitWall = movePlayer(dx * ratio, dy * ratio);

        // Se encontrou obstáculo e não consegue avançar, parar
        if (hitWall) {
          const newDist = Math.hypot(player.targetX - player.x, player.targetY - player.y);
          if (Math.abs(newDist - dist) < 0.1) {
            player.targetX = null;
            player.targetY = null;
            targetMarker.visible = false;
            setAction(0);
          }
        }

        // Atualizar direção dinamicamente
        const currentDir = calculateDirection(dx, dy);
        if (currentDir !== player.dir) {
          setDirection(currentDir);
        }
      }
      updateHUD();
    }

    // 3. Animação do Marcador de Destino
    if (targetMarker.visible) {
      targetPulseTimer += deltaSeconds * 4;
      targetMarker.clear();
      const radius = 8 + Math.sin(targetPulseTimer) * 3;
      const alpha = 0.7 + Math.sin(targetPulseTimer) * 0.3;
      targetMarker.lineStyle(2, 0x88c0d0, alpha);
      targetMarker.drawCircle(0, 0, radius);
      targetMarker.beginFill(0xebcb8b, alpha);
      targetMarker.drawCircle(0, 0, 3);
      targetMarker.endFill();
    }

    // 3.8 Animação e Detecção de Portais de Teleporte
    if (portalsContainer && portalsContainer.children.length > 0) {
      portalPulseTimer += deltaSeconds * 3;
      portalsContainer.children.forEach(pg => {
        const glow = pg.getChildByName("glow");
        const outerRing = pg.getChildByName("outerRing");
        const innerRing = pg.getChildByName("innerRing");
        const innerCore = pg.getChildByName("innerCore");
        const labelContainer = pg.getChildByName("labelContainer");

        if (glow) glow.alpha = 0.25 + Math.sin(portalPulseTimer) * 0.15;
        if (outerRing) {
          outerRing.scale.set(1.0 + Math.sin(portalPulseTimer * 1.5) * 0.05);
          outerRing.rotation += deltaSeconds * 0.7;
        }
        if (innerRing) {
          innerRing.scale.set(1.0 + Math.cos(portalPulseTimer * 1.8) * 0.06);
          innerRing.rotation -= deltaSeconds * 1.1;
        }
        if (innerCore) innerCore.alpha = 0.40 + Math.cos(portalPulseTimer * 2) * 0.20;
        if (labelContainer) labelContainer.y = -36 + Math.sin(portalPulseTimer * 2.2) * 3;
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

    // 4. Transparência Dinâmica dos Telhados e Árvores (Máscaras de Sobreposição)
    let anyOccluded = false;
    if (enableTransparency) {
      const pLeft = player.x - 25;
      const pRight = player.x + 25;
      const pTop = player.y - 85;
      const pBottom = player.y;

      for (const item of maskSprites) {
        const s = item.sprite;
        const mLeft = s.x;
        const mRight = s.x + s.width;
        const mTop = s.y;
        const mBottom = s.y + s.height;

        // Bounding box overlap 2.5D
        const isOccluded = (pRight >= mLeft && pLeft <= mRight && pBottom >= mTop && pTop <= mBottom);
        if (isOccluded) anyOccluded = true;
        const targetAlpha = isOccluded ? 0.35 : 1.0;
        s.alpha += (targetAlpha - s.alpha) * 0.25;
      }
    }
    drawerOccluded.innerText = anyOccluded ? "SIM (Transparente 35%)" : "NÃO (Visível 100%)";
    drawerOccluded.style.color = anyOccluded ? "#ebcb8b" : "#88c0d0";

    // Z-Ordering dinâmico de entidades no mundo 2.5D
    playerContainer.zIndex = Math.round(player.y);
    entitiesContainer.sortChildren();

    updatePlayerVisual(deltaSeconds);
    updateMonsterVisual(deltaSeconds);
    updateCombatTexts(deltaSeconds);
    updateCamera();
  });

  // 15. Controles Mobile & Drawer
  const drawer = document.getElementById("debug-drawer");
  const backdrop = document.getElementById("drawer-backdrop");
  const btnToggleMenu = document.getElementById("btn-toggle-menu");
  const btnCloseDrawer = document.getElementById("btn-close-drawer");

  function openDrawer() {
    drawer.classList.remove("drawer-closed");
    backdrop.classList.remove("hidden");
  }

  function closeDrawer() {
    drawer.classList.add("drawer-closed");
    backdrop.classList.add("hidden");
  }

  btnToggleMenu.onclick = openDrawer;
  btnCloseDrawer.onclick = closeDrawer;
  backdrop.onclick = closeDrawer;

  // Botões de Ação Mobile
  document.getElementById("btn-act-attack").onclick = () => {
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;
    setAction(3); // Golpe / Ataque Físico
  };

  document.getElementById("btn-act-cast").onclick = () => {
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;
    setAction(7); // Magia / Conjuração
  };

  document.getElementById("btn-act-run").onclick = () => {
    setAction(2); // Correr
  };

  document.getElementById("btn-act-defense").onclick = () => {
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;
    setAction(6); // Defesa
  };

  document.getElementById("btn-act-stop").onclick = () => {
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;
    setAction(0); // Stand
  };

  const btnHurt = document.getElementById("btn-act-hurt");
  if (btnHurt) {
    btnHurt.onclick = () => {
      player.targetX = null;
      player.targetY = null;
      targetMarker.visible = false;
      setAction(5); // Tomando Dano (Ação 5)
    };
  }

  const btnDead = document.getElementById("btn-act-dead");
  if (btnDead) {
    btnDead.onclick = () => {
      player.targetX = null;
      player.targetY = null;
      targetMarker.visible = false;
      setAction(4); // Derrotado / Caído (Ação 4)
    };
  }

  const btnUlt = document.getElementById("btn-act-ultimate");
  if (btnUlt) {
    btnUlt.onclick = () => {
      player.targetX = null;
      player.targetY = null;
      targetMarker.visible = false;
      setAction(10); // Habilidade Suprema (Ação 10: 32 frames!)
    };
  }

  // Botões de Seleção de Modelo de Personagem
  document.querySelectorAll(".model-btn").forEach(btn => {
    btn.onclick = async () => {
      const model = btn.dataset.model;
      await setCharacterModel(model);
    };
  });

  // Botões de Teste de Todas as Ações (0 a 10) no Drawer
  document.querySelectorAll(".action-btn-test").forEach(btn => {
    btn.onclick = () => {
      const act = parseInt(btn.dataset.action);
      if (act !== 1 && act !== 2) {
        player.targetX = null;
        player.targetY = null;
        targetMarker.visible = false;
      }
      setAction(act);
    };
  });

  document.querySelectorAll(".dir-btn[data-dir]").forEach(btn => {
    btn.onclick = () => setDirection(parseInt(btn.dataset.dir));
  });

  // Botões de Zoom Mobile
  const zoomVal = document.getElementById("zoom-val");
  const zoomSlider = document.getElementById("zoom-slider");

  function applyZoom(newZoom) {
    zoomLevel = Math.max(0.5, Math.min(2.0, parseFloat(newZoom.toFixed(1))));
    zoomSlider.value = zoomLevel;
    zoomVal.innerText = `${zoomLevel}x`;
    updateCamera();
  }

  document.getElementById("btn-zoom-in").onclick = () => applyZoom(zoomLevel + 0.15);
  document.getElementById("btn-zoom-out").onclick = () => applyZoom(zoomLevel - 0.15);
  zoomSlider.oninput = (e) => applyZoom(parseFloat(e.target.value));

  // Zoom pelo Mouse Wheel (Desktop)
  window.addEventListener("wheel", (e) => {
    applyZoom(e.deltaY < 0 ? zoomLevel + 0.1 : zoomLevel - 0.1);
  }, { passive: true });

  // Controle de Velocidade no Drawer
  const speedVal = document.getElementById("speed-val");
  const speedSlider = document.getElementById("speed-slider");
  if (speedSlider) {
    speedSlider.oninput = (e) => {
      const spd = parseInt(e.target.value);
      player.speed = spd;
      if (speedVal) speedVal.innerText = `${spd} px/s`;
    };
  }

  // Teleporte helper
  function teleportTo(x, y) {
    player.x = x;
    player.y = y;
    player.targetX = null;
    player.targetY = null;
    targetMarker.visible = false;
    playerContainer.x = x;
    playerContainer.y = y;
    setAction(0);
    updateCamera();
    updateHUD();
  }

  document.getElementById("btn-center").onclick = () => teleportTo(1000, 1000);
  document.getElementById("tp-plaza").onclick = () => teleportTo(1000, 1000);
  document.getElementById("tp-tree").onclick = () => teleportTo(930, 1080);
  document.getElementById("tp-wall").onclick = () => teleportTo(1000, 1110);
  document.getElementById("tp-bridge").onclick = () => teleportTo(389, 580);

  // Camadas e Opções
  document.getElementById("chk-camera").onchange = (e) => {
    cameraFollow = e.target.checked;
  };

  document.getElementById("chk-npcs").onchange = (e) => {
    npcList.forEach(grp => grp.visible = e.target.checked);
  };

  // Fechar diálogo de NPC
  const closeNpcDlg = () => {
    const dlg = document.getElementById("npc-dialog");
    if (dlg) dlg.classList.add("hidden");
  };
  const btnCloseDlg = document.getElementById("btn-close-npc-dialog");
  if (btnCloseDlg) btnCloseDlg.onclick = closeNpcDlg;
  const btnAckDlg = document.getElementById("btn-ack-npc-dialog");
  if (btnAckDlg) btnAckDlg.onclick = closeNpcDlg;

  document.getElementById("chk-collision").onchange = (e) => {
    colOverlaySprite.visible = e.target.checked;
  };

  document.getElementById("chk-transparency").onchange = (e) => {
    enableTransparency = e.target.checked;
    if (!enableTransparency) {
      maskSprites.forEach(m => m.sprite.alpha = 1.0);
    }
  };

  // Botões do Painel de Teste de Combate
  const btnCloseCombat = document.getElementById("btn-close-combat-test");
  if (btnCloseCombat) btnCloseCombat.onclick = closeCombatTest;

  const btnPAtk = document.getElementById("test-p-attack");
  if (btnPAtk) btnPAtk.onclick = testPlayerAttack;
  const btnPSkl = document.getElementById("test-p-skill");
  if (btnPSkl) btnPSkl.onclick = testPlayerSkill;
  const btnPUlt = document.getElementById("test-p-ultimate");
  if (btnPUlt) btnPUlt.onclick = testPlayerUltimate;
  const btnPDef = document.getElementById("test-p-defend");
  if (btnPDef) btnPDef.onclick = testPlayerDefend;
  const btnPHrt = document.getElementById("test-p-hurt");
  if (btnPHrt) btnPHrt.onclick = testPlayerHurt;
  const btnPDed = document.getElementById("test-p-dead");
  if (btnPDed) btnPDed.onclick = testPlayerDead;

  const btnMAtk = document.getElementById("test-m-attack");
  if (btnMAtk) btnMAtk.onclick = testMonsterAttack;
  const btnMSkl = document.getElementById("test-m-skill");
  if (btnMSkl) btnMSkl.onclick = testMonsterSkill;
  const btnMDef = document.getElementById("test-m-defend");
  if (btnMDef) btnMDef.onclick = testMonsterDefend;
  const btnMHrt = document.getElementById("test-m-hurt");
  if (btnMHrt) btnMHrt.onclick = testMonsterHurt;
  const btnMDed = document.getElementById("test-m-dead");
  if (btnMDed) btnMDed.onclick = testMonsterDead;

  const btnSpar = document.getElementById("btn-combat-sparring");
  if (btnSpar) btnSpar.onclick = toggleSparring;
  const btnResetCombat = document.getElementById("btn-combat-reset");
  if (btnResetCombat) btnResetCombat.onclick = resetCombatPoses;

  const btnDrawerBattle = document.getElementById("btn-drawer-battle");
  if (btnDrawerBattle) {
    btnDrawerBattle.onclick = () => {
      closeDrawer();
      openCombatTest();
    };
  }

  // Inicializar com o Guerreiro Evoluído (Tier 2 - Ações 0 a 10)
  await setCharacterModel("PC_MALE_000011");

  updateHUD();
  updateCamera();

  // ==========================================
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

  // Expor para debug e inspeção
  window.game = {
    switchMap,
    movePlayerTo,
    movePlayer,
    openWorldMapModal,
    mapsCatalog,
    currentMapId: () => currentMapId,
    setMapMonster,
    openClassesModal,
    openMonstersModal,
    openMountsModal,
    openNpcsModal,
    mountsList,
    npcsList,
    player,
    monster,
    charSprite,
    playerContainer,
    mapMonsterSprite,
    mapMonsterGroup,
    isWalkable,
    canStand,
    teleportTo,
    setCharacterModel,
    maskSprites,
    npcsData,
    npcList,
    showNPCDialog,
    openCombatTest,
    closeCombatTest,
    isCombatTesting: () => isCombatTesting,
    testPlayerAttack,
    testPlayerSkill,
    playSkillVFX,
    executeSkill,
    openSkillsModal,
    testPlayerUltimate,
    testMonsterAttack,
    testMonsterSkill,
    toggleSparring
  };

  
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

  // Controles da Barra Flutuante de Teste de Habilidade / VFX
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
      }
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
                ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? (
                  (item.is_fly_mount || (item.model_id && item.model_id.startsWith("equip_fly_")))
                    ? `<span class="equipment-slot-tag" style="background: rgba(180, 142, 173, 0.25); border: 1px solid #b48ead; color: #d8bee5;">🧹 Montaria Voadora</span>`
                    : `<span class="equipment-slot-tag" style="background: rgba(136, 192, 208, 0.25); border: 1px solid #88c0d0; color: #88c0d0;">🪽 Asa Mística</span>`
                ) : `<span class="equipment-slot-tag">${item.position_name}</span>`}
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
            ${item.category_group === "weapons" ? `
              <button class="btn-weapon-equip ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'active' : ''}" data-equip-id="${item.id}" title="${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? 'Clique para desempunhar' : 'Clique para empunhar na mão do personagem'}">
                ${playerEquippedWeapon && playerEquippedWeapon.id === item.id ? '⚔️ Equipado' : '🖐️ Empunhar'}
              </button>
            ` : ''}
            ${(item.type === "wing" || item.category_group === "wings" || item.position === 22) ? (() => {
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
            })() : ''}
            ${(item.category_group === "wings_costumes" || item.position === 21) ? `
              <button class="btn-costume-equip ${playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id) ? 'active' : ''}" data-costume-id="${item.id}" title="${playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id) ? 'Clique para remover moda' : 'Clique para provar e vestir a skin no personagem'}">
                ${playerEquippedCostume && String(playerEquippedCostume.id) === String(item.id) ? '👗 Vestindo' : '✨ Provar Traje'}
              </button>
            ` : ''}
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
    equipmentGrid.querySelectorAll(".btn-weapon-equip").forEach(btn => {
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
    });

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
  }

  // Restaurar arma empunhada salva ou equipar inicial
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
  }

  console.log("Magic Campus Mobile Engine inicializado com sucesso!");
  window.switchMap = switchMap;
  window.player = player;
  window.maskSprites = maskSprites;
  window.getCurrentMapPortals = () => currentMapPortals;
}

window.onload = initGame;