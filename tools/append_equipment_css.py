import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

css_append = """
/* ==========================================================================
   Armaria de Equipamentos & Armas (Modal 7 & HUD)
   ========================================================================== */
.nav-equipment {
  background: rgba(235, 203, 139, 0.15) !important;
  border-color: rgba(235, 203, 139, 0.35) !important;
  color: #ebcb8b !important;
}

.nav-equipment:hover {
  background: rgba(235, 203, 139, 0.28) !important;
  border-color: #ebcb8b !important;
}

.equipment-card {
  background: rgba(30, 34, 43, 0.88);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  backdrop-filter: blur(8px);
}

.equipment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}

.equipment-card-header {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.equipment-card-icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #12151c;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  border: 1.5px solid #4c566a;
}

.equipment-card-icon {
  width: 32px;
  height: 32px;
  image-rendering: pixelated;
  object-fit: contain;
}

.equipment-card-title-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.equipment-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.equipment-card-name {
  font-size: 13.5px;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.equipment-card-orig {
  font-size: 10px;
  color: #94a3b8;
  font-style: italic;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.equipment-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 2px;
}

.equipment-slot-tag {
  font-size: 9.5px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(136, 192, 208, 0.15);
  border: 1px solid rgba(136, 192, 208, 0.35);
  color: #88c0d0;
}

.equipment-type-tag {
  font-size: 9.5px;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(163, 190, 140, 0.15);
  border: 1px solid rgba(163, 190, 140, 0.35);
  color: #a3be8c;
}

.equipment-class-tag {
  font-size: 9.5px;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(180, 142, 173, 0.15);
  border: 1px solid rgba(180, 142, 173, 0.35);
  color: #b48ead;
}

.equipment-suit-tag {
  font-size: 9.5px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(235, 203, 139, 0.15);
  border: 1px solid rgba(235, 203, 139, 0.4);
  color: #ebcb8b;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.equipment-card-desc {
  font-size: 11px;
  line-height: 1.35;
  color: #d8dee9;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 28px;
}

.equipment-card-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.equipment-stat-pill {
  font-size: 9.5px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #81a1c1;
}

.equipment-stat-pill.atk {
  color: #bf616a;
  border-color: rgba(191, 97, 106, 0.3);
  background: rgba(191, 97, 106, 0.1);
}

.equipment-stat-pill.def {
  color: #a3be8c;
  border-color: rgba(163, 190, 140, 0.3);
  background: rgba(163, 190, 140, 0.1);
}

.equipment-stat-pill.spd {
  color: #ebcb8b;
  border-color: rgba(235, 203, 139, 0.3);
  background: rgba(235, 203, 139, 0.1);
}

.equipment-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.equipment-durability {
  font-size: 10px;
  color: #94a3b8;
}

.equipment-quality-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
}
"""

with open(r'web\style.css', 'a', encoding='utf-8') as f:
    f.write(css_append)

print("Appended equipment CSS styles successfully!")
