import cv2
import numpy as np
from skimage import measure
import matplotlib.pyplot as plt

# Load video and extract frame 80
cap = cv2.VideoCapture("IMG_4128.mp4")
cap.set(cv2.CAP_PROP_POS_FRAMES, 80)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Failed to read frame!")
    exit(1)

# ROI
roi_x1, roi_y1 = 1000, 1803
roi_x2, roi_y2 = 1200, 2492

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
cropped = gray[roi_y1:roi_y2, roi_x1:roi_x2]

print(f"Cropped shape: {cropped.shape}")
print(f"Intensity range: {cropped.min()} - {cropped.max()}")

# Apply CLAHE
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
enhanced = clahe.apply(cropped)

# Threshold
_, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh = cv2.bitwise_not(thresh)

# Find regions
labels = measure.label(thresh)
regions = measure.regionprops(labels, intensity_image=cropped)

print(f"\nFound {len(regions)} regions")

# Print ALL regions to debug
print("\nALL regions:")
for i, region in enumerate(regions):
    cy, cx = region.centroid
    area = region.area
    if region.perimeter > 0:
        circularity = 4 * np.pi * area / (region.perimeter ** 2)
    else:
        circularity = 0

    in_upper = cy < cropped.shape[0] * 0.6
    size_ok = 100 < area < 2000
    circular_ok = circularity > 0.5

    print(f"  Region {i}: center=({cx:.0f},{cy:.0f}), area={area}, circ={circularity:.2f}, "
          f"intensity={region.mean_intensity:.1f}, in_upper={in_upper}, size_ok={size_ok}, circular_ok={circular_ok}")

# Analyze each region with RELAXED filters
candidates = []
for i, region in enumerate(regions):
    cy, cx = region.centroid
    area = region.area

    # RELAXED: Just check if in upper 80% and reasonable size
    if cy < cropped.shape[0] * 0.8 and area > 50:  # Removed upper bound, lowered minimum
        if region.perimeter > 0:
            circularity = 4 * np.pi * area / (region.perimeter ** 2)
        else:
            circularity = 0

        # RELAXED: Accept circularity > 0.3 instead of 0.5
        if circularity > 0.3:
            darkness = 50 - region.mean_intensity
            score = circularity * 2 + darkness/10 + (1 - cy/cropped.shape[0])

            candidates.append({
                'id': i,
                'center': (cx, cy),
                'area': area,
                'circularity': circularity,
                'mean_intensity': region.mean_intensity,
                'score': score,
                'diameter': np.mean([region.major_axis_length, region.minor_axis_length])
            })

# Sort by score
candidates.sort(key=lambda x: x['score'], reverse=True)

print(f"\nTop 5 candidates:")
for i, c in enumerate(candidates[:5]):
    print(f"{i+1}. Center: ({c['center'][0]:.1f}, {c['center'][1]:.1f}), "
          f"Intensity: {c['mean_intensity']:.1f}, "
          f"Circularity: {c['circularity']:.2f}, "
          f"Score: {c['score']:.2f}")

# Visualize
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].imshow(cropped, cmap='gray')
axes[0].set_title('Original')
axes[0].axhline(y=cropped.shape[0] * 0.6, color='r', linestyle='--', label='60% line')

axes[1].imshow(enhanced, cmap='gray')
axes[1].set_title('CLAHE Enhanced')

axes[2].imshow(cropped, cmap='gray')

# Draw top 3 candidates
colors = ['red', 'yellow', 'cyan']
for i, c in enumerate(candidates[:3]):
    cx, cy = c['center']
    r = c['diameter'] / 2
    circle = plt.Circle((cx, cy), r, color=colors[i], fill=False, linewidth=2, label=f"#{i+1} (score={c['score']:.1f})")
    axes[2].add_patch(circle)
    axes[2].plot(cx, cy, 'x', color=colors[i], markersize=10)

axes[2].set_title('Top 3 Detections')
axes[2].legend()

plt.tight_layout()
plt.savefig('debug_detect/first_frame_validation.png', dpi=150)
print("\nSaved validation to debug_detect/first_frame_validation.png")

if candidates:
    best = candidates[0]
    print(f"\nBEST DETECTION: Center ({best['center'][0]:.1f}, {best['center'][1]:.1f})")
    print("Is this correct? The ball should be at approximately y=200")
