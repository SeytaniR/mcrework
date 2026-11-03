import os, re, json

world_map_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\docs\client\view\view\compMain\WorldMap.as"
with open(world_map_path, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

print("Length of WorldMap.as:", len(text))

# Flex UIComponentDescriptor parsing
# Usually look like: "id":"i1", ... "propertiesFactory":function():Object{ return {"x":123, "y":456 ...
pattern = re.compile(r'\"id\"\s*:\s*\"([^\"]+)\".*?\"x\"\s*:\s*(\d+).*?\"y\"\s*:\s*(\d+)', re.DOTALL)
matches = pattern.findall(text)
print("Regex matches (id, x, y):", len(matches))
for m in matches[:20]:
    print(m)

# Search for mapId assignments or icon configuration
map_id_pattern = re.compile(r'(\w+)\.mapId\s*=\s*(\d+)', re.IGNORECASE)
map_ids = map_id_pattern.findall(text)
print("mapId assignments:", len(map_ids))
for m in map_ids[:20]:
    print(m)

# Search for any string containing map or icon
for line in text.split("\n"):
    if "mapid" in line.lower() or "mapname" in line.lower() or "tipmap" in line.lower():
        if len(line.strip()) < 140:
            print("MAP LINE:", line.strip())
