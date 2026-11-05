from PIL import Image

bg2 = Image.open('web/assets/maps/map_2/bg.jpg').convert('RGBA')
mask = Image.open('tools/test_map2_world_mask.png').convert('RGBA')

# Let's crop a 600x600 region where the mask has opaque pixels
# On Map 2, around x=500..1100, y=100..700
crop_bg = bg2.crop((500, 100, 1100, 700))
crop_mask = mask.crop((500, 100, 1100, 700))

# Save side by side
comb = Image.new('RGB', (1200, 600))
comb.paste(crop_bg.convert('RGB'), (0, 0))
comb.paste(crop_mask.convert('RGB'), (600, 0))
comb.save('tools/test_map2_side_by_side.jpg')
print("Saved tools/test_map2_side_by_side.jpg")
