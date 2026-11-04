import os

main_js_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\main.js"
with open(main_js_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = """    if (isSpritesheet) {
      const tex = animFrames[player.frameIdx % animFrames.length];
      if (tex) {
        charSprite.texture = tex;
        const anchorY = currentMeta && currentMeta.anchor ? currentMeta.anchor[1] : 1.0;
        charSprite.anchor.set(0.5, anchorY);
        charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
      }
    } else {
      const currentFrameData = animFrames[player.frameIdx % animFrames.length];
      const tex = textureCache[currentFrameData.file];
      if (tex) {
        charSprite.texture = tex;
        charSprite.anchor.set(0.5, 110 / 150);
        charSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
      }
    }

    // Sincronizar asas na mesma direção e frame de ação
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
            wingSprite.position.set(0, PLAYER_GROUND_OFFSET_Y - 38);
            wingSprite.visible = true;

            // Z-Order: se estiver virado de costas (Norte: dirs 3, 4, 5), asas ficam na frente do corpo
            // Caso contrário (Frente/Sul/Lados: dirs 0, 1, 2, 6, 7), asas ficam atrás do corpo
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
      } else {
        wingSprite.visible = false;
      }
    }

    // Sincronizar arma empunhada na mesma direção e frame de ação
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
            weaponSprite.position.set(0, PLAYER_GROUND_OFFSET_Y);
            weaponSprite.visible = true;
          }
        }
      } else {
        weaponSprite.visible = false;
      }
    }"""

replacement = """    // Verificação de Montaria Voadora (tapetes, vassouras, pranchas, nuvens)
    const isFlyingMount = !!(playerEquippedWing && (
      playerEquippedWing.is_fly_mount ||
      (currentWingModel && currentWingModel.startsWith("equip_fly_")) ||
      (playerEquippedWing.model_id && playerEquippedWing.model_id.startsWith("equip_fly_"))
    ));

    // Flutuação suave e elevação dinâmica em montarias voadoras
    let hoverBob = 0;
    let charOffsetY = PLAYER_GROUND_OFFSET_Y;
    if (isFlyingMount) {
      hoverBob = Math.sin(performance.now() * 0.0035) * 4;
      charOffsetY = PLAYER_GROUND_OFFSET_Y - 30 + hoverBob; // Eleva o herói ~30px acima do chão para montar no veículo
      if (playerShadow) {
        playerShadow.scale.set(0.85, 0.85); // Sombra fica menor/mais suave durante o voo
      }
    } else {
      if (playerShadow) {
        playerShadow.scale.set(1.0, 1.0);
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
              // Montaria voadora posicionada sob os pés do personagem:
              wingSprite.position.set(0, PLAYER_GROUND_OFFSET_Y - 6 + hoverBob);
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
    }"""

text_norm = text.replace('\r\n', '\n')
target_norm = target.replace('\r\n', '\n')
replacement_norm = replacement.replace('\r\n', '\n')

if target_norm in text_norm:
    text_norm = text_norm.replace(target_norm, replacement_norm)
    with open(main_js_path, 'w', encoding='utf-8') as f:
        f.write(text_norm)
    print("SUCCESS: Replaced visual update logic in main.js!")
else:
    print("ERROR: Target block not found in main.js")
