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

Command-line script that tracks a ball falling through fluid and calculates viscosity
using Stokes' Law. Uses computer vision to track the ball and Kalman filtering to
smooth the trajectory.

Authors: Aryan Sinha, Vibhav Durgesh
"""
import argparse
import math
import os

import cv2
import numpy as np

# Parse command-line arguments before importing matplotlib
parser = argparse.ArgumentParser()
parser.add_argument('--save-plots', action='store_true', help='Save plots to files instead of showing them')
parser.add_argument('--plots-dir', type=str, default='debug_detect', help='Directory to save plots')
args = parser.parse_args()

# Set matplotlib backend to non-interactive if saving plots
import matplotlib
if args.save_plots:
    matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from scipy.signal import lfilter
from scipy.optimize import curve_fit

# Import core functions from viscum_core library
from viscum_core import KalmanTracker, find_darkest_circle, poly3


# ==============================================================================
# STEP 1: Load Video and Get User Input
# ==============================================================================

# Load the video file
video_path = input("file name: ")
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise IOError(f"Cannot open video {video_path}")

# Get video properties
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"fps: {fps}, frames: {frame_count}, resolution: {frame_width}x{frame_height}")

# Get Region of Interest (ROI) from user
# ROI defines the rectangular area where the ball falls
roi_x1 = int(input("ROI x1: "))
roi_y1 = int(input("ROI y1: "))
roi_x2 = int(input("ROI x2: "))
roi_y2 = int(input("ROI y2: "))

# Validate ROI coordinates
if roi_x2 <= roi_x1:
    raise ValueError(f"Invalid ROI: x2 ({roi_x2}) must be greater than x1 ({roi_x1})")
if roi_y2 <= roi_y1:
    raise ValueError(f"Invalid ROI: y2 ({roi_y2}) must be greater than y1 ({roi_y1})")
if roi_x1 < 0 or roi_y1 < 0:
    raise ValueError(f"Invalid ROI: coordinates must be non-negative (x1={roi_x1}, y1={roi_y1})")
if roi_x2 > frame_width or roi_y2 > frame_height:
    raise ValueError(f"Invalid ROI: coordinates exceed frame bounds ({frame_width}x{frame_height}). Got x2={roi_x2}, y2={roi_y2}")

# roi_pos format: [x, y, width, height]
roi_pos = [roi_x1, roi_y1, roi_x2 - roi_x1, roi_y2 - roi_y1]
print(f"ROI size: {roi_pos[2]}x{roi_pos[3]} pixels")

# Get frame range for tracking
starting_frame = int(input("starting frame: "))
ending_frame = int(input("ending frame: "))

# Validate frame range
if starting_frame < 0:
    raise ValueError(f"Invalid starting frame: {starting_frame} (must be >= 0)")
if ending_frame > frame_count:
    raise ValueError(f"Invalid ending frame: {ending_frame} (video only has {frame_count} frames)")
if ending_frame <= starting_frame:
    raise ValueError(f"Invalid frame range: ending frame ({ending_frame}) must be greater than starting frame ({starting_frame})")
if ending_frame - starting_frame < 5:
    print(f"Warning: Frame range is very short ({ending_frame - starting_frame} frames). Results may be inaccurate.")

print(f"Tracking {ending_frame - starting_frame} frames ({(ending_frame - starting_frame) / fps:.2f} seconds)")

# ==============================================================================
# STEP 2: Initialize Tracking Variables
# ==============================================================================

# Lists to store tracking results
xloc, yloc, frame_num = [], [], []  # Ball position and frame numbers
ball_diameters_pixels = []  # Measured ball diameters
confidences = []  # Detection confidence scores

# Initialize Kalman filter (will be created on first detection)
kalman_tracker = None
prev_center = None  # Previous ball center for localized search
dt = 1.0 / fps  # Time step between frames (seconds)

# Create debug output directory
debug_dir = "debug_detect"
if not os.path.exists(debug_dir):
    os.makedirs(debug_dir)

print("\nProcessing frames...")

# ==============================================================================
# STEP 3: Main Tracking Loop
# ==============================================================================

# Process each frame in the specified range
for k in range(starting_frame, ending_frame):
    # Seek to the specific frame in the video
    cap.set(cv2.CAP_PROP_POS_FRAMES, k)
    ret, frame = cap.read()
    if not ret:
        print(f"Warning: Could not read frame {k}")
        continue

    # Convert frame to grayscale for processing
    # Ball detection works better with grayscale images
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Extract the Region of Interest (ROI)
    # This focuses processing on the area where the ball is falling
    x, y, w, h = roi_pos
    cropped = gray[y:y + h, x:x + w]

    # Get predicted position from Kalman filter (if initialized)
    # The Kalman filter predicts where the ball should be based on its motion model
    predicted_center = None
    if kalman_tracker is not None:
        predicted_center = kalman_tracker.predict()
        predicted_center = (predicted_center[0], predicted_center[1])

    # Detect the ball using the darkest circle algorithm
    # Uses prediction or previous position to guide the search
    cx, cy, diameter_pixels, confidence = find_darkest_circle(
        cropped,
        prev_center=predicted_center if predicted_center is not None else prev_center,
        expected_radius_range=(8, 35)
    )

    # Process detection result
    if cx is not None:
        center = (cx, cy)
        if kalman_tracker is None:
            print(f"First frame: Found ball at ({cx:.1f}, {cy:.1f}), diameter={diameter_pixels:.1f}")
    else:
        center = None

    # Fallback strategy: use Kalman prediction if detection fails
    # This helps maintain tracking even when the ball is temporarily obscured
    if center is None:
        if kalman_tracker is not None:
            print(f"Frame {k}: Detection failed, using Kalman prediction")
            center = predicted_center
            diameter_pixels = ball_diameters_pixels[-1] if ball_diameters_pixels else 30
            confidence = 0.3  # Lower confidence for predicted positions
        else:
            # No detection and no tracker yet - skip this frame
            print(f"Frame {k}: No detection possible, skipping frame")
            continue

    # Initialize Kalman filter on first successful detection
    # The Kalman filter learns the ball's velocity and smooths the trajectory
    if kalman_tracker is None:
        kalman_tracker = KalmanTracker(center[0], center[1], dt)
        print(f"Kalman tracker initialized at frame {k}")

    # Update Kalman filter with the current measurement
    # This corrects the prediction with the actual observed position
    updated_center = kalman_tracker.update([center[0], center[1]])

    # Store measurements for later analysis
    ball_diameters_pixels.append(diameter_pixels)
    confidences.append(confidence)

    # ==============================================================================
    # Visualization: Draw tracking overlay on each frame
    # ==============================================================================

    # Create circle outline to show detected ball position
    w_circ = diameter_pixels / 2
    theta = np.linspace(0, 2 * np.pi, 100)
    x_circ = center[0] + w_circ * np.cos(theta)
    y_circ = center[1] + w_circ * np.sin(theta)

    # Display current frame with tracking overlay (only if not saving plots)
    if not args.save_plots:
        plt.figure(1)
        plt.clf()
        plt.imshow(cropped, cmap='gray')
        plt.plot(center[0], center[1], 'mx', markersize=10, label='Detected')

        # Show Kalman prediction (if available) to see prediction accuracy
        if predicted_center is not None:
            plt.plot(predicted_center[0], predicted_center[1], 'b+', markersize=8, label='Predicted')

        # Draw circle around detected ball
        plt.plot(x_circ, y_circ, 'm-', linewidth=2)

        # Color-code the title based on detection confidence
        # Green = high confidence, Yellow = medium, Red = low/predicted
        if confidence > 0.7:
            color = 'green'
        elif confidence > 0.4:
            color = 'yellow'
        else:
            color = 'red'

        plt.title(f'Frame {k + 1} | Confidence: {confidence:.2f}', color=color)
        plt.legend()
        plt.pause(0.01)  # Brief pause to update display

    # Save debug images for key frames (first, middle, last)
    # This helps diagnose tracking issues later
    if k in [starting_frame, starting_frame + (ending_frame-starting_frame)//2, ending_frame-1]:
        debug_path = os.path.join(debug_dir, f'frame_{k:04d}_conf_{confidence:.2f}.png')
        plt.savefig(debug_path, dpi=100, bbox_inches='tight')
        print(f"Saved debug frame: {debug_path}")

    # Record position and frame number for analysis
    xloc.append(center[0])
    yloc.append(center[1])
    frame_num.append(k + 1)
    prev_center = center  # Save for next frame's search hint

print(f"\nTracking complete! Successfully tracked {len(xloc)} frames")
print(f"Average confidence: {np.mean(confidences):.2f}")

cap.release()
plt.close(1)

# ==============================================================================
# STEP 4: Position and Velocity Analysis
# ==============================================================================

# Convert tracking data to numpy arrays for numerical processing
xloc = np.array(xloc)
yloc = np.array(yloc)
frame_num = np.array(frame_num)

# Create time vector: convert frame numbers to elapsed time in seconds
time_vec = (frame_num - frame_num[0]) / fps

# Plot raw ball position vs time
plt.figure(2, figsize=(6, 3.5))
plt.plot(time_vec, yloc, 'ro-')
plt.xlabel('Time (s)')
plt.ylabel('Y Position (pixels)')
plt.title('Droplet Position vs Time')
plt.grid(True)

# Apply moving average filter to smooth position data
# This reduces measurement noise before calculating velocity
num_frames = len(yloc)
window_size = min(20, max(3, num_frames // 3))  # Adapt to available data
b = np.ones(window_size) / window_size  # Moving average coefficients
a = 1
yloc_filtered = lfilter(b, a, yloc)

# Calculate velocity from position data using numerical differentiation
# Skip initial frames where the ball may still be accelerating
skip_frames = min(24, max(0, num_frames - 5))  # Ensure at least 5 points remain

if num_frames > skip_frames + 3:
    # Sufficient data: compute velocities using gradient (numerical derivative)
    velocity = np.gradient(yloc[skip_frames:], time_vec[skip_frames:])
    velocity_filtered = np.gradient(yloc_filtered[skip_frames:], time_vec[skip_frames:])

    # Fit smoothed velocity with polynomial for even better smoothing
    # This helps extract the terminal velocity accurately
    if len(velocity_filtered) >= 4:
        popt, _ = curve_fit(poly3, time_vec[skip_frames:], velocity_filtered)
        curvefit_data = poly3(time_vec[skip_frames:], *popt)
    else:
        # Not enough points for polynomial fit
        curvefit_data = velocity_filtered
        popt = None
else:
    # Very few frames: use all available data
    velocity = np.gradient(yloc, time_vec)
    velocity_filtered = np.gradient(yloc_filtered, time_vec)
    curvefit_data = velocity_filtered
    skip_frames = 0
    popt = None

# Plot velocity vs time to visualize ball's motion
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

# Plot measured ball diameter over time
# This helps verify that ball size detection was consistent
if len(ball_diameters_pixels) > 0:
    plt.figure(4, figsize=(6, 3.5))
    plt.plot(time_vec, ball_diameters_pixels, 'go-')
    plt.xlabel('Time (s)')
    plt.ylabel('Ball Diameter (pixels)')
    plt.title('Ball Diameter vs. Time')
    plt.grid(True)
else:
    print("\nNo ball diameters were measured, so a graph could not be created.")

# Plot tracking confidence over time
# Shows quality of ball detection throughout the video
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

# Save plots to files or display them
if args.save_plots:
    # Save all figures to files
    print(f"\nSaving plots to {args.plots_dir}/...")

    plt.figure(2)
    plt.savefig(os.path.join(args.plots_dir, 'plot_position.png'), dpi=100, bbox_inches='tight')
    print(f"Saved: {os.path.join(args.plots_dir, 'plot_position.png')}")

    plt.figure(3)
    plt.savefig(os.path.join(args.plots_dir, 'plot_velocity.png'), dpi=100, bbox_inches='tight')
    print(f"Saved: {os.path.join(args.plots_dir, 'plot_velocity.png')}")

    if len(ball_diameters_pixels) > 0:
        plt.figure(4)
        plt.savefig(os.path.join(args.plots_dir, 'plot_diameter.png'), dpi=100, bbox_inches='tight')
        print(f"Saved: {os.path.join(args.plots_dir, 'plot_diameter.png')}")

    if len(confidences) > 0:
        plt.figure(5)
        plt.savefig(os.path.join(args.plots_dir, 'plot_confidence.png'), dpi=100, bbox_inches='tight')
        print(f"Saved: {os.path.join(args.plots_dir, 'plot_confidence.png')}")

    plt.close('all')  # Close all figures
    print("All plots saved successfully.")
else:
    # Display all plots (original behavior for command-line use)
    plt.show()

# Calculate average ball diameter in pixels
# This is needed to convert pixel measurements to real-world units
if ball_diameters_pixels:
    average_diameter = np.mean(ball_diameters_pixels)
    print(f"\nAverage ball diameter from analyzed frames: {average_diameter:.2f} pixels")
else:
    print("\nCould not detect the ball in any of the frames to calculate the diameter.")

print(f"Final filtered velocity: {velocity_filtered[-1]:.2f} pixels/s")

# ==============================================================================
# STEP 5: Viscosity Calculation Using Stokes' Law
# ==============================================================================

# Get physical parameters from user
# These are needed to convert pixel measurements to real-world values
real_diameter_mm = float(input("real diameter of your ball in mm: "))  # Real ball diameter (e.g., 3 mm)
pixel_diameter = average_diameter  # Ball diameter in pixels (measured from video)
g = float(input("g value in your area: "))  # Local gravity in m/s² (e.g., 9.79)
ball_density_kg_m3 = float(input("density of your ball: "))  # Ball density in kg/m³ (e.g., 880)
liquid_density_kg_m3 = float(input("density of your liquid: "))  # Liquid density in kg/m³ (e.g., 872)

# Validate physical parameters
if real_diameter_mm <= 0:
    raise ValueError(f"Invalid ball diameter: {real_diameter_mm} mm (must be positive)")
if real_diameter_mm > 50:
    print(f"Warning: Ball diameter ({real_diameter_mm} mm) is unusually large. Are you sure?")

if g <= 0 or g > 15:
    raise ValueError(f"Invalid gravity: {g} m/s² (typical range: 9.78-9.82 m/s²)")

if ball_density_kg_m3 <= 0:
    raise ValueError(f"Invalid ball density: {ball_density_kg_m3} kg/m³ (must be positive)")
if liquid_density_kg_m3 <= 0:
    raise ValueError(f"Invalid liquid density: {liquid_density_kg_m3} kg/m³ (must be positive)")

if ball_density_kg_m3 <= liquid_density_kg_m3:
    raise ValueError(f"Ball density ({ball_density_kg_m3} kg/m³) must be greater than liquid density ({liquid_density_kg_m3} kg/m³) for the ball to sink")

# Calculate pixel-to-millimeter conversion factor
mm_per_pixel = real_diameter_mm / pixel_diameter

# Convert velocity from pixels/s to mm/s
velocity_mm_s = velocity_filtered[-1] * mm_per_pixel

# Calculate viscosity using Stokes' Law for a falling sphere
# Formula: η = (d²g(ρ_ball - ρ_fluid)) / (18v)
# Where:
#   η = dynamic viscosity (Pa·s)
#   d = ball diameter (m)
#   g = gravitational acceleration (m/s²)
#   ρ_ball, ρ_fluid = densities (kg/m³)
#   v = terminal velocity (m/s)

# Check for zero velocity to avoid division by zero
if velocity_mm_s == 0:
    print("\n⚠ WARNING: Ball velocity is zero!")
    print("This usually means the ball was not successfully tracked.")
    print("Please check:")
    print("  - ROI includes the ball's falling path")
    print("  - Frame range captures ball motion")
    print("  - Ball is visible and contrasts with background")
    viscosity = float('inf')  # Set to infinity to indicate error
else:
    viscosity = (real_diameter_mm / 1000) ** 2 * g * (ball_density_kg_m3 - liquid_density_kg_m3) / (18 * velocity_mm_s / 1000)

# Display results
print(f"Final mm per pixel: {mm_per_pixel} mm/pixel")
print(f"Final velocity: {velocity_mm_s} mm/s")
print(f"Final Fluid Viscosity: {viscosity} Pa·s")

# ==============================================================================
# STEP 6: Calibration Mode (Optional)
# ==============================================================================
# If this is a calibration test with a fluid of known viscosity,
# we can validate our measurement using the Arrhenius equation

is_calibration = input("Was this a calibration test? ")
if is_calibration.strip().lower().__eq__('yes'):
    # Get calibration data
    test_temperature_C = float(input("What temperature was the liquid at (°C)? "))
    manufacturer_visc_40C_cP = float(input("Manufacturer value at 40°C (in cP)? "))
    manufacturer_visc_100C_cP = float(input("Manufacturer value at 100°C (in cP)? "))

    # Universal gas constant
    R = 8.314  # J/mol·K

    # Convert all temperatures to Kelvin
    # (Arrhenius equation requires absolute temperature)
    T_40C_kelvin = 40 + 273.15
    T_100C_kelvin = 100 + 273.15
    test_temperature_kelvin = test_temperature_C + 273.15

    # Convert viscosities from centipoise (cP) to Pascal-seconds (Pa·s)
    # 1 cP = 0.001 Pa·s
    manufacturer_visc_40C_Pa_s = manufacturer_visc_40C_cP * 1e-3
    manufacturer_visc_100C_Pa_s = manufacturer_visc_100C_cP * 1e-3

    # Calculate Arrhenius equation parameters from manufacturer data
    # Arrhenius equation: η(T) = A * exp(Ea / (R*T))
    # Using two known points, we can solve for Ea and A
    activation_energy = R * math.log(manufacturer_visc_40C_Pa_s / manufacturer_visc_100C_Pa_s) / (1 / T_40C_kelvin - 1 / T_100C_kelvin)
    pre_exponential_factor = manufacturer_visc_40C_Pa_s / math.exp(activation_energy / (R * T_40C_kelvin))

    # Calculate expected viscosity at the test temperature
    # This is what the manufacturer's data predicts
    expected_viscosity = pre_exponential_factor * math.exp(activation_energy / (R * test_temperature_kelvin))

    # Display calibration results
    print(f"Activation Energy (Ea): {activation_energy:.2f} J/mol")
    print(f"Pre-exponential Factor (A): {pre_exponential_factor:.6e} Pa·s")
    print(f"Expected viscosity at {test_temperature_C}°C: {expected_viscosity:.6f} Pa·s")

    # Calculate relative error to assess measurement accuracy
    relative_error = math.fabs((expected_viscosity - viscosity) / expected_viscosity)
    print(f"Relative error between expected and measured viscosity: {relative_error:.4f} ({relative_error*100:.2f}%)")