import sys, os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

with open('web/main.js', 'r', encoding='utf-8') as f:
    code = f.read()

vfx_code = '''
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
'''

if 'async function playSkillVFX' not in code:
    code = code.replace('function resetCombatPoses()', vfx_code + '\n  function resetCombatPoses()', 1)
    with open('web/main.js', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Inserted playSkillVFX and executeSkill successfully!")
else:
    print("playSkillVFX already present in main.js")
