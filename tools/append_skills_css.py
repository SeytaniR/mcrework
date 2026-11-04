import sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'
os.chdir(ws)

skill_css = '''
/* ========================================================
   GRIMÓRIO DE HABILIDADES & EFEITOS ESPECIAIS (VFX)
======================================================== */
.nav-skills {
  background: rgba(180, 142, 173, 0.25) !important;
  border-color: rgba(180, 142, 173, 0.5) !important;
  color: #d8bee5 !important;
}
.nav-skills:hover {
  background: rgba(180, 142, 173, 0.4) !important;
  border-color: #b48ead !important;
  box-shadow: 0 0 10px rgba(180, 142, 173, 0.4);
}

.skill-card {
  background: linear-gradient(145deg, rgba(33, 37, 46, 0.96), rgba(46, 52, 64, 0.94));
  border: 1px solid rgba(180, 142, 173, 0.28);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: all 0.22s ease;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
}

.skill-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #b48ead, #88c0d0, #ebcb8b);
  opacity: 0.6;
}

.skill-card:hover {
  transform: translateY(-3px);
  border-color: rgba(180, 142, 173, 0.7);
  box-shadow: 0 6px 18px rgba(180, 142, 173, 0.25);
}

.skill-card-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.skill-icon-wrapper {
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 8px;
  background: radial-gradient(circle, #2e3440 20%, #1e222b 90%);
  border: 1px solid rgba(180, 142, 173, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6);
}

.skill-icon-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
  image-rendering: pixelated;
}

.skill-card-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.skill-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.skill-card-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #eceff4;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.skill-badge-level {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 10px;
  background: rgba(235, 203, 139, 0.18);
  border: 1px solid rgba(235, 203, 139, 0.4);
  color: #ebcb8b;
  flex-shrink: 0;
}

.skill-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 2px;
}

.skill-type-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(136, 192, 208, 0.15);
  border: 1px solid rgba(136, 192, 208, 0.35);
  color: #88c0d0;
}

.skill-class-tag {
  font-size: 10px;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(163, 190, 140, 0.15);
  border: 1px solid rgba(163, 190, 140, 0.35);
  color: #a3be8c;
}

.skill-card-desc {
  font-size: 11px;
  line-height: 1.4;
  color: #d8dee9;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  min-height: 30px;
}

.skill-card-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.stat-pill {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.05);
  color: #e5e9f0;
}
.stat-pill.mp { color: #81a1c1; border: 1px solid rgba(129, 161, 193, 0.25); }
.stat-pill.sp { color: #ebcb8b; border: 1px solid rgba(235, 203, 139, 0.25); }
.stat-pill.target { color: #d08770; border: 1px solid rgba(208, 135, 112, 0.25); }
.stat-pill.area { color: #b48ead; border: 1px solid rgba(180, 142, 173, 0.25); }

.btn-cast-skill {
  width: 100%;
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 700;
  border: none;
  background: linear-gradient(135deg, #b48ead, #8fbcbb);
  color: #1e222b;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.btn-cast-skill:hover {
  background: linear-gradient(135deg, #c9a4c3, #a3c7c6);
  transform: scale(1.02);
  box-shadow: 0 4px 10px rgba(180, 142, 173, 0.4);
}

.btn-cast-skill:active {
  transform: scale(0.98);
}
'''

with open('web/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

if '/* GRIMÓRIO DE HABILIDADES' not in css and '.nav-skills' not in css:
    css += '\n' + skill_css
    with open('web/style.css', 'w', encoding='utf-8') as f:
        f.write(css)
    print("Appended skill styles to web/style.css successfully!")
else:
    print("Skill styles already present in style.css")
