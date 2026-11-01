from PIL import Image

map_img = Image.open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\map1.jpg").convert("RGBA")
col_img = Image.open(r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\web\assets\map1\collision.png").convert("L")

w, h = map_img.size
print(f"Map size: {w}x{h}, Col size: {col_img.size}")

# Overlay blocked pixels (0) with semi-transparent RED
overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
over_pixels = overlay.load()
col_pixels = col_img.load()

for y in range(h):
    for x in range(w):
        if col_pixels[x, y] == 0:  # obstacle
            over_pixels[x, y] = (255, 0, 0, 100) # Red
        else:
            over_pixels[x, y] = (0, 255, 0, 30)  # Faint green for walkable path

comp = Image.alpha_composite(map_img, overlay)
out_path = r"C:\Users\Dell\.gemini\antigravity\scratch\magic-campus-pixi\debug_map_collision.png"
comp.save(out_path)
print(f"Saved {out_path}")
