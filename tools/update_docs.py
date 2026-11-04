import sys, os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

# 1. Update README.md
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

skills_readme_section = '''
### 5. Acervo de Habilidades & Efeitos Especiais (VFX / SFX) 🔮✨
* **Extração Visual Exclusiva:** Conforme a filosofia do projeto, nenhuma fórmula ou cálculo antigo foi importado. Todo o foco foi direcionado para a recuperação integral do patrimônio audiovisual de magias e efeitos:
  * 🔮 **1.923 Habilidades Catalogadas:** Mapeadas com nomes, categorias (Classes, Pets, Despertar, Suporte), tipos de alvo e padrões de área.
  * 🎨 **411 Ícones Oficiais (32×32 PNG):** Extraídos e organizados em `web/assets/skills/icons/`.
  * ⚡ **128 Efeitos Especiais Animados (VFX):** Decompilados a partir dos arquivos SWF originais (`DefineSprite` e vetores Flash) e convertidos em spritesheets WebP compactos com transparência alfa e metadados de duração em `web/assets/effects/`.
  * 📱 **Grimório Interativo no Cliente:** Provador de habilidades no topo do HUD mobile com busca em tempo real, filtros por classe/pet e botão de disparo imediato do efeito visual no jogo.
'''

if '### 5. Acervo de Habilidades' not in readme:
    readme = readme.replace('### 4. Separação Arquitetural em 3 Camadas', skills_readme_section + '\n### 4. Separação Arquitetural em 3 Camadas')
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme)
    print("Updated README.md successfully!")

# 2. Update GUIA_MIGRACAO.md
with open('GUIA_MIGRACAO.md', 'r', encoding='utf-8') as f:
    guia = f.read()

skills_guia_section = '''
---

## 7. Pipeline de Conversão de Habilidades e Efeitos Especiais (VFX)

### 7.1. Arquitetura de Hashes e Resolução de Recursos
O cliente Flash original do Magic Campus resolvia recursos através de códigos numéricos de 13 dígitos (`iconCode`, `resCode`) mapeados pela classe `UrlUtil.as`:
* **Ícones de Habilidade:** Convertidos a partir de `icon/skill/SKILL_NORMAL_{num:06d}.png` para MD5 e extraídos para `web/assets/skills/icons/{num}.png` (411 ícones recuperados).
* **Efeitos Especiais:** Localizados como `resource/effect/EFF_PLAYER_{num:06d}.swf` (128 arquivos SWF processados com sucesso).

### 7.2. Rasterização Vetorial Headless e Geração de Spritesheets WebP
Diferente dos monstros e personagens que continham bitmaps rasterizados internos, os efeitos especiais de magia e combate eram animações vetoriais Flash puras (`DefineSprite`, `DefineShape3`).
* **Descompilação:** Uso de pipeline automatizado com JPEXS Decompiler (FFDec v26.4.0) em modo headless (`-ignorebackground -format sprite:png,frame:png -export sprite,frame`).
* **Empacotamento WebP:** Para cada efeito, os quadros do `Timeline_1` / sprite principal foram recortados por sua caixa delimitadora global (*bounding box*) e montados em um atlas WebP de alta eficiência (`atlas.webp` + `atlas.json` + `visual_meta.json`).
* **Metadados:** Cada efeito inclui FPS, duração em milissegundos (`duration_ms`), dimensões e pontos de âncora para centralização perfeita sobre o alvo.

### 7.3. Catálogo de Habilidades e Desacoplamento Lógico
* **Catálogo Unificado:** `web/assets/skills/catalog.json` consolida 1.923 habilidades distintas com níveis, descrições, classes requeridas, custos de MP/SP e vinculação ao respectivo efeito especial VFX (`effect_id`).
* **Zero Fórmulas Antigas:** Nenhuma tabela de dano ou cálculo antigo foi importado, permitindo que o novo motor de combate defina livremente seus multiplicadores e balanceamento.
'''

if '## 7. Pipeline de Conversão de Habilidades' not in guia:
    guia += '\n' + skills_guia_section
    with open('GUIA_MIGRACAO.md', 'w', encoding='utf-8') as f:
        f.write(guia)
    print("Updated GUIA_MIGRACAO.md successfully!")
