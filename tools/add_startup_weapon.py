with open('web/main.js', 'r', encoding='utf-8') as f:
    c = f.read()

target = '  console.log("Magic Campus Mobile Engine inicializado com sucesso!");'
replacement = '''  // Restaurar arma empunhada salva ou equipar inicial
  const savedWeaponId = localStorage.getItem("mc_equipped_weapon_id");
  if (savedWeaponId && equipmentList && equipmentList.length > 0) {
    const savedItem = equipmentList.find(x => String(x.id) === String(savedWeaponId));
    if (savedItem) equipWeapon(savedItem);
  } else if (equipmentList && equipmentList.length > 0) {
    const defItem = equipmentList.find(x => x.id === 170) || equipmentList.find(x => x.category_group === "weapons");
    if (defItem) equipWeapon(defItem);
  }

  console.log("Magic Campus Mobile Engine inicializado com sucesso!");'''

if target in c:
    c = c.replace(target, replacement, 1)
    with open('web/main.js', 'w', encoding='utf-8') as f:
        f.write(c)
    print('Startup weapon equip added successfully!')
else:
    print('Target not found!')
