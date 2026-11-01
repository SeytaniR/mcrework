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

  // 2. Carregar Metadados do Mapa e Monstro
  const [npcsData, masksData, colArrayBuffer, monsterManifest] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer()),
    fetch("assets/monsters/mushroom/monster_manifest.json").then(r => r.json())
  ]);

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

  // Sprite animado do Monstro no Mapa (Idle 0-0)
  const mapMonsterAnimFrames = monsterManifest.animations["0-0"].map(f => PIXI.Texture.from(f.file));
  const mapMonsterSprite = new PIXI.AnimatedSprite(mapMonsterAnimFrames);
  mapMonsterSprite.animationSpeed = 0.08;
  mapMonsterSprite.play();
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
  mapMonsterName.y = - Math.round(monsterManifest.height * 0.70) - 4;
  mapMonsterGroup.addChild(mapMonsterName);

  // Interação de Clique/Toque no Monstro para Iniciar Batalha
  let pendingBattleMonster = null;
  mapMonsterGroup.eventMode = "static";
  mapMonsterGroup.cursor = "pointer";
  mapMonsterGroup.on("pointerdown", (e) => {
    e.stopPropagation();
    const dist = Math.hypot(player.x - 1080, player.y - 950);
    if (dist <= 110) {
      startBattle("mushroom");
    } else {
      pendingBattleMonster = "mushroom";
      movePlayerTo(1040, 950);
    }
  });

  entitiesContainer.addChild(mapMonsterGroup);

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

  async function setCharacterModel(modelId) {
    currentModel = modelId;
    playerName.text = modelLabels[modelId] || "Personagem";
    console.log(`Carregando animações do modelo ${modelId}...`);
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
    console.log(`Modelo ${modelId} pronto com ${Object.keys(activeManifest).length} animações!`);

    // Atualizar visibilidade dos botões de ações 8, 9, 10 conforme disponibilidade no modelo
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
    posDisplay.innerText = `${px}, ${py}`;
    dirDisplay.innerText = dirNames[player.dir] || player.dir;

    drawerPos.innerText = `X: ${px} | Y: ${py}`;
    drawerDir.innerText = dirNames[player.dir] || player.dir;
    const animKey = `${player.dir}-${player.action}`;
    const totalFrames = activeManifest[animKey]?.length || 1;
    drawerAnim.innerText = `${animKey} [${player.frameIdx + 1}/${totalFrames}] - ${actionNames[player.action] || 'Ação'}`;

    const walkable = canStand(player.x, player.y);
    drawerWalkable.innerText = walkable ? "LIVRE (Walkable)" : "BLOQUEADO!";
    drawerWalkable.style.color = walkable ? "#a3be8c" : "#bf616a";
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
    let animFrames = activeManifest[animKey];

    if (!animFrames || animFrames.length === 0) {
      animFrames = activeManifest[`${player.dir}-0`] || activeManifest["0-0"];
    }

    if (!animFrames || animFrames.length === 0) return;

    player.frameTimer += deltaSeconds;
    if (player.frameTimer >= player.frameDuration) {
      player.frameTimer = 0;
      player.frameIdx = (player.frameIdx + 1) % animFrames.length;

      // Ação 4 (Morto): trava no chão
      if (player.action === 4) {
        player.frameIdx = 0;
      }
      // Ações pontuais (3: Ataque, 5: Dano, 6: Defesa, 7: Magia): ao completar voltam a Parado (0)
      else if (player.action >= 3 && player.frameIdx === 0) {
        setAction(0);
        return;
      }
      updateHUD();
    }

    const currentFrameData = animFrames[player.frameIdx % animFrames.length];
    const tex = textureCache[currentFrameData.file];
    if (tex) {
      charSprite.texture = tex;
      charSprite.anchor.set(0.5, 110 / 150);
      charSprite.position.set(0, 0);
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

  // 13.5 Sistema de Batalha em Turnos (Simulador de Combate)
  let isBattleActive = false;
  let battleTurn = "player"; // "player" | "monster" | "animating"
  let isAutoBattle = false;
  let battleShakeTimer = 0;
  let battleShakeIntensity = 0;

  const playerCombat = {
    name: "Guerreiro Evoluído",
    maxHp: 1000,
    hp: 1000,
    maxSp: 250,
    sp: 250,
    isDefending: false,
    dir: 1, // Facing Southeast em direção ao monstro
    action: 0,
    frameIdx: 0,
    frameTimer: 0,
    frameDuration: 0.08,
    offsetX: 0,
    offsetY: 0
  };

  const monsterCombat = {
    name: "Cogumelo Selvagem",
    level: 5,
    maxHp: 650,
    hp: 650,
    isDefending: false,
    dir: 7, // Facing Southwest em direção ao jogador
    action: 0,
    frameIdx: 0,
    frameTimer: 0,
    frameDuration: 0.08,
    offsetX: 0,
    offsetY: 0
  };

  // Container PixiJS da Batalha (renderizado na camada superior do stage)
  const battleContainer = new PIXI.Container();
  battleContainer.visible = false;
  app.stage.addChild(battleContainer);

  const battleDimBg = new PIXI.Graphics();
  battleContainer.addChild(battleDimBg);

  const battleArenaFloor = new PIXI.Graphics();
  battleContainer.addChild(battleArenaFloor);

  const battlePlayerGroup = new PIXI.Container();
  const battleMonsterGroup = new PIXI.Container();
  battleContainer.addChild(battlePlayerGroup);
  battleContainer.addChild(battleMonsterGroup);

  const floatingTextContainer = new PIXI.Container();
  battleContainer.addChild(floatingTextContainer);

  // Sombra e Sprite do Jogador na Batalha
  const btlPlayerShadow = new PIXI.Graphics();
  btlPlayerShadow.beginFill(0x000000, 0.45);
  btlPlayerShadow.drawEllipse(0, 0, 24, 10);
  btlPlayerShadow.endFill();
  battlePlayerGroup.addChild(btlPlayerShadow);

  const battlePlayerSprite = new PIXI.Sprite();
  battlePlayerSprite.anchor.set(0.5, 110 / 150);
  battlePlayerSprite.scale.set(0.95);
  battlePlayerGroup.addChild(battlePlayerSprite);

  // Sombra e Sprite do Monstro na Batalha
  const btlMonsterShadow = new PIXI.Graphics();
  btlMonsterShadow.beginFill(0x000000, 0.45);
  btlMonsterShadow.drawEllipse(0, 0, 26, 11);
  btlMonsterShadow.endFill();
  battleMonsterGroup.addChild(btlMonsterShadow);

  const battleMonsterSprite = new PIXI.Sprite();
  battleMonsterSprite.anchor.set(0.5, 1.0);
  battleMonsterSprite.scale.set(1.15);
  battleMonsterGroup.addChild(battleMonsterSprite);

  // Textos de Dano e Cura Flutuantes
  const floatingTexts = [];

  function spawnDamageText(text, x, y, color = 0xffe066) {
    const txt = new PIXI.Text(text, {
      fontFamily: "system-ui, -apple-system, sans-serif",
      fontSize: 22,
      fontWeight: "900",
      fill: color,
      stroke: 0x000000,
      strokeThickness: 4,
      align: "center",
      dropShadow: true,
      dropShadowColor: 0x000000,
      dropShadowDistance: 2
    });
    txt.anchor.set(0.5, 1.0);
    txt.x = x;
    txt.y = y;
    floatingTextContainer.addChild(txt);
    floatingTexts.push({
      sprite: txt,
      life: 0.9,
      maxLife: 0.9,
      vy: -55
    });
  }

  // Elementos do DOM da Batalha
  const btlPlayerName = document.getElementById("btl-player-name");
  const btlPlayerHpBar = document.getElementById("battle-player-hp-bar");
  const btlPlayerHpText = document.getElementById("battle-player-hp-text");
  const btlPlayerSpBar = document.getElementById("battle-player-sp-bar");
  const btlPlayerSpText = document.getElementById("battle-player-sp-text");
  const battleTurnBadge = document.getElementById("battle-turn-badge");
  const battleTurnText = document.getElementById("battle-turn-text");
  const btlMonsterName = document.getElementById("btl-monster-name");
  const btlMonsterHpBar = document.getElementById("battle-monster-hp-bar");
  const btlMonsterHpText = document.getElementById("battle-monster-hp-text");
  const battleActionText = document.getElementById("battle-action-text");
  const battleOverlay = document.getElementById("battle-overlay");
  const battleResultModal = document.getElementById("battle-result-modal");
  const battleResultTitle = document.getElementById("battle-result-title");
  const battleResultDesc = document.getElementById("battle-result-desc");
  const btnBattleFinish = document.getElementById("btn-battle-finish");
  const btnBtlAttack = document.getElementById("btn-btl-attack");
  const btnBtlSkill = document.getElementById("btn-btl-skill");
  const btnBtlUltimate = document.getElementById("btn-btl-ultimate");
  const btnBtlDefend = document.getElementById("btn-btl-defend");
  const btnBtlAuto = document.getElementById("btn-btl-auto");
  const btnBtlFlee = document.getElementById("btn-btl-flee");

  function setBattleBanner(msg) {
    if (battleActionText) battleActionText.textContent = msg;
  }

  function updateBattleHUD() {
    if (!btlPlayerHpBar) return;
    const pPct = Math.max(0, Math.min(100, (playerCombat.hp / playerCombat.maxHp) * 100));
    const sPct = Math.max(0, Math.min(100, (playerCombat.sp / playerCombat.maxSp) * 100));
    btlPlayerHpBar.style.width = `${pPct}%`;
    btlPlayerHpText.textContent = `${playerCombat.hp} / ${playerCombat.maxHp}`;
    btlPlayerSpBar.style.width = `${sPct}%`;
    btlPlayerSpText.textContent = `${playerCombat.sp} / ${playerCombat.maxSp}`;
    btlPlayerName.textContent = playerCombat.name;

    const mPct = Math.max(0, Math.min(100, (monsterCombat.hp / monsterCombat.maxHp) * 100));
    btlMonsterHpBar.style.width = `${mPct}%`;
    btlMonsterHpText.textContent = `${monsterCombat.hp} / ${monsterCombat.maxHp}`;
    btlMonsterName.textContent = monsterCombat.name;

    if (battleTurn === "player") {
      battleTurnBadge.className = "battle-turn-badge turn-player";
      battleTurnText.textContent = "SEU TURNO";
    } else if (battleTurn === "monster") {
      battleTurnBadge.className = "battle-turn-badge turn-monster";
      battleTurnText.textContent = "TURNO DO MONSTRO";
    } else {
      battleTurnBadge.className = "battle-turn-badge turn-animating";
      battleTurnText.textContent = "EXECUTANDO...";
    }

    const isPlayerTurn = (battleTurn === "player");
    document.querySelectorAll(".btl-btn").forEach(btn => {
      if (btn.id === "btn-btl-auto") return;
      btn.style.opacity = isPlayerTurn ? "1.0" : "0.45";
      btn.style.pointerEvents = isPlayerTurn ? "auto" : "none";
    });

    if (btnBtlSkill && isPlayerTurn && playerCombat.sp < 40) {
      btnBtlSkill.style.opacity = "0.4";
    }
    if (btnBtlUltimate && isPlayerTurn && playerCombat.sp < 80) {
      btnBtlUltimate.style.opacity = "0.4";
    }
  }

  function updateBattleVisuals(deltaSeconds) {
    const sw = app.screen.width;
    const sh = app.screen.height;

    // Fundo escuro imersivo
    battleDimBg.clear();
    battleDimBg.beginFill(0x070b14, 0.82);
    battleDimBg.drawRect(0, 0, sw, sh);
    battleDimBg.endFill();

    const arenaX = sw / 2;
    const arenaY = sh * 0.54;
    const arenaRadiusX = Math.min(sw * 0.42, 280);
    const arenaRadiusY = Math.min(sh * 0.18, 90);

    battleArenaFloor.clear();
    battleArenaFloor.beginFill(0x131a29, 0.75);
    battleArenaFloor.drawEllipse(arenaX, arenaY, arenaRadiusX, arenaRadiusY);
    battleArenaFloor.endFill();

    battleArenaFloor.lineStyle(2, 0x5e81ac, 0.65);
    battleArenaFloor.drawEllipse(arenaX, arenaY, arenaRadiusX, arenaRadiusY);

    battleArenaFloor.lineStyle(1.5, 0x88c0d0, 0.45);
    battleArenaFloor.drawEllipse(arenaX, arenaY, arenaRadiusX * 0.68, arenaRadiusY * 0.68);
    battleArenaFloor.drawEllipse(arenaX, arenaY, arenaRadiusX * 0.35, arenaRadiusY * 0.35);

    let shakeX = 0;
    let shakeY = 0;
    if (battleShakeTimer > 0) {
      battleShakeTimer -= deltaSeconds;
      shakeX = (Math.random() - 0.5) * battleShakeIntensity;
      shakeY = (Math.random() - 0.5) * battleShakeIntensity;
    }

    const pBaseX = arenaX - arenaRadiusX * 0.52 + shakeX;
    const pBaseY = arenaY + 8 + shakeY;
    const mBaseX = arenaX + arenaRadiusX * 0.52 + shakeX;
    const mBaseY = arenaY + 8 + shakeY;

    battlePlayerGroup.x = pBaseX + playerCombat.offsetX;
    battlePlayerGroup.y = pBaseY + playerCombat.offsetY;

    battleMonsterGroup.x = mBaseX + monsterCombat.offsetX;
    battleMonsterGroup.y = mBaseY + monsterCombat.offsetY;

    // Sprite do Jogador
    const pAnimKey = `${playerCombat.dir}-${playerCombat.action}`;
    let pFrames = activeManifest[pAnimKey] || activeManifest[`${playerCombat.dir}-0`] || activeManifest["0-0"];
    if (pFrames && pFrames.length > 0) {
      playerCombat.frameTimer += deltaSeconds;
      if (playerCombat.frameTimer >= playerCombat.frameDuration) {
        playerCombat.frameTimer = 0;
        playerCombat.frameIdx = (playerCombat.frameIdx + 1) % pFrames.length;
        if (playerCombat.action === 4) {
          playerCombat.frameIdx = pFrames.length - 1;
        }
      }
      const pFData = pFrames[playerCombat.frameIdx % pFrames.length];
      const pTex = textureCache[pFData.file];
      if (pTex) battlePlayerSprite.texture = pTex;
    }

    // Sprite do Monstro
    const mAnimKey = `${monsterCombat.dir}-${monsterCombat.action}`;
    let mFrames = monsterManifest.animations[mAnimKey] || monsterManifest.animations[`${monsterCombat.dir}-0`] || monsterManifest.animations["0-0"];
    if (mFrames && mFrames.length > 0) {
      monsterCombat.frameTimer += deltaSeconds;
      if (monsterCombat.frameTimer >= monsterCombat.frameDuration) {
        monsterCombat.frameTimer = 0;
        monsterCombat.frameIdx = (monsterCombat.frameIdx + 1) % mFrames.length;
        if (monsterCombat.action === 4) {
          monsterCombat.frameIdx = mFrames.length - 1;
        }
      }
      const mFData = mFrames[monsterCombat.frameIdx % mFrames.length];
      const mTex = PIXI.Texture.from(mFData.file);
      if (mTex) battleMonsterSprite.texture = mTex;
    }

    // Textos Flutuantes
    for (let i = floatingTexts.length - 1; i >= 0; i--) {
      const ft = floatingTexts[i];
      ft.life -= deltaSeconds;
      ft.sprite.y += ft.vy * deltaSeconds;
      ft.sprite.alpha = Math.max(0, ft.life / ft.maxLife);
      if (ft.life <= 0) {
        floatingTextContainer.removeChild(ft.sprite);
        floatingTexts.splice(i, 1);
      }
    }
  }

  // Executores de Ação
  async function executePlayerAttack() {
    if (battleTurn !== "player" || !isBattleActive) return;
    battleTurn = "animating";
    updateBattleHUD();
    setBattleBanner("⚔️ O Guerreiro avança com um golpe cortante!");

    playerCombat.action = 3; // Attack
    playerCombat.frameIdx = 0;
    playerCombat.offsetX = 35;

    await new Promise(r => setTimeout(r, 260));

    let damage = Math.floor(130 + Math.random() * 50);
    if (monsterCombat.isDefending) {
      damage = Math.floor(damage * 0.5);
      monsterCombat.isDefending = false;
      spawnDamageText(`🛡️ BLOQUEOU! -${damage}`, battleMonsterGroup.x, battleMonsterGroup.y - 65, 0x88c0d0);
    } else {
      const isCrit = Math.random() < 0.25;
      if (isCrit) {
        damage = Math.floor(damage * 1.5);
        spawnDamageText(`💥 CRÍTICO! -${damage}`, battleMonsterGroup.x, battleMonsterGroup.y - 65, 0xff5555);
      } else {
        spawnDamageText(`-${damage}`, battleMonsterGroup.x, battleMonsterGroup.y - 65, 0xffe066);
      }
    }

    monsterCombat.hp = Math.max(0, monsterCombat.hp - damage);
    playerCombat.sp = Math.min(playerCombat.maxSp, playerCombat.sp + 15);
    spawnDamageText(`+15 SP`, battlePlayerGroup.x, battlePlayerGroup.y - 65, 0x81a1c1);

    monsterCombat.action = 5; // Hurt
    monsterCombat.frameIdx = 0;
    battleMonsterSprite.tint = 0xff6666;
    battleShakeTimer = 0.25;
    battleShakeIntensity = 6;
    updateBattleHUD();

    await new Promise(r => setTimeout(r, 280));
    playerCombat.action = 0;
    playerCombat.offsetX = 0;
    battleMonsterSprite.tint = 0xffffff;

    if (monsterCombat.hp <= 0) {
      onBattleVictory();
      return;
    }

    monsterCombat.action = 0;
    await new Promise(r => setTimeout(r, 350));
    executeMonsterTurn();
  }

  async function executePlayerSkill() {
    if (battleTurn !== "player" || !isBattleActive) return;
    if (playerCombat.sp < 40) {
      setBattleBanner("⚠️ SP insuficiente para Magia! (Requer 40 SP)");
      return;
    }
    battleTurn = "animating";
    playerCombat.sp -= 40;
    updateBattleHUD();
    setBattleBanner("🔮 O Guerreiro conjura uma rajada de energia arcana!");

    playerCombat.action = 7; // Magia / Cast
    playerCombat.frameIdx = 0;

    await new Promise(r => setTimeout(r, 350));

    let damage = Math.floor(240 + Math.random() * 70);
    if (monsterCombat.isDefending) {
      damage = Math.floor(damage * 0.5);
      monsterCombat.isDefending = false;
      spawnDamageText(`🛡️ BLOQUEOU! -${damage}`, battleMonsterGroup.x, battleMonsterGroup.y - 65, 0x88c0d0);
    } else {
      spawnDamageText(`🔮 -${damage}`, battleMonsterGroup.x, battleMonsterGroup.y - 65, 0xb48ead);
    }

    monsterCombat.hp = Math.max(0, monsterCombat.hp - damage);
    monsterCombat.action = 5;
    monsterCombat.frameIdx = 0;
    battleMonsterSprite.tint = 0xd08770;
    battleShakeTimer = 0.35;
    battleShakeIntensity = 8;
    updateBattleHUD();

    await new Promise(r => setTimeout(r, 350));
    playerCombat.action = 0;
    battleMonsterSprite.tint = 0xffffff;

    if (monsterCombat.hp <= 0) {
      onBattleVictory();
      return;
    }

    monsterCombat.action = 0;
    await new Promise(r => setTimeout(r, 350));
    executeMonsterTurn();
  }

  async function executePlayerUltimate() {
    if (battleTurn !== "player" || !isBattleActive) return;
    if (playerCombat.sp < 80) {
      setBattleBanner("⚠️ SP insuficiente para Suprema! (Requer 80 SP)");
      return;
    }
    battleTurn = "animating";
    playerCombat.sp -= 80;
    updateBattleHUD();
    setBattleBanner("⚡ HABILIDADE SUPREMA! Sequência devastadora de golpes!");

    playerCombat.action = activeManifest[`${playerCombat.dir}-10`] ? 10 : 3;
    playerCombat.frameIdx = 0;
    playerCombat.frameDuration = 0.05;
    playerCombat.offsetX = 45;

    // Hit 1
    await new Promise(r => setTimeout(r, 300));
    let hit1 = Math.floor(140 + Math.random() * 30);
    monsterCombat.hp = Math.max(0, monsterCombat.hp - hit1);
    spawnDamageText(`⚡ -${hit1}`, battleMonsterGroup.x - 15, battleMonsterGroup.y - 70, 0xebcb8b);
    battleMonsterSprite.tint = 0xebcb8b;
    battleShakeTimer = 0.2;
    battleShakeIntensity = 5;
    updateBattleHUD();

    // Hit 2
    await new Promise(r => setTimeout(r, 260));
    let hit2 = Math.floor(160 + Math.random() * 40);
    monsterCombat.hp = Math.max(0, monsterCombat.hp - hit2);
    spawnDamageText(`⚡ -${hit2}`, battleMonsterGroup.x + 15, battleMonsterGroup.y - 85, 0xebcb8b);
    battleMonsterSprite.tint = 0xbf616a;
    battleShakeTimer = 0.25;
    battleShakeIntensity = 8;
    updateBattleHUD();

    // Finisher
    await new Promise(r => setTimeout(r, 300));
    let hitFinal = Math.floor(250 + Math.random() * 70);
    monsterCombat.hp = Math.max(0, monsterCombat.hp - hitFinal);
    spawnDamageText(`💥 GOLPE FINAL! -${hitFinal}`, battleMonsterGroup.x, battleMonsterGroup.y - 100, 0xff3333);
    monsterCombat.action = 5;
    monsterCombat.frameIdx = 0;
    battleMonsterSprite.tint = 0xff2222;
    battleShakeTimer = 0.5;
    battleShakeIntensity = 15;
    updateBattleHUD();

    await new Promise(r => setTimeout(r, 450));
    playerCombat.action = 0;
    playerCombat.frameDuration = 0.08;
    playerCombat.offsetX = 0;
    battleMonsterSprite.tint = 0xffffff;

    if (monsterCombat.hp <= 0) {
      onBattleVictory();
      return;
    }

    monsterCombat.action = 0;
    await new Promise(r => setTimeout(r, 400));
    executeMonsterTurn();
  }

  async function executePlayerDefend() {
    if (battleTurn !== "player" || !isBattleActive) return;
    battleTurn = "animating";
    playerCombat.isDefending = true;
    playerCombat.sp = Math.min(playerCombat.maxSp, playerCombat.sp + 35);
    updateBattleHUD();
    setBattleBanner("🛡️ O Guerreiro assume postura defensiva! Dano reduzido em 65%.");

    playerCombat.action = 6; // Defend / Block
    playerCombat.frameIdx = 0;
    spawnDamageText(`+35 SP`, battlePlayerGroup.x, battlePlayerGroup.y - 65, 0x88c0d0);

    await new Promise(r => setTimeout(r, 650));
    executeMonsterTurn();
  }

  async function executeMonsterTurn() {
    if (!isBattleActive || monsterCombat.hp <= 0) return;
    battleTurn = "monster";
    updateBattleHUD();

    await new Promise(r => setTimeout(r, 450));

    const roll = Math.random();
    if (roll < 0.60) {
      setBattleBanner("🍄 Cogumelo Selvagem avança com uma cabeçada veloz!");
      monsterCombat.action = 3;
      monsterCombat.frameIdx = 0;
      monsterCombat.offsetX = -30;

      await new Promise(r => setTimeout(r, 260));

      let dmg = Math.floor(75 + Math.random() * 35);
      if (playerCombat.isDefending) {
        dmg = Math.floor(dmg * 0.35);
        spawnDamageText(`🛡️ DEFESA! -${dmg}`, battlePlayerGroup.x, battlePlayerGroup.y - 65, 0x88c0d0);
      } else {
        spawnDamageText(`-${dmg}`, battlePlayerGroup.x, battlePlayerGroup.y - 65, 0xbf616a);
      }

      playerCombat.hp = Math.max(0, playerCombat.hp - dmg);
      playerCombat.action = playerCombat.isDefending ? 6 : 5;
      playerCombat.frameIdx = 0;
      battlePlayerSprite.tint = 0xff7777;
      battleShakeTimer = 0.2;
      battleShakeIntensity = 5;
      updateBattleHUD();

      await new Promise(r => setTimeout(r, 320));
      monsterCombat.action = 0;
      monsterCombat.offsetX = 0;
      battlePlayerSprite.tint = 0xffffff;
      playerCombat.action = 0;
    } else if (roll < 0.88) {
      setBattleBanner("🍄 Cogumelo Selvagem espalha uma nuvem venenosa de esporos!");
      monsterCombat.action = 7;
      monsterCombat.frameIdx = 0;

      await new Promise(r => setTimeout(r, 350));

      let dmg = Math.floor(110 + Math.random() * 45);
      if (playerCombat.isDefending) {
        dmg = Math.floor(dmg * 0.40);
        spawnDamageText(`🛡️ DEFESA! -${dmg}`, battlePlayerGroup.x, battlePlayerGroup.y - 65, 0xa3be8c);
      } else {
        spawnDamageText(`☠️ ESPOROS! -${dmg}`, battlePlayerGroup.x, battlePlayerGroup.y - 65, 0xa3be8c);
      }

      playerCombat.hp = Math.max(0, playerCombat.hp - dmg);
      playerCombat.action = 5;
      playerCombat.frameIdx = 0;
      battlePlayerSprite.tint = 0xa3be8c;
      battleShakeTimer = 0.3;
      battleShakeIntensity = 7;
      updateBattleHUD();

      await new Promise(r => setTimeout(r, 350));
      monsterCombat.action = 0;
      battlePlayerSprite.tint = 0xffffff;
      playerCombat.action = 0;
    } else {
      setBattleBanner("🍄 Cogumelo Selvagem endurece seu chapéu para resistir ao próximo golpe!");
      monsterCombat.action = 6;
      monsterCombat.frameIdx = 0;
      monsterCombat.isDefending = true;
      spawnDamageText(`🛡️ DEFESA`, battleMonsterGroup.x, battleMonsterGroup.y - 65, 0x88c0d0);

      await new Promise(r => setTimeout(r, 600));
      monsterCombat.action = 0;
    }

    playerCombat.isDefending = false;

    if (playerCombat.hp <= 0) {
      onBattleDefeat();
      return;
    }

    battleTurn = "player";
    updateBattleHUD();
    setBattleBanner("Sua vez! Escolha seu comando.");

    if (isAutoBattle && isBattleActive) {
      setTimeout(() => {
        if (battleTurn === "player" && isBattleActive) autoBattleStep();
      }, 500);
    }
  }

  function autoBattleStep() {
    if (battleTurn !== "player" || !isBattleActive) return;
    if (playerCombat.sp >= 80) {
      executePlayerUltimate();
    } else if (playerCombat.sp >= 40) {
      executePlayerSkill();
    } else {
      executePlayerAttack();
    }
  }

  function toggleAutoBattle() {
    isAutoBattle = !isAutoBattle;
    btnBtlAuto.classList.toggle("active", isAutoBattle);
    if (isAutoBattle) {
      setBattleBanner("🤖 Modo Automático ATIVADO! Lutando continuamente...");
      if (battleTurn === "player") autoBattleStep();
    } else {
      setBattleBanner("🤖 Modo Automático DESATIVADO.");
    }
  }

  async function executePlayerFlee() {
    if (battleTurn !== "player" || !isBattleActive) return;
    battleTurn = "animating";
    updateBattleHUD();
    setBattleBanner("🏃 Tentando fugir da batalha...");

    playerCombat.dir = 6;
    playerCombat.action = 2;
    playerCombat.offsetX = -40;

    await new Promise(r => setTimeout(r, 500));

    if (Math.random() < 0.85) {
      setBattleBanner("🏃 Você conseguiu escapar com sucesso!");
      await new Promise(r => setTimeout(r, 600));
      endBattle();
    } else {
      setBattleBanner("❌ Falha ao fugir! O Cogumelo bloqueou sua passagem!");
      playerCombat.dir = 1;
      playerCombat.action = 0;
      playerCombat.offsetX = 0;
      await new Promise(r => setTimeout(r, 600));
      executeMonsterTurn();
    }
  }

  function onBattleVictory() {
    battleTurn = "animating";
    monsterCombat.action = 4;
    monsterCombat.frameIdx = 0;
    setBattleBanner("🏆 VITÓRIA! O Cogumelo Selvagem foi derrotado!");
    updateBattleHUD();

    setTimeout(() => {
      battleResultTitle.textContent = "🏆 VITÓRIA!";
      battleResultTitle.style.color = "#a3be8c";
      battleResultDesc.innerHTML = `Você derrotou o <strong>Cogumelo Selvagem</strong>!<br><span style="color: #ebcb8b;">+180 EXP obtidos</span> | <span style="color: #88c0d0;">+75 Moedas de Ouro</span>`;
      battleResultModal.style.display = "flex";
      battleResultModal.classList.remove("hidden");
    }, 700);
  }

  function onBattleDefeat() {
    battleTurn = "animating";
    playerCombat.action = 4;
    playerCombat.frameIdx = 0;
    setBattleBanner("💀 DERROTA... O Cogumelo Selvagem superou suas defesas.");
    updateBattleHUD();

    setTimeout(() => {
      battleResultTitle.textContent = "💀 DERROTA...";
      battleResultTitle.style.color = "#bf616a";
      battleResultDesc.innerHTML = `O <strong>Cogumelo Selvagem</strong> derrotou você em combate.<br>Descanse e recupere suas forças para tentar novamente!`;
      battleResultModal.style.display = "flex";
      battleResultModal.classList.remove("hidden");
    }, 700);
  }

  function startBattle(monsterId = "mushroom") {
    closeDrawer();
    closeNpcDlg();

    playerCombat.name = modelLabels[currentModel] || "Guerreiro";
    playerCombat.hp = playerCombat.maxHp;
    playerCombat.sp = playerCombat.maxSp;
    playerCombat.dir = 1;
    playerCombat.action = 0;
    playerCombat.frameIdx = 0;
    playerCombat.offsetX = 0;
    playerCombat.isDefending = false;
    battlePlayerSprite.tint = 0xffffff;

    monsterCombat.hp = monsterCombat.maxHp;
    monsterCombat.dir = 7;
    monsterCombat.action = 0;
    monsterCombat.frameIdx = 0;
    monsterCombat.offsetX = 0;
    monsterCombat.isDefending = false;
    battleMonsterSprite.tint = 0xffffff;

    floatingTexts.forEach(ft => floatingTextContainer.removeChild(ft.sprite));
    floatingTexts.length = 0;

    isBattleActive = true;
    battleTurn = "player";
    isAutoBattle = false;
    btnBtlAuto.classList.remove("active");

    battleOverlay.classList.remove("hidden");
    battleOverlay.style.display = "flex";
    battleResultModal.classList.add("hidden");
    battleResultModal.style.display = "none";
    battleContainer.visible = true;

    setBattleBanner("⚔️ A batalha começou! Selecione uma ação para atacar.");
    updateBattleHUD();
  }

  function endBattle() {
    isBattleActive = false;
    isAutoBattle = false;
    pendingBattleMonster = null;
    btnBtlAuto.classList.remove("active");
    battleOverlay.classList.add("hidden");
    battleOverlay.style.display = "none";
    battleResultModal.classList.add("hidden");
    battleResultModal.style.display = "none";
    battleContainer.visible = false;

    setAction(0);
    setDirection(0);
    updateHUD();
    updateCamera();
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

    // Se estiver em Batalha, anima a arena e pausa o mapa
    if (isBattleActive) {
      updateBattleVisuals(deltaSeconds);
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

  // Botões de Ação na Tela de Batalha
  if (btnBtlAttack) btnBtlAttack.onclick = executePlayerAttack;
  if (btnBtlSkill) btnBtlSkill.onclick = executePlayerSkill;
  if (btnBtlUltimate) btnBtlUltimate.onclick = executePlayerUltimate;
  if (btnBtlDefend) btnBtlDefend.onclick = executePlayerDefend;
  if (btnBtlAuto) btnBtlAuto.onclick = toggleAutoBattle;
  if (btnBtlFlee) btnBtlFlee.onclick = executePlayerFlee;
  if (btnBattleFinish) btnBattleFinish.onclick = endBattle;

  const btnDrawerBattle = document.getElementById("btn-drawer-battle");
  if (btnDrawerBattle) {
    btnDrawerBattle.onclick = () => {
      closeDrawer();
      startBattle("mushroom");
    };
  }

  // Inicializar com o Guerreiro Evoluído (Tier 2 - Ações 0 a 10)
  await setCharacterModel("char11");

  updateHUD();
  updateCamera();

  // Expor para debug e inspeção
  window.game = {
    player,
    isWalkable,
    canStand,
    teleportTo,
    setCharacterModel,
    maskSprites,
    npcsData,
    npcList,
    showNPCDialog,
    startBattle,
    endBattle,
    isBattleActive: () => isBattleActive,
    playerCombat,
    monsterCombat
  };

  console.log("Magic Campus Mobile Engine inicializado com sucesso!");
}

window.onload = initGame;
