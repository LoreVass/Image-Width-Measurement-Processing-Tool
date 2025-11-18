import cv2
import numpy as np
import os
import pandas as pd

output_folder = r"C:\Users\Utente\Desktop\Image_tool\Test_shapes"
os.makedirs(output_folder, exist_ok=True)

rows = []  # for CSV: ID, LENGTH, MIN_WIDTH, MAX_WIDTH

def save_shape(img, name):
    path = os.path.join(output_folder, name)
    cv2.imwrite(path, img)
    h, w = img.shape[:2]
    # For testing: length = image width (so 1 px = 1 mm)
    rows.append({"ID": name, "LENGTH": w, "MIN_WIDTH": 0, "MAX_WIDTH": 9999})

# 1) Constant bar
img = np.full((400, 800, 3), 255, np.uint8)
cv2.rectangle(img, (100, 180), (700, 220), (0, 0, 0), -1)
save_shape(img, "bar.png")

# 2) Ellipse
img = np.full((400, 800, 3), 255, np.uint8)
cv2.ellipse(img, (400, 200), (300, 100), 0, 0, 360, (0, 0, 0), -1)
save_shape(img, "ellipse.png")

# 3) Trapezoid (tapered bar)
img = np.full((400, 800, 3), 255, np.uint8)
pts = np.array([
    [100, 250],
    [700, 250],
    [650, 150],
    [150, 150]
], np.int32)
cv2.fillPoly(img, [pts], (0, 0, 0))
save_shape(img, "trapezoid.png")

# 4) Triangle
img = np.full((400, 800, 3), 255, np.uint8)
pts = np.array([
    [100, 300],
    [700, 200],
    [100, 100]
], np.int32)
cv2.fillPoly(img, [pts], (0, 0, 0))
save_shape(img, "triangle.png")

# 5) Plus / cross
img = np.full((600, 600, 3), 255, np.uint8)
cv2.rectangle(img, (250, 100), (350, 500), (0, 0, 0), -1)
cv2.rectangle(img, (100, 250), (500, 350), (0, 0, 0), -1)
save_shape(img, "plus.png")

# 6) Star-like polygon
img = np.full((600, 600, 3), 255, np.uint8)
pts = np.array([
    [300, 80],
    [340, 220],
    [480, 220],
    [360, 300],
    [400, 440],
    [300, 340],
    [200, 440],
    [240, 300],
    [120, 220],
    [260, 220]
], np.int32)
cv2.fillPoly(img, [pts], (0, 0, 0))
save_shape(img, "star.png")

# 7) “Fishy” polygon (long body + thin tail)
img = np.full((400, 800, 3), 255, np.uint8)
pts = np.array([
    [100, 200],  # tail left
    [200, 160],
    [350, 160],
    [650, 120],  # dorsal bump
    [700, 200],  # nose
    [650, 280],
    [350, 240],
    [200, 240]
], np.int32)
cv2.fillPoly(img, [pts], (0, 0, 0))
save_shape(img, "fishy_polygon.png")

# Save CSV
csv_path = os.path.join(output_folder, "example_shapes.csv")
pd.DataFrame(rows).to_csv(csv_path, index=False)
print("Saved images and CSV to:", output_folder)
