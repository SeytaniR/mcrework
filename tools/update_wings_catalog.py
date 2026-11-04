import json, os

catalog_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\wings\catalog.json"
with open(catalog_path, 'r', encoding='utf-8') as f:
    items = json.load(f)

fly_mount_meta = {
    "equip_fly_000004": ("Tapete Mágico Imperial", "Tapete místico lendário que flutua suavemente sob os pés do personagem."),
    "equip_fly_000006": ("Vassoura Encantada da Bruxa", "Vassoura mágica veloz que voa pelos ares sustentando o herói com encantos arcanos."),
    "equip_fly_000007": ("Prancha Cósmica Astral", "Prancha translúcida com energia das estrelas para surfar pelos céus do continente."),
    "equip_fly_000008": ("Tapete Voador da Aurora", "Tapete sagrado tecido com fios celestiais e poeira de estrelas cadentes."),
    "equip_fly_000009": ("Nuvem Mística dos Sábios", "Nuvem pura e luminosa dos antigos mestres que flutua suavemente sob os pés."),
    "equip_fly_000010": ("Espada Voadora Celestial", "Espada sagrada imbuída de mana arcano sobre a qual o herói cavalga os ventos."),
    "equip_fly_000011": ("Vassoura das Sombras", "Artefato místico noturno das bruxas das trevas para voo rápido e silencioso."),
    "equip_fly_000014": ("Prancha Solar Dourada", "Prancha de velocidade supersônica banhada com o poder do sol da alvorada."),
    "equip_fly_000015": ("Tapete Real dos Sultões", "Tapete ricamente bordado em ouro puro e pedras preciosas da corte real."),
    "equip_fly_000017": ("Prancha Glacial do Ártico", "Esculpida em gelo perpétuo dos cumes nevados, emana uma brisa refrescante."),
    "equip_fly_000018": ("Pássaro Mecânico Flutuante", "Engenhosa invenção aérea com engrenagens e asas mecânicas a vapor."),
    "equip_fly_000019": ("Nuvem Celestial do Trovão", "Nuvem de tempestade carregada com faíscas elétricas e relâmpagos."),
    "equip_fly_000020": ("Lótus Voadora Espiritual", "Flor sagrada de lótus flutuante que concede serenidade e voo gracioso."),
    "equip_fly_000021": ("Fênix Cósmica de Chamas", "Montaria voadora lendária que cruza os céus envolta em labaredas místicas."),
    "equip_fly_000022": ("Tapete Lendário do Dragão", "Tapeçaria ancestral forjada com a proteção mística do Dragão Supremo.")
}

for item in items:
    mid = item.get('model_id', '')
    is_fly = mid.startswith('equip_fly_')
    item['is_fly_mount'] = is_fly
    item['category_type'] = 'fly_mount' if is_fly else 'wing'
    if is_fly and mid in fly_mount_meta:
        pt_name, pt_desc = fly_mount_meta[mid]
        item['name'] = pt_name
        item['description'] = pt_desc
        item['type_label'] = "Montaria Voadora"
    else:
        item['type_label'] = "Asa Mística"

with open(catalog_path, 'w', encoding='utf-8') as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"Updated {len(items)} wings/mounts in catalog.json! (15 flying mounts, 21 wings)")
