# Magic Campus Rework (HTML5 / Pixi.js Engine) 🧙‍♂️✨

Um projeto moderno de recriação e migração de engine para o clássico MMORPG **Magic Campus (魔力学堂)**, convertendo os assets e lógicas originais em Flash (**ActionScript 3 / SWF**) para uma stack moderna de alta performance em **HTML5, WebGL e Pixi.js**, com suporte completo e otimizado para dispositivos móveis e desktop.

---

## 🌟 Funcionalidades Implementadas

### 🗺️ Sistema de Mapas 2.5D & NPCs Autênticos
* **Renderização em Camadas:** Terreno base (`2000x1500`), entidades dinâmicas com Z-Ordering 2.5D e sobreposições de primeiro plano.
* **NPCs Originais Animados:** Todos os 14 NPCs do Mapa 1 extraídos dos arquivos SWF originais (`creature/NPC_FUNC_*.swf`), com animações completas de respiração/idle em 4 frames em loop, proporção calibrada (`scale = 0.70`, redução de 30% combinando com o jogador), sombras suaves no chão e nomes dourados autênticos.
* **Interatividade com NPCs:** Toque em qualquer NPC para o personagem correr até ele e abrir o cartão de diálogo mobile com as falas e saudações dos personagens.
* **Ordenação de Profundidade (Z-Ordering 2.5D):** O jogador passa na frente ou atrás dos NPCs e árvores de forma natural e realista com base na coordenada Y dos pés.
* **Malha de Colisão Binária (1-Bit Binary Mesh):** Extraída diretamente de `Hit.swf` para um arquivo bruto `collision.bin` (`2031x1531`). Checagem de colisão bitwise ultra-eficiente $O(1)$ sem lag de CPU.
* **Deslize em Paredes (*Wall Sliding*):** O personagem contorna cantos e desliza pelas quinas suavemente sem travar.
* **Transparência de Oclusão (*Foreground Occlusion Fading*):** Telhados de casas e copas de árvores ficam transparentes suavemente (`alpha = 0.35`) quando o jogador passa por trás deles.

### ⚔️ Sistema de Animações e Personagens
* **Alinhamento e Pivô Matemático Exato:** Ponto de registro cravado nos pés `(0.5, 110/150)`, garantindo alinhamento perfeito de sombra, modelo e etiqueta de nome em todas as direções e ações.
* **8 Direções Isométricas (0 a 7):** Sul, Sudeste, Leste, Nordeste, Norte, Noroeste, Oeste e Sudoeste calculadas via trigonometria angular contínua.
* **11 Ações de Combate e Movimento:**
  * `0`: Parado / Respirando (*Idle* - 27f)
  * `1`: Andar lento (*Walk* - 8f)
  * `2`: Corrida rápida (*Run / Rush* - 16f) — **movimentação padrão**
  * `3`: Golpe físico / Ataque (*Attack* - 10f)
  * `4`: Derrotado / Caído no chão (*Dead* - 1f)
  * `5`: Tomando dano com flash de impacto (*Hurt* - 7f)
  * `6`: Defesa / Guarda (*Block* - 7f)
  * `7`: Conjuração / Magia (*Cast* - 12f)
  * `8`: Buff / Postura tática (*Prepare* - 27f)
  * `9`: Golpe pesado (*Heavy Attack* - 16f)
  * `10`: Habilidade Suprema (*Ultimate* - 32 frames completos!)
* **Suporte Multi-Classes e Tiers:**
  * 🛡️ **Guerreiro Evoluído / Tier 2** (`PC_MALE_000011` - 11 ações completas)
  * ⚔️ **Guerreiro Base / Tier 1** (`PC_MALE_000001` - 8 ações)
  * 🔮 **Mago Base** (`PC_MALE_000002` - 8 ações com animações de cajado)
  * 🐎 **Pose de Montaria** (`PC_MALE_100001` - postura montada)

### 👾 Monstros & Teste de Animações em Combate (Direto no Mapa)
* **Monstro no Mapa 1:** `Cogumelo Selvagem [Nv. 5]` (*Nấm Đồng Cỏ* / `NPC_CRE_000015.swf`), extraído com precisão dos arquivos SWF de criaturas originais, renderizado diretamente no mapa com sombra suave e animação de respiração contínua em escala proporcional (`scale = 0.70`).
* **Engajamento Direto no Mapa:** Ao clicar no monstro (ou via botão do menu lateral), o personagem corre até ele e ambos ficam frente a frente no próprio mapa para testar as animações sem telas separadas ou barras de HP que encerram a sessão.
* **Painel de Teste de Animações de Combate:**
  * **Animações do Jogador:**
    * `⚔️ Golpe`: Golpe físico cortante (Ação 3) com avanço e impacto no monstro.
    * `🔮 Magia`: Rajada arcana (Ação 7) com efeito visual de conjuração.
    * `⚡ Suprema`: Sequência completa de 32 frames (Ação 10) com múltiplos hits e finalizador.
    * `🛡️ Guarda`: Postura de bloqueio e defesa (Ação 6).
    * `💥 Dano`: Reação de impacto / hurt (Ação 5) com flash avermelhado.
    * `💀 Caído`: Animação de derrotado / caído no chão (Ação 4).
  * **Animações do Monstro:**
    * `🍄 Cabeçada`: Ataque físico com avanço frontal (Ação 3).
    * `☠️ Esporos`: Magia de liberação de nuvem tóxica de esporos (Ação 7).
    * `🛡️ Defesa`: Postura de cúpula endurecida (Ação 6).
    * `💥 Dano`: Reação de impacto / hurt (Ação 5) com flash vermelho.
    * `💀 Caído`: Animação de derrotado / caído no chão (Ação 4).
* **🔄 Sparring Contínuo (Loop Infinito):** Modo que faz os combatentes trocarem golpes e reações continuamente em loop sem limite de vida, ideal para apreciar a fluidez das animações combinadas.
* **Textos Flutuantes de Combate:** Textos animados estilizados sobre os personagens (`💥 GOLPE!`, `🔮 MAGIA!`, `⚡ COMBO!`, `☠️ ESPOROS!`, `🛡️ DEFESA!`).
* **Sem Interrupções:** Não há telas de "fim de batalha" bloqueando os testes; você pode alternar livremente entre ações e sair para andar pelo mapa quando quiser.

### 📱 Interface Mobile-First
* **Joystick Analógico Virtual:** Toque dinâmico e resposta vetorial precisa.
* **Tap-to-Move:** Toque em qualquer ponto livre do mapa para o personagem correr até o local.
* **Grade de Ações Compacta (2x4):** Ataque, Magia, Suprema, Defesa, Dano, Caído, Correr e Parar no alcance do polegar.
* **Painel de Diagnóstico (Menu ⚙️):** Teleportes rápidos, seletor de classes em tempo real, controle de zoom, slider de velocidade e visualizador da malha de colisão vermelha para testes.

---

## 🌐 Jogar Online (GitHub Pages)

A aplicação está configurada para deploy contínuo no GitHub Pages:
👉 **[https://seytanir.github.io/mcrework/](https://seytanir.github.io/mcrework/)**

---

## 🚀 Como Executar Localmente

### 1. Iniciar o Servidor
Com Python instalado, execute na raiz do projeto:
```bash
python -m http.server 8080 --directory web
```

### 2. Acessar
* **No Computador:** [http://localhost:8080/](http://localhost:8080/)
* **No Celular (mesmo Wi-Fi):** `http://{IP_DO_SEU_PC}:8080/`

---

## 📖 Documentação Técnica de Migração

Para entender detalhadamente como os arquivos SWF, as matrizes de bits de colisão e os frames foram revertidos e convertidos, consulte o guia completo:

👉 **[GUIA_MIGRACAO.md](GUIA_MIGRACAO.md)**

---

## 📁 Estrutura do Repositório

```text
├── web/                           # Aplicação Web Pixi.js (Pronta para rodar)
│   ├── index.html                 # Interface responsiva mobile
│   ├── style.css                  # Estilização moderna e layout de botões
│   ├── main.js                    # Motor Pixi.js, física, colisão e animações
│   └── assets/                    # Assets convertidos e otimizados
│       ├── map1/                  # Background, máscaras, NPCs e collision.bin
│       ├── char1/                 # Guerreiro Base (Tier 1)
│       ├── char11/                # Guerreiro Evoluído (Tier 2 - Ações 0 a 10)
│       ├── char2/                 # Mago Base
│       └── char_mount/            # Poses de Montaria
├── tools/                         # Ferramentas Python de extração e conversão
│   ├── extract_character.py       # Extrai qualquer SWF de personagem para Pixi
│   ├── extract_map.py             # Extrai mapas, máscaras e NPCs
│   └── extract_collision.py       # Decodifica malhas de colisão RLE de Hit.swf
├── GUIA_MIGRACAO.md               # Documentação técnica aprofundada da migração
└── README.md                      # Apresentação do projeto
```
