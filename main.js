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
  const [npcsData, masksData, colArrayBuffer, initialMonsterMeta, initialMonsterSheet, classesCatalogData, monstersCatalogData, mountsCatalogData, npcsCatalogData] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/visual_meta.json").then(r => r.json()),
    PIXI.Assets.load("assets/monsters/mushroom/atlas.json"),
    fetch("assets/characters/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_classes: 0, classes: [] })),
    fetch("assets/monsters/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_monsters: 0, monsters: [] })),
    fetch("assets/mounts/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_mounts: 0, mounts: [] })),
    fetch("assets/npcs/catalog.json?v=1.2.1").then(r => r.json()).catch(() => ({ total_npcs: 0, npcs: [] }))
  ]);

  let monsterMeta = initialMonsterMeta;
  let monsterSheet = initialMonsterSheet;
  let currentMonsterId = "mushroom";
  let currentSpritesheet = null;
  let currentMeta = null;

  // 3. Malha de Colisão Binária (Uint8Array de 388.683 bytes, 2031x1531)
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
  }

  function canStand(x, y) {
    if (!isWalkable(x, y)) return false;
    // Pequeno raio de footprint (5px horizontal, 3px vertical) para evitar clipping
    if (!isWalkable(x - 5, y) || !isWalkable(x + 5, y)) return false;
    if (!isWalkable(x, y - 3) || !isWalkable(x, y + 3)) return false;
    return true;
  }

  function findClosestWalkable(tx, ty, maxRadius = 60) {
    if (canStand(tx, ty)) return { x: tx, y: ty };
    for (let r = 3; r <= maxRadius; r += 3) {
      for (let ang = 0; ang < Math.PI * 2; ang += Math.PI / 8) {
        const testX = tx + Math.cos(ang) * r;
        const testY = ty + Math.sin(ang) * r;
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

  const MAP_WIDTH = 2000;
  const MAP_HEIGHT = 1500;

  // Camada 2: Overlay Visual da Colisão (Inspecionável / Debug)
  const colOverlayTexture = await PIXI.Assets.load("assets/map1/collision_overlay.png");
  const colOverlaySprite = new PIXI.Sprite(colOverlayTexture);
  colOverlaySprite.visible = false;
  world.addChild(colOverlaySprite);

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
  charSprite.position.set(0, 0);
  charSprite.scale.set(0.70);
  playerContainer.addChild(charSprite);

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

  // Camada 6: Máscaras de Telhado / Árvores (Foreground / Sobreposição)
  const maskContainer = new PIXI.Container();
  world.addChild(maskContainer);

  const maskSprites = [];
  for (const maskInfo of masksData) {
    const tex = await PIXI.Assets.load(maskInfo.file);
    const mSprite = new PIXI.Sprite(tex);
    mSprite.x = maskInfo.x;
    mSprite.y = maskInfo.y;
    maskContainer.addChild(mSprite);
    maskSprites.push({ sprite: mSprite, info: maskInfo });
  }
  console.log(`Carregadas ${maskSprites.length} sobreposições de primeiro plano.`);

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

    if (isSpritesheet) {
      const tex = animFrames[player.frameIdx % animFrames.length];
      if (tex) {
        charSprite.texture = tex;
        charSprite.anchor.set(0.5, 1.0);
        charSprite.position.set(0, 0);
      }
    } else {
      const currentFrameData = animFrames[player.frameIdx % animFrames.length];
      const tex = textureCache[currentFrameData.file];
      if (tex) {
        charSprite.texture = tex;
        charSprite.anchor.set(0.5, 110 / 150);
        charSprite.position.set(0, 0);
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

    let camX = screenWidth / 2 - player.x * zoomLevel;
    let camY = screenHeight / 2 - player.y * zoomLevel;

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

    if (combatTestPanel) combatTestPanel.classList.remove("hidden");
    if (mobileActionBar) mobileActionBar.style.display = "none";
    if (joystickContainer) joystickContainer.style.display = "none";

    setCombatStatus("⚔️ Modo de Combate Ativo! Toque em uma ação abaixo ou ative o Sparring Contínuo.");
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

    await new Promise(r => setTimeout(r, 260));
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("💥 GOLPE!", monster.x, monster.y - 65, 0xffe066);

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

    await new Promise(r => setTimeout(r, 350));
    setMonsterAction(5); // Hurt do Monstro
    spawnCombatText("🔮 MAGIA!", monster.x, monster.y - 65, 0xb48ead);

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

    await new Promise(r => setTimeout(r, 280));
    spawnCombatText("⚡ COMBO!", monster.x, monster.y - 70, 0xebcb8b);

    await new Promise(r => setTimeout(r, 280));
    spawnCombatText("⚡ HIT 2!", monster.x, monster.y - 80, 0xebcb8b);

    await new Promise(r => setTimeout(r, 320));
    setMonsterAction(5);
    spawnCombatText("💥 FINALIZADOR!", monster.x, monster.y - 90, 0xff3333);

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

  // Expor para debug e inspeção
  window.game = {
    setMapMonster,
    openClassesModal,
    openMonstersModal,
    openMountsModal,
    openNpcsModal,
    mountsList,
    npcsList,
    player,
    monster,
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
    testPlayerUltimate,
    testMonsterAttack,
    testMonsterSkill,
    toggleSparring
  };

  console.log("Magic Campus Mobile Engine inicializado com sucesso!");
}

window.onload = initGame;
