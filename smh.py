import cv2
import numpy as np
from PIL import Image

# Load master image with alpha channel
master_path = "master_pekseg.png"
img = cv2.imread(master_path, cv2.IMREAD_UNCHANGED)
height, width = img.shape[:2]

# Extract alpha channel and threshold to get mask
alpha = img[:, :, 3]
mask = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)[1]

# Find contours (each segment should be a separate contour)
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours if needed (e.g. by area or position)
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Create output folder
import os
os.makedirs("segments", exist_ok=True)

# Process each contour
for i, cnt in enumerate(contours):
    # Create a blank transparent canvas
    blank = np.zeros((height, width, 4), dtype=np.uint8)

    # Draw the contour onto the blank canvas
    cv2.drawContours(blank, [cnt], -1, (255, 255, 255, 255), thickness=cv2.FILLED)

    # Mask the original image with the drawn contour
    isolated = cv2.bitwise_and(img, blank)

    # Save as PNG
    segment_pil = Image.fromarray(isolated)
    segment_pil.save(f"segments/segment_{i:02d}.png")
    print(f"Saved segment_{i:02d}.png")
