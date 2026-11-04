import os, sys, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ws = r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi'

print("=== 1. CHECKING WING ICONS IN CATALOG ===")
with open(os.path.join(ws, 'web', 'assets', 'wings', 'catalog.json'), 'r', encoding='utf-8') as f:
    wings = json.load(f)

for w in wings[:8]:
    icon_rel = w.get('icon', '')
    full_path = os.path.join(ws, 'web', icon_rel)
    print(f"  {w['name']}: {icon_rel} -> exists? {os.path.exists(full_path)}")

print("\n=== 2. CHECKING FASHION / DRESS IN DATA_TBL_DRESS.SQL & CATALOG ===")
with open(os.path.join(ws, 'web', 'assets', 'equipment', 'catalog.json'), 'r', encoding='utf-8') as f:
    eq_catalog = json.load(f)

items = eq_catalog.get('items', [])
costumes = [x for x in items if x.get('category_group') == 'wings_costumes' or 'fashion' in str(x.get('type_name', '')).lower() or 'trang phục' in str(x.get('position_name', '')).lower()]
print(f"Total Costumes / Fashion in catalog: {len(costumes)}")
for c in costumes[:10]:
    print(f"  ID {c['id']}: {c['name']} | pos={c.get('position_name')} | type={c.get('type_name')} | active_model={c.get('active_weapon_model') or c.get('active_wing_model')}")
