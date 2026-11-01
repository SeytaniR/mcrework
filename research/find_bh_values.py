with open(r'C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\mcgame\frontend\s\sv\MainClient_decrypted.swf', 'rb') as f:
    data = f.read()

# Let's search for "BH_ATTACK" in traits/cinit
# Or let's search for the byte sequence of traits in AbstractGameRes
# Let's search for text around 'AbstractGameRes'
idx = data.find(b'com.qeedoo.game.resource:AbstractGameRes')
print('AbstractGameRes at:', idx)

# Let's search for occurrences of 'BH_' in the script traits of AbstractGameRes
# In ABC, traits on a class often store const values directly in trait data!
# Trait_Slot / Trait_Const has: name (u30), type (u30), vindex (u30), vkind (u8)
# If vkind is 0x03 (CONSTANT_Int), vindex points to integer pool!
# Let's inspect bytes from idx - 2000 to idx + 2000
chunk = data[idx-1000:idx+2000]
# Search for strings
for s in [b'BH_ATTACK', b'BH_MAGIC', b'BH_RUN_NORMAL', b'BH_RUN_FAST', b'BH_BREATH_SLOW', b'BH_BREATH_FAST', b'BH_HURT', b'BH_DEAD', b'BH_SIT', b'BH_RUSH']:
    p = chunk.find(s)
    print(s.decode(), 'in chunk at:', p)
