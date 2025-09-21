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
video_path = input("file name: ") #'Video4.mp4'
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Cannot open video {video_path}")

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Hardcoded ROI [x, y, width, height]
roi_x1 = int(input("ROI x1: ")) #600
roi_y1 = int(input("ROI y1: ")) # 600
roi_x2 = int(input("ROI x2: ")) # 700
roi_y2 = int(input("ROI y2: ")) # 1100
roi_pos = [roi_x1, roi_y1, roi_x2-roi_x1, roi_y2 - roi_y1]

xloc, yloc, frame_num = [], [], []
ball_diameters_pixels = []  # List to store the diameter of the ball in pixels for each frame
starting_frame = int(input("starting frame: ")) #0
ending_frame = int(input("ending frame: ")) #65
# Process frames 75 to 235 (1-based indexing in MATLAB, 0-based in Python)
for k in range(starting_frame, ending_frame):  # Python index starts at 0
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

    # Calculate the diameter of the ball in pixels
    # We take the average of the major and minor axis lengths for a more robust diameter estimate
    diameter_pixels = np.mean([region.major_axis_length, region.minor_axis_length])
    ball_diameters_pixels.append(diameter_pixels)

    w_circ = diameter_pixels
    theta = np.linspace(0, 2 * np.pi, 100)
    x_circ = ctr[1] + w_circ * np.cos(theta)
    y_circ = ctr[0] + w_circ * np.sin(theta)

    # Plot for visualization (optional)
    plt.figure(1)
    plt.clf()
    plt.imshow(cropped, cmap='gray')
    plt.plot(ctr[1], ctr[0], 'mx', markersize=10)  # centroid: col=x, row=y
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
densityb = float(input("density of your ball: ")) #936 for me
densityl = float(input("density of your liquid: ")) #872 for me
pixeltomm = rldiameter / pdiameter
mmvelocity = velocity_filtered[-1] * pixeltomm
viscosity = (rldiameter / 1000) ** 2 * g * (densityb - densityl) / (18 * mmvelocity / 1000)
print(f"Final mmtopixel: {pixeltomm} mm in a pixel")
print(f"Final mm velocity: {mmvelocity} mm/s")
print(f"Final Fluid Viscosity: {viscosity} mm/s")