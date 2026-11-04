import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 1. Update README.md
with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

old_tree = '''│       ├── monsters/              # Atlases WebP de todos os 351 monstros e pets + catalog.json
│       └── characters/            # Atlases WebP de todas as 46 skins de classes + catalog.json'''

new_tree = '''│       ├── monsters/              # Atlases WebP de todos os 543 monstros e pets + catalog.json
│       ├── characters/            # Atlases WebP de todas as 46 skins de classes + catalog.json
│       ├── mounts/                # Catálogo de 20 montarias oficiais
│       ├── npcs/                  # 365 NPCs catalogados
│       ├── maps/                  # 76 mapas navegáveis com portais e colisões
│       ├── skills/                # 1.923 habilidades catalogadas com 411 ícones oficiais
│       ├── effects/               # 128 animações VFX de efeitos especiais em WebP
│       └── equipment/             # 1.865 equipamentos e armas com 1.565 ícones e 248 conjuntos'''

readme = readme.replace(old_tree.replace('\r\n', '\n'), new_tree.replace('\r\n', '\n'))
readme = readme.replace(old_tree.replace('\n', '\r\n'), new_tree.replace('\n', '\r\n'))

with open('README.md', 'w', encoding='utf-8') as f:
    f.write(readme)

# 2. Update GUIA_MIGRACAO.md
with open('GUIA_MIGRACAO.md', 'r', encoding='utf-8') as f:
    guia = f.read()

equip_section = '''

---

## 10. Conversão de Equipamentos, Armas e Conjuntos (Suits)

### 10.1 Origem dos Dados e Decodificação de Ícones
Os dados de equipamentos e armas foram extraídos de:
- `data_tbl_equipt_template.sql`: 1.865 itens de equipamento.
- `data_tbl_equipt_suit.sql`: 248 conjuntos com bônus de conjunto.
- `icon_code` mapeado via fórmula algorítmica:
  `code -> folder + prefix + num + ext` -> MD5 Hash -> `mcgame/frontend/s/res/{hash}`.
  Total de **1.565 ícones únicos** extraídos com 100% de correspondência.

### 10.2 Categorização & Tipos
- **Armas Principais (123 itens):** Espadas, Cajados, Rifles/Mosquetes, Maças/Martelos, Alaúdes e Bastões.
- **Armas Secundárias / Offhand (101 itens):** Escudos, Grimórios, Braçadeiras, Adagas, Cítaras e Manoplas.
- **Armaduras & Roupas (600 itens):** Elmos, Peitorais, Calças, Botas, Ombreiras e Cintos.
- **Joias & Acessórios (137 itens):** Colares, Anéis, Talismãs I e II.
- **Asas Celestiais & Visuais (334 itens):** Asas, Trajes Visuais (Costumes) e Voadores.
- **Equipamentos de Pets (570 itens):** Chifres, Coleiras, Sinos, Asas de Pet, Armaduras e Selos.
- **Conjuntos (248 sets):** Conjuntos com atributos e identificação de peças.

### 10.3 Catálogo JSON Unificado
Gerado em `web/assets/equipment/catalog.json` (2.07 MB) contendo nomes em Português e Vietnamita original, restrições de classe, nível mínimo, raridade com cores hexadecimais e propriedades estáticas dos itens.
'''

if '10. Conversão de Equipamentos' not in guia:
    guia += equip_section

with open('GUIA_MIGRACAO.md', 'w', encoding='utf-8') as f:
    f.write(guia)

print("Updated README.md and GUIA_MIGRACAO.md successfully!")
