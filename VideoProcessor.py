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
Python-based solution for finding viscosity.

This module provides necessary implementation to process a video of
ball falling into the liquid of your choice and returns the viscosity.

Authors:
    Aryan Sinha <aryanstarwars@gmail.com>
    Vibhav Durgesh <vibhavd@gmail.com>

Created: 2025-06-15
Version: 1.0
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure, morphology
from scipy.signal import lfilter
from scipy.optimize import curve_fit


# Helper function: polynomial fit for velocity smoothing
def poly3(x, a, b, c, d):
    return a * x ** 3 + b * x ** 2 + c * x + d


# Video file
video_path = 'Video4.mp4'
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Cannot open video {video_path}")

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Hardcoded ROI [x, y, width, height]
roi_pos = [600, 600, 100, 500]

xloc, yloc, frame_num = [], [], []

# Process frames 75 to 235 (1-based indexing in MATLAB, 0-based in Python)
for k in range(0, 65):  # Python index starts at 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, k)
    ret, frame = cap.read()
    if not ret:
        continue

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Crop to ROI
    x, y, w, h = roi_pos
    cropped = gray[y:y + h, x:x + w]

    # Display cropped frame (optional)
    # cv2.imshow('Cropped', cropped)
    # cv2.waitKey(1)

    # Threshold using Otsu
    _, bw = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    bw = cv2.bitwise_not(bw)  # invert

    # Remove small objects (area < 10 pixels)
    bw_clean = morphology.remove_small_objects(bw > 0, min_size=10)
    bw_clean = morphology.remove_small_holes(bw_clean, area_threshold=100)
    bw_clean = bw_clean.astype(np.uint8) * 255

    # Find connected components / contours
    labels = measure.label(bw_clean)
    regions = measure.regionprops(labels)
    if not regions:
        continue

    # Find largest region by major axis length (approximate as max of major axis length)
    major_axes = [region.major_axis_length for region in regions]
    idx = np.argmax(major_axes)
    region = regions[idx]

    ctr = region.centroid  # (row, col)
    diam = np.mean([region.major_axis_length, region.minor_axis_length])

    # Plot for visualization (optional)
    plt.figure(1)
    plt.clf()
    plt.imshow(cropped, cmap='gray')
    plt.plot(ctr[1], ctr[0], 'mx', markersize=10)  # centroid: col=x, row=y
    w_circ = diam
    theta = np.linspace(0, 2 * np.pi, 100)
    x_circ = ctr[1] + w_circ * np.cos(theta)
    y_circ = ctr[0] + w_circ * np.sin(theta)
    plt.plot(x_circ, y_circ, 'm.', linewidth=3)
    plt.title(f'Frame {k + 1}')
    plt.pause(0.2)

    xloc.append(ctr[1])
    yloc.append(ctr[0])
    frame_num.append(k + 1)

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
window_size = 20
b = np.ones(window_size) / window_size
a = 1
yloc_filtered = lfilter(b, a, yloc)

# Compute raw velocity (numerical derivative)
velocity = np.gradient(yloc[24:], time_vec[24:])
velocity_filtered = np.gradient(yloc_filtered[24:], time_vec[24:])

# Fit velocity_filtered with 3rd degree polynomial
popt, _ = curve_fit(poly3, time_vec[24:], velocity_filtered)
curvefit_data = poly3(time_vec[24:], *popt)

# Plot velocity vs time
plt.figure(3, figsize=(6, 3.5))
plt.plot(time_vec[24:], velocity, 'b.', label='Original Velocity')
plt.plot(time_vec[24:], velocity_filtered, 'r.', label='Filtered Velocity', linewidth=1.5)
plt.plot(time_vec[24:], curvefit_data, 'm-', linewidth=2, label='Curve fit Velocity')
plt.xlabel('Time (s)')
plt.ylabel('Velocity (pixels/s)')
plt.title('Velocity vs Time (Smoothed)')
plt.legend()
plt.grid(True)

plt.show()

print(f"Final filtered velocity: {velocity_filtered[-1]:.2f} pixels/s")
