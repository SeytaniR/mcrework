import os, sys

BASE_DIR = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi"
MAIN_JS = os.path.join(BASE_DIR, "web", "main.js")

with open(MAIN_JS, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update renderMapPortals and add loadMapMasks definition
old_render_portals = """  function renderMapPortals(portals) {
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
  }"""

new_render_portals = """  function renderMapPortals(portals) {
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
  }"""

if old_render_portals in code:
    code = code.replace(old_render_portals, new_render_portals)
    print("Updated renderMapPortals successfully!")
else:
    print("Warning: old_render_portals not matched exactly!")

# 2. Update switchMap to load masks dynamically
old_switch_map_masks = """      // 5. Renderizar portais deste mapa
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
      }"""

new_switch_map_masks = """      // 5. Renderizar portais deste mapa
      renderMapPortals(currentMapPortals);

      // 6. Carregar dinamicamente as máscaras de transparência deste mapa
      await loadMapMasks(targetMapId);

      // 7. Atualizar HUD de Mapa
      const mapNameEl = document.querySelector(".map-name");
      if (mapNameEl) mapNameEl.textContent = `${mapMeta.name} (#${mapMeta.id})`;

      const worldCurrentLocEl = document.getElementById("worldmap-current-loc");
      if (worldCurrentLocEl) worldCurrentLocEl.textContent = `${mapMeta.name} (#${mapMeta.id})`;

      // 8. Visibilidade de elementos específicos do Mapa 1
      const isMap1 = (targetMapId === 1);"""

if old_switch_map_masks in code:
    code = code.replace(old_switch_map_masks, new_switch_map_masks)
    print("Updated switchMap mask loading successfully!")
else:
    print("Warning: old_switch_map_masks not matched exactly!")

# 3. Replace static mask initialization with loadMapMasks function
old_mask_init = """  // Camada 6: Máscaras de Telhado / Árvores (Foreground / Sobreposição)
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
  console.log(`Carregadas ${maskSprites.length} sobreposições de primeiro plano.`);"""

new_mask_init = """  // Camada 6: Máscaras de Telhado / Árvores (Foreground / Sobreposição Universal 76 Mapas)
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
  await loadMapMasks(currentMapId);"""

if old_mask_init in code:
    code = code.replace(old_mask_init, new_mask_init)
    print("Updated maskContainer initialization and loadMapMasks successfully!")
else:
    print("Warning: old_mask_init not matched exactly!")

# 4. Update ticker portal animation
old_ticker_portals = """    // 3.8 Animação e Detecção de Portais de Teleporte
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
    }"""

new_ticker_portals = """    // 3.8 Animação e Detecção de Portais de Teleporte
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
    }"""

if old_ticker_portals in code:
    code = code.replace(old_ticker_portals, new_ticker_portals)
    print("Updated ticker portal animation successfully!")
else:
    print("Warning: old_ticker_portals not matched exactly!")

# Save updated main.js
with open(MAIN_JS, "w", encoding="utf-8") as f:
    f.write(code)

print("Saved updated web/main.js successfully!")
