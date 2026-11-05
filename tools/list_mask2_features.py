from PIL import Image
import numpy as np

m = Image.open('tools/test_map2_world_mask.png')
arr = np.array(m)
# Find clusters of alpha > 20 in world coordinates
from scipy.ndimage import label, find_objects
labeled, num_features = label(arr[:, :, 3] > 20)
objects = find_objects(labeled)
print(f"Total features in test_map2_world_mask: {num_features}")
for i, obj in enumerate(objects):
    sy, sx = obj
    area = np.sum(labeled[obj] == (i + 1))
    if area > 100:
        print(f"Feature {i+1}: x=[{sx.start}..{sx.stop}] (w={sx.stop-sx.start}), y=[{sy.start}..{sy.stop}] (h={sy.stop-sy.start}), area={area}")
