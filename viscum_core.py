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
Viscum Core Library

Core functions and classes for ball tracking viscosity measurement.
This module contains only the reusable components without script execution.

Authors: Aryan Sinha, Vibhav Durgesh
"""
import cv2
import numpy as np


def poly3(x, a, b, c, d):
    """Polynomial for smoothing velocity data"""
    return a * x ** 3 + b * x ** 2 + c * x + d


class KalmanTracker:
    """Kalman filter to smooth out tracking noise"""

    def __init__(self, initial_x, initial_y, dt=1.0):
        """
        Initialize Kalman tracker

        Args:
            initial_x: Initial x position
            initial_y: Initial y position
            dt: Time step (1/fps)
        """
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
        """Predict next state"""
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.state[:2]

    def update(self, measurement):
        """Update state with measurement"""
        measurement = np.array(measurement, dtype=np.float32)

        y = measurement - (self.H @ self.state)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P

        return self.state[:2]


def find_darkest_circle(image, prev_center=None, expected_radius_range=(10, 30), search_fraction=0.8):
    """
    Finds the darkest circular region in the image
    Works better than thresholding for low contrast videos

    Args:
        image: Grayscale image
        prev_center: Previous ball center (x, y) for localized search
        expected_radius_range: (min_radius, max_radius) in pixels
        search_fraction: Fraction of image to search (unused, kept for compatibility)

    Returns:
        (cx, cy, diameter, confidence) or (None, None, None, None)
    """
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
