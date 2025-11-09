import cv2
import numpy as np
import matplotlib.pyplot as plt

def find_dark_circle(image, expected_radius_range=(10, 40), search_top_fraction=0.6):
    """
    Find the darkest circular region in the image using a sliding window approach.

    Args:
        image: Grayscale image
        expected_radius_range: (min_radius, max_radius) in pixels
        search_top_fraction: Search only in the top fraction of the image

    Returns:
        (cx, cy, radius, darkness_score) or None
    """
    height, width = image.shape
    search_height = int(height * search_top_fraction)

    best_score = float('inf')  # Lower is better (darker)
    best_result = None

    # Try different radii
    for radius in range(expected_radius_range[0], expected_radius_range[1] + 1, 2):
        # Create circular mask
        mask = np.zeros((radius*2, radius*2), dtype=np.uint8)
        cv2.circle(mask, (radius, radius), radius, 255, -1)

        # Slide the window
        for y in range(radius, search_height - radius, 5):  # Step by 5 for speed
            for x in range(radius, width - radius, 5):
                # Extract region
                region = image[y-radius:y+radius, x-radius:x+radius]

                if region.shape != mask.shape:
                    continue

                # Calculate mean intensity in circular region
                circle_pixels = region[mask > 0]
                mean_intensity = np.mean(circle_pixels)
                std_intensity = np.std(circle_pixels)

                # Score: prefer darker regions with low variance (uniform darkness)
                score = mean_intensity + std_intensity * 0.5

                if score < best_score:
                    best_score = score
                    best_result = (x, y, radius, mean_intensity)

    return best_result

# Test on frame 80
cap = cv2.VideoCapture("IMG_4128.mp4")
cap.set(cv2.CAP_PROP_POS_FRAMES, 80)
ret, frame = cap.read()
cap.release()

if ret:
    # ROI
    roi_x1, roi_y1 = 1000, 1803
    roi_x2, roi_y2 = 1200, 2492

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cropped = gray[roi_y1:roi_y2, roi_x1:roi_x2]

    print("Searching for darkest circular region...")
    result = find_dark_circle(cropped, expected_radius_range=(10, 30), search_top_fraction=0.7)

    if result:
        cx, cy, radius, intensity = result
        print(f"Found ball at: ({cx}, {cy}), radius={radius}, intensity={intensity:.1f}")
        print(f"Expected position: y ≈ 200")
        print(f"Actual detection: y = {cy}")

        # Visualize
        fig, ax = plt.subplots(1, 1, figsize=(6, 12))
        ax.imshow(cropped, cmap='gray')

        circle = plt.Circle((cx, cy), radius, color='red', fill=False, linewidth=2, label=f'Detected (y={cy})')
        ax.add_patch(circle)
        ax.plot(cx, cy, 'rx', markersize=15, markeredgewidth=3)

        ax.axhline(y=200, color='yellow', linestyle='--', linewidth=2, label='Expected (y≈200)')
        ax.set_title(f'Ball Detection: Intensity={intensity:.1f}')
        ax.legend()

        plt.tight_layout()
        plt.savefig('debug_detect/simple_detection.png', dpi=150)
        print("\nSaved to debug_detect/simple_detection.png")

        error = abs(cy - 200)
        if error < 30:
            print(f"✓ SUCCESS! Detection is within 30 pixels of expected position (error={error:.0f}px)")
        else:
            print(f"✗ FAILED! Detection is {error:.0f} pixels off from expected position")
    else:
        print("No ball detected!")
