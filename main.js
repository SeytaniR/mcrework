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

  // 2. Carregar Metadados do Mapa
  const [npcsData, masksData, colArrayBuffer] = await Promise.all([
    fetch("assets/map1/npcs.json").then(r => r.json()),
    fetch("assets/map1/masks.json").then(r => r.json()),
    fetch("assets/map1/collision.bin").then(r => r.arrayBuffer())
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

    // 1. Movimento pelo Joystick
    if (joystickActive) {
      const moveDist = player.speed * deltaSeconds;
      movePlayer(joyVectorX * moveDist, joyVectorY * moveDist);
      updateHUD();
    }
    // 2. Movimento pelo Clique no Mapa (Target Point)
    else if (player.targetX !== null && player.targetY !== null) {
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
    showNPCDialog
  };

  console.log("Magic Campus Mobile Engine inicializado com sucesso!");
}

window.onload = initGame;
