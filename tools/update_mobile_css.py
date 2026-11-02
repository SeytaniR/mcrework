with open('web/style.css', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = "/* ==========================================================================\n   REFATORAÇÃO DA BARRA SUPERIOR (HEADER SEM BOTÕES ESMAGADOS)\n   ========================================================================== */"
end_marker = "/* ==========================================================================\n   MINIATURAS E CARDS VISUAIS DE ASSETS (THUMBNAILS)\n   ========================================================================== */"

idx1 = text.find(start_marker)
idx2 = text.find(end_marker)

print("idx1:", idx1, "idx2:", idx2)

replacement = """/* ==========================================================================
   REFATORAÇÃO DA BARRA SUPERIOR & LAYOUT MOBILE
   ========================================================================== */
#mobile-top-bar {
  position: absolute;
  top: max(8px, var(--safe-top));
  left: max(8px, var(--safe-left));
  right: max(8px, var(--safe-right));
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(22, 26, 36, 0.94);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 14px;
  padding: 6px 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.45);
  pointer-events: auto;
  gap: 6px;
  max-width: calc(100vw - 16px);
  box-sizing: border-box;
}

.game-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.top-center-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  padding: 2px 2px;
}
.top-center-actions::-webkit-scrollbar {
  display: none;
}

.nav-pill-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  border-radius: 16px;
  padding: 5px 10px;
  color: #eceff4;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  border: 1px solid;
  flex-shrink: 0;
}
.nav-pill-btn:active {
  transform: scale(0.95);
}

.nav-count {
  background: rgba(0, 0, 0, 0.35);
  padding: 1px 5px;
  border-radius: 10px;
  font-size: 9.5px;
  font-weight: 800;
}

.nav-classes {
  background: rgba(94, 129, 172, 0.22);
  border-color: rgba(94, 129, 172, 0.45);
  color: #88c0d0;
}
.nav-monsters {
  background: rgba(191, 97, 106, 0.22);
  border-color: rgba(191, 97, 106, 0.45);
  color: #ebcb8b;
}
.nav-mounts {
  background: rgba(136, 192, 208, 0.22);
  border-color: rgba(136, 192, 208, 0.45);
  color: #88c0d0;
}
.nav-npcs {
  background: rgba(235, 203, 139, 0.22);
  border-color: rgba(235, 203, 139, 0.45);
  color: #ebcb8b;
}

.card-btn-action.btn-mount {
  background: #88c0d0;
  color: #1e222b;
}
.card-btn-action.btn-mount:hover {
  background: #9bd6e6;
}
.card-btn-action.btn-npc {
  background: #ebcb8b;
  color: #1e222b;
}
.card-btn-action.btn-npc:hover {
  background: #f5dca3;
}

.top-right-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

@media (max-width: 600px) {
  #mobile-top-bar {
    padding: 4px 8px;
    gap: 4px;
    top: max(4px, var(--safe-top));
    left: max(4px, var(--safe-left));
    right: max(4px, var(--safe-right));
    max-width: calc(100vw - 8px);
  }
  .logo-icon {
    font-size: 16px;
  }
  .game-name {
    font-size: 11px;
  }
  .map-name {
    display: none;
  }
  .nav-pill-btn {
    padding: 4px 8px;
    font-size: 10.5px;
    gap: 4px;
    border-radius: 14px;
  }
  .nav-count {
    font-size: 9px;
    padding: 0 4px;
  }
  .fps-pill {
    display: none;
  }
  .icon-btn {
    width: 32px;
    height: 32px;
    font-size: 15px;
  }

  /* Modais como Bottom Sheet Nativo Mobile */
  .catalog-modal {
    padding: 0 !important;
    align-items: flex-end !important;
  }
  .modal-card {
    max-width: 100vw !important;
    width: 100vw !important;
    height: 94vh !important;
    max-height: 94vh !important;
    border-radius: 20px 20px 0 0 !important;
    border-bottom: none !important;
  }
  .modal-header {
    padding: 12px 14px !important;
  }
  .modal-title-group h3 {
    font-size: 15px !important;
  }
  .modal-subtitle {
    font-size: 10.5px !important;
  }
  .modal-close-btn {
    width: 32px !important;
    height: 32px !important;
    font-size: 16px !important;
  }
  .modal-search-bar {
    padding: 8px 12px 4px 12px !important;
  }
  .modal-search-bar input {
    padding: 8px 12px !important;
    font-size: 12.5px !important;
  }
  .modal-filter-pills {
    padding: 4px 12px 8px 12px !important;
    gap: 5px !important;
  }
  .pill-filter {
    font-size: 10px !important;
    padding: 4px 8px !important;
  }
  .modal-grid-container {
    padding: 4px 12px 16px 12px !important;
    grid-template-columns: 1fr !important;
    gap: 8px !important;
  }
  .asset-card {
    padding: 8px 10px !important;
  }
  .asset-thumb-wrapper {
    width: 60px !important;
    height: 60px !important;
    min-width: 60px !important;
  }
  .card-title {
    font-size: 12.5px !important;
  }
  .card-meta-text {
    font-size: 10px !important;
  }
  .card-btn-action {
    padding: 8px 10px !important;
    font-size: 11px !important;
  }

  /* Painel de Combate Mobile */
  .combat-test-panel {
    width: 100vw !important;
    max-width: 100vw !important;
    max-height: 52vh !important;
    border-radius: 20px 20px 0 0 !important;
    padding: 10px 12px max(12px, var(--safe-bottom)) 12px !important;
    box-sizing: border-box !important;
  }
  .combat-test-header {
    padding-bottom: 6px !important;
  }
  .combat-badge-group {
    gap: 5px !important;
  }
  .combat-sub {
    font-size: 11px !important;
  }
  .btn-switch-mon {
    font-size: 10px !important;
    padding: 4px 7px !important;
  }
  .btn-close-combat {
    font-size: 10px !important;
    padding: 4px 7px !important;
  }
  .combat-status-bar {
    padding: 4px 8px !important;
    font-size: 10.5px !important;
  }
  .combat-controls-body {
    max-height: calc(52vh - 90px) !important;
    overflow-y: auto !important;
    gap: 8px !important;
  }
  .combat-actions-grid {
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 5px !important;
  }
  .c-btn {
    padding: 5px 3px !important;
    font-size: 10px !important;
  }
  .c-icon {
    font-size: 14px !important;
  }

  /* Diálogo de NPC */
  .npc-dialog {
    width: calc(100% - 20px) !important;
    bottom: max(90px, var(--safe-bottom)) !important;
  }

  /* Joystick e Botões de Ação na Tela */
  #joystick-container {
    width: 110px !important;
    height: 110px !important;
    bottom: max(14px, var(--safe-bottom)) !important;
    left: max(12px, var(--safe-left)) !important;
  }
  #mobile-action-bar {
    grid-template-columns: repeat(2, 46px) !important;
    gap: 5px !important;
    bottom: max(14px, var(--safe-bottom)) !important;
    right: max(10px, var(--safe-right)) !important;
  }
  .action-btn {
    width: 46px !important;
    height: 46px !important;
  }
  .btn-icon {
    font-size: 15px !important;
  }
  .btn-label {
    font-size: 7.5px !important;
  }
}

@media (max-width: 375px) {
  .game-name {
    display: none;
  }
  #mobile-action-bar {
    grid-template-columns: repeat(2, 42px) !important;
    gap: 4px !important;
  }
  .action-btn {
    width: 42px !important;
    height: 42px !important;
  }
}
"""

if idx1 != -1 and idx2 != -1:
    new_text = text[:idx1] + replacement + "\n" + text[idx2:]
    with open('web/style.css', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("Successfully replaced top bar and mobile rules in web/style.css!")
else:
    print("Could not find markers!")
