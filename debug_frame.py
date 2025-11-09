import cv2
import numpy as np
import matplotlib.pyplot as plt

# Load video
video_path = "IMG_4128.mp4"
cap = cv2.VideoCapture(video_path)

# Parameters
roi_x1, roi_y1 = 1000, 1803
roi_x2, roi_y2 = 1200, 2492
starting_frame = 80

# Read frame 80
cap.set(cv2.CAP_PROP_POS_FRAMES, starting_frame)
ret, frame = cap.read()

if ret:
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Crop to ROI
    cropped = gray[roi_y1:roi_y2, roi_x1:roi_x2]

    print(f"Frame shape: {frame.shape}")
    print(f"ROI shape: {cropped.shape}")
    print(f"ROI min value: {cropped.min()}, max value: {cropped.max()}")
    print(f"ROI mean: {cropped.mean():.2f}, std: {cropped.std():.2f}")

    # Apply contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(cropped)
    hist_eq = cv2.equalizeHist(cropped)

    print(f"\nEnhanced min value: {enhanced.min()}, max value: {enhanced.max()}")
    print(f"Enhanced mean: {enhanced.mean():.2f}, std: {enhanced.std():.2f}")

    # Save the cropped frame
    cv2.imwrite("debug_detect/raw_frame_80.png", cropped)
    cv2.imwrite("debug_detect/enhanced_frame_80.png", enhanced)
    cv2.imwrite("debug_detect/hist_eq_frame_80.png", hist_eq)

    # Try different thresholding methods ON ENHANCED IMAGE
    _, otsu = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu_inv = cv2.bitwise_not(otsu)

    adaptive = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 2
    )

    # Save thresholded versions
    cv2.imwrite("debug_detect/otsu_frame_80.png", otsu)
    cv2.imwrite("debug_detect/otsu_inv_frame_80.png", otsu_inv)
    cv2.imwrite("debug_detect/adaptive_frame_80.png", adaptive)

    # Try Hough circles on enhanced image with more sensitive parameters
    circles = cv2.HoughCircles(
        enhanced,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=30,
        param2=15,
        minRadius=5,
        maxRadius=80
    )

    if circles is None:
        # Try on histogram equalized version
        circles = cv2.HoughCircles(
            hist_eq,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=30,
            param2=15,
            minRadius=5,
            maxRadius=80
        )

    print(f"\nHough circles detected: {circles.shape if circles is not None else 'None'}")

    if circles is not None:
        circles = np.uint16(np.around(circles))
        print("Circle centers and radii:")
        for i, circle in enumerate(circles[0, :]):
            print(f"  Circle {i}: center=({circle[0]}, {circle[1]}), radius={circle[2]}")

    # Create visualization
    fig, axes = plt.subplots(3, 2, figsize=(12, 16))

    axes[0, 0].imshow(cropped, cmap='gray')
    axes[0, 0].set_title('Original ROI (Very Low Contrast!)')

    axes[0, 1].imshow(enhanced, cmap='gray')
    axes[0, 1].set_title('CLAHE Enhanced')

    axes[1, 0].imshow(hist_eq, cmap='gray')
    axes[1, 0].set_title('Histogram Equalized')

    axes[1, 1].imshow(otsu_inv, cmap='gray')
    axes[1, 1].set_title('Otsu (inverted, on enhanced)')

    axes[2, 0].imshow(adaptive, cmap='gray')
    axes[2, 0].set_title('Adaptive Threshold (on enhanced)')

    # Draw circles if detected on enhanced image
    enhanced_color = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    if circles is not None:
        for circle in circles[0, :]:
            cv2.circle(enhanced_color, (circle[0], circle[1]), circle[2], (255, 0, 0), 2)
            cv2.circle(enhanced_color, (circle[0], circle[1]), 2, (0, 255, 0), 3)

    axes[2, 1].imshow(enhanced_color)
    axes[2, 1].set_title(f'Hough Circles Detected ({circles.shape[1] if circles is not None else 0} circles)')

    plt.tight_layout()
    plt.savefig('debug_detect/analysis_frame_80.png', dpi=150)
    print("\nSaved analysis to debug_detect/analysis_frame_80.png")

else:
    print("Failed to read frame")

cap.release()
print("\nDone! Check the debug_detect folder for images.")
