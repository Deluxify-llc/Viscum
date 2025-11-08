# Copyright 2025 Aryan Sinha
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Ball tracking for viscosity measurement

Tracks a ball falling through fluid and calculates viscosity

Authors: Aryan Sinha, Vibhav Durgesh
"""
import math

import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure, morphology
from scipy.signal import lfilter
from scipy.optimize import curve_fit


# polynomial for smoothing velocity data
def poly3(x, a, b, c, d):
    return a * x ** 3 + b * x ** 2 + c * x + d


class KalmanTracker:
    # Kalman filter to smooth out tracking noise
    def __init__(self, initial_x, initial_y, dt=1.0):
        # state vector: position and velocity
        self.state = np.array([initial_x, initial_y, 0.0, 0.0], dtype=np.float32)

        # transition matrix
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)

        self.Q = np.eye(4, dtype=np.float32) * 0.1
        self.R = np.eye(2, dtype=np.float32) * 10
        self.P = np.eye(4, dtype=np.float32) * 100

    def predict(self):
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.state[:2]

    def update(self, measurement):
        measurement = np.array(measurement, dtype=np.float32)

        y = measurement - (self.H @ self.state)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

        return self.state[:2]


def find_darkest_circle(image, prev_center=None, expected_radius_range=(10, 30), search_fraction=0.8):
    # finds the darkest circular region in the image
    # works better than thresholding for low contrast videos

    height, width = image.shape

    if prev_center is not None:
        cx_prev, cy_prev = prev_center
        search_radius = 100

        # search region - ball is falling so extend downward more
        y_min = max(0, int(cy_prev - search_radius//2))
        y_max = min(height, int(cy_prev + search_radius*2))
        x_min = max(0, int(cx_prev - search_radius))
        x_max = min(width, int(cx_prev + search_radius))
    else:
        # first frame - search upper part of image
        y_min = 0
        y_max = int(height * 0.6)
        x_min = 0
        x_max = width

    best_score = float('inf')
    best_result = None

    # try different ball sizes
    for radius in range(expected_radius_range[0], expected_radius_range[1] + 1, 2):
        mask = np.zeros((radius*2, radius*2), dtype=np.uint8)
        cv2.circle(mask, (radius, radius), radius, 255, -1)

        step = 5 if prev_center is not None else 7
        for y in range(max(y_min, radius), min(y_max, height - radius), step):
            for x in range(max(x_min, radius), min(x_max, width - radius), step):
                region = image[y-radius:y+radius, x-radius:x+radius]

                if region.shape != mask.shape:
                    continue

                circle_pixels = region[mask > 0]
                mean_intensity = np.mean(circle_pixels)
                std_intensity = np.std(circle_pixels)

                # lower score = darker and more uniform
                score = mean_intensity + std_intensity * 0.3

                if prev_center is not None:
                    dist = np.sqrt((x - prev_center[0])**2 + (y - prev_center[1])**2)
                    dy = y - prev_center[1]

                    score += dist * 0.1
                    if dy < 0:  # upward motion is bad
                        score += abs(dy) * 0.5

                if score < best_score:
                    best_score = score
                    best_result = (x, y, radius * 2, mean_intensity)

    if best_result is not None:
        cx, cy, diameter, intensity = best_result
        confidence = min(1.0, (50 - intensity) / 20)
        return cx, cy, diameter, max(confidence, 0.3)

    return None, None, None, None


# load video
video_path = input("file name: ")
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Cannot open video {video_path}")

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"fps: {fps}, frames: {frame_count}")

# get ROI from user
roi_x1 = int(input("ROI x1: "))
roi_y1 = int(input("ROI y1: "))
roi_x2 = int(input("ROI x2: "))
roi_y2 = int(input("ROI y2: "))
roi_pos = [roi_x1, roi_y1, roi_x2-roi_x1, roi_y2 - roi_y1]


xloc, yloc, frame_num = [], [], []
ball_diameters_pixels = []
confidences = []
starting_frame = int(input("starting frame: "))
ending_frame = int(input("ending frame: "))

kalman_tracker = None
prev_center = None
ball_template = None
dt = 1.0 / fps

print("\nProcessing frames...")

import os
debug_dir = "debug_detect"
if not os.path.exists(debug_dir):
    os.makedirs(debug_dir)

# main tracking loop
for k in range(starting_frame, ending_frame):  # Python index starts at 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, k)
    ret, frame = cap.read()
    if not ret:
        print(f"Warning: Could not read frame {k}")
        continue

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    x, y, w, h = roi_pos
    cropped = gray[y:y + h, x:x + w]

    predicted_center = None
    if kalman_tracker is not None:
        predicted_center = kalman_tracker.predict()
        predicted_center = (predicted_center[0], predicted_center[1])

    # detect ball
    cx, cy, diameter_pixels, confidence = find_darkest_circle(
        cropped,
        prev_center=predicted_center if predicted_center is not None else prev_center,
        expected_radius_range=(8, 35)
    )

    if cx is not None:
        center = (cx, cy)
        if kalman_tracker is None:
            print(f"First frame: Found ball at ({cx:.1f}, {cy:.1f}), diameter={diameter_pixels:.1f}")
    else:
        center = None

    # fallback to prediction if detection fails
    if center is None:
        if kalman_tracker is not None:
            print(f"Frame {k}: Detection failed, using Kalman prediction")
            center = predicted_center
            diameter_pixels = ball_diameters_pixels[-1] if ball_diameters_pixels else 30
            confidence = 0.3
        else:
            print(f"Frame {k}: No detection possible, skipping frame")
            continue

    # Initialize Kalman filter on first successful detection
    if kalman_tracker is None:
        kalman_tracker = KalmanTracker(center[0], center[1], dt)
        print(f"Kalman tracker initialized at frame {k}")

    # Update Kalman filter with measurement
    updated_center = kalman_tracker.update([center[0], center[1]])

    # Use Kalman-smoothed position for better accuracy
    ctr = (updated_center[1], updated_center[0])  # Convert to (row, col) for consistency

    ball_diameters_pixels.append(diameter_pixels)
    confidences.append(confidence)

    # Draw visualization circle
    w_circ = diameter_pixels / 2
    theta = np.linspace(0, 2 * np.pi, 100)
    x_circ = center[0] + w_circ * np.cos(theta)
    y_circ = center[1] + w_circ * np.sin(theta)

    # Plot for visualization
    plt.figure(1)
    plt.clf()
    plt.imshow(cropped, cmap='gray')
    plt.plot(center[0], center[1], 'mx', markersize=10, label='Detected')
    if predicted_center is not None:
        plt.plot(predicted_center[0], predicted_center[1], 'b+', markersize=8, label='Predicted')
    plt.plot(x_circ, y_circ, 'm-', linewidth=2)

    # Color code by confidence
    if confidence > 0.7:
        color = 'green'
    elif confidence > 0.4:
        color = 'yellow'
    else:
        color = 'red'

    plt.title(f'Frame {k + 1} | Confidence: {confidence:.2f}', color=color)
    plt.legend()
    plt.pause(0.01)

    # Save debug image for first, middle, and last frames
    if k in [starting_frame, starting_frame + (ending_frame-starting_frame)//2, ending_frame-1]:
        debug_path = os.path.join(debug_dir, f'frame_{k:04d}_conf_{confidence:.2f}.png')
        plt.savefig(debug_path, dpi=100, bbox_inches='tight')
        print(f"Saved debug frame: {debug_path}")

    xloc.append(center[0])
    yloc.append(center[1])
    frame_num.append(k + 1)
    prev_center = center

print(f"\nTracking complete! Successfully tracked {len(xloc)} frames")
print(f"Average confidence: {np.mean(confidences):.2f}")

cap.release()
plt.close(1)

# Convert to numpy arrays
xloc = np.array(xloc)
yloc = np.array(yloc)
frame_num = np.array(frame_num)

# Time vector in seconds
time_vec = (frame_num - frame_num[0]) / fps

# Plot raw position vs time
plt.figure(2, figsize=(6, 3.5))
plt.plot(time_vec, yloc, 'ro-')
plt.xlabel('Time (s)')
plt.ylabel('Y Position (pixels)')
plt.title('Droplet Position vs Time')
plt.grid(True)

# Moving average filter (low-pass)
# Adapt window size based on available frames
num_frames = len(yloc)
window_size = min(20, max(3, num_frames // 3))
b = np.ones(window_size) / window_size
a = 1
yloc_filtered = lfilter(b, a, yloc)

# Compute raw velocity (numerical derivative)
# Start from a point that makes sense based on available data
skip_frames = min(24, max(0, num_frames - 5))  # Ensure we have at least 5 points for velocity

if num_frames > skip_frames + 3:
    velocity = np.gradient(yloc[skip_frames:], time_vec[skip_frames:])
    velocity_filtered = np.gradient(yloc_filtered[skip_frames:], time_vec[skip_frames:])

    # Fit velocity_filtered with 3rd degree polynomial (only if we have enough points)
    if len(velocity_filtered) >= 4:
        popt, _ = curve_fit(poly3, time_vec[skip_frames:], velocity_filtered)
        curvefit_data = poly3(time_vec[skip_frames:], *popt)
    else:
        # Not enough points for polynomial fit, use filtered velocity directly
        curvefit_data = velocity_filtered
        popt = None
else:
    # Very few frames, just compute velocity from all points
    velocity = np.gradient(yloc, time_vec)
    velocity_filtered = np.gradient(yloc_filtered, time_vec)
    curvefit_data = velocity_filtered
    skip_frames = 0
    popt = None

# Plot velocity vs time
plt.figure(3, figsize=(6, 3.5))
plt.plot(time_vec[skip_frames:], velocity, 'b.', label='Original Velocity')
plt.plot(time_vec[skip_frames:], velocity_filtered, 'r.', label='Filtered Velocity', linewidth=1.5)
if popt is not None:
    plt.plot(time_vec[skip_frames:], curvefit_data, 'm-', linewidth=2, label='Curve fit Velocity')
else:
    plt.plot(time_vec[skip_frames:], curvefit_data, 'm.', linewidth=1.5, label='Filtered Velocity (no fit)')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (pixels/s)')
plt.title('Velocity vs Time (Smoothed)')
plt.legend()
plt.grid(True)

# --- NEW CODE FOR PLOTTING DIAMETER ---
# Check if there are diameter measurements before plotting
if len(ball_diameters_pixels) > 0:
    plt.figure(4, figsize=(6, 3.5))
    plt.plot(time_vec, ball_diameters_pixels, 'go-')
    plt.xlabel('Time (s)')
    plt.ylabel('Ball Diameter (pixels)')
    plt.title('Ball Diameter vs. Time')
    plt.grid(True)
else:
    print("\nNo ball diameters were measured, so a graph could not be created.")
# --- END OF NEW CODE ---

# --- CONFIDENCE TRACKING PLOT ---
if len(confidences) > 0:
    plt.figure(5, figsize=(6, 3.5))
    plt.plot(time_vec, confidences, 'bo-')
    plt.axhline(y=0.7, color='g', linestyle='--', label='High confidence')
    plt.axhline(y=0.4, color='orange', linestyle='--', label='Medium confidence')
    plt.xlabel('Time (s)')
    plt.ylabel('Detection Confidence')
    plt.title('Tracking Confidence vs. Time')
    plt.legend()
    plt.ylim([0, 1])
    plt.grid(True)
# --- END CONFIDENCE PLOT ---


plt.show()

# Calculate the average diameter from the collected measurements
if ball_diameters_pixels:
    average_diameter = np.mean(ball_diameters_pixels)
    print(f"\nAverage ball diameter from analyzed frames: {average_diameter:.2f} pixels")
else:
    print("\nCould not detect the ball in any of the frames to calculate the diameter.")

print(f"Final filtered velocity: {velocity_filtered[-1]:.2f} pixels/s")

############################
#        Constants         #
############################

rldiameter = float(input("real diameter of your ball in mm: ")) #3 for me
pdiameter = average_diameter
g = float(input("g value in your area: ")) #9.79 in mine
densityb = float(input("density of your ball: ")) #880 for me
densityl = float(input("density of your liquid: ")) #872 for me
pixeltomm = rldiameter / pdiameter
mmvelocity = velocity_filtered[-1] * pixeltomm
viscosity = (rldiameter / 1000) ** 2 * g * (densityb - densityl) / (18 * mmvelocity / 1000)
print(f"Final mmtopixel: {pixeltomm} mm in a pixel")
print(f"Final mm velocity: {mmvelocity} mm/s")
print(f"Final Fluid Viscosity: {viscosity} mm/s")
cal = input("Was this a calibration test? ")
if cal.strip().lower().__eq__('yes'):
    temp = float(input("What temperature was the liquid at (°C)? "))
    m40 = float(input("Manufacturer value at 40°C (in cP)? "))
    m100 = float(input("Manufacturer value at 100°C (in cP)? "))

    # Constants
    R = 8.314  # J/mol·K

    # Convert to Kelvin
    T40 = 40 + 273.15
    T100 = 100 + 273.15
    T = temp + 273.15

    # Convert viscosities from cP → Pa·s
    m40 *= 1e-3
    m100 *= 1e-3

    # Calculate activation energy and pre-exponential factor
    Ea = R * math.log(m40 / m100) / (1 / T40 - 1 / T100)
    A = m40 / math.exp(Ea / (R * T40))

    # Calculate viscosity at the desired temperature (in Pa·s)
    calculated_visc = A * math.exp(Ea / (R * T))

    print(f"Activation Energy (Ea): {Ea:.2f} J/mol")
    print(f"Pre-exponential Factor (A): {A:.6e} Pa·s")
    print(f"Viscosity at {temp}°C: {calculated_visc:.6f} Pa·s")
    calculated_error = math.fabs((calculated_visc - viscosity)/calculated_visc)
    print(f"Relative error between calculated and observed viscosity: {calculated_error}")