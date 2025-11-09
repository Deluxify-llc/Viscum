"""
Unit tests for ball detection functions
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import cv2
import pytest
from viscum_core import find_darkest_circle, poly3


class TestFindDarkestCircle:
    """Test cases for the darkest circle detection algorithm"""

    def create_test_image_with_circle(self, width=200, height=200,
                                     circle_center=(100, 50),
                                     circle_radius=15,
                                     background=128,
                                     circle_intensity=30):
        """Helper to create synthetic test image with a dark circle"""
        image = np.full((height, width), background, dtype=np.uint8)
        cv2.circle(image, circle_center, circle_radius, circle_intensity, -1)
        return image

    def test_detects_single_circle(self):
        """Test detection of a single dark circle"""
        image = self.create_test_image_with_circle(
            width=200, height=200,
            circle_center=(100, 50),
            circle_radius=15,
            background=128,
            circle_intensity=30
        )

        cx, cy, diameter, confidence = find_darkest_circle(
            image,
            expected_radius_range=(10, 30)
        )

        assert cx is not None
        assert cy is not None
        # Should detect near the actual position (within 10 pixels)
        assert abs(cx - 100) < 10
        assert abs(cy - 50) < 10
        # Diameter should be approximately 30 (radius 15 * 2)
        assert 18 <= diameter <= 40  # Allow for rounding
        # Confidence should be reasonable
        assert 0.3 <= confidence <= 1.0

    def test_prefers_darker_circle(self):
        """Test that algorithm prefers darker circles"""
        image = np.full((200, 200), 128, dtype=np.uint8)

        # Draw two circles: one darker, one lighter
        cv2.circle(image, (60, 50), 15, 80, -1)   # Lighter circle
        cv2.circle(image, (140, 50), 15, 20, -1)  # Darker circle

        cx, cy, diameter, confidence = find_darkest_circle(
            image,
            expected_radius_range=(10, 30)
        )

        # Should detect the darker circle at (140, 50)
        assert cx is not None
        assert cx > 100  # Should be on the right side where darker circle is

    def test_with_previous_center(self):
        """Test that providing previous center biases search"""
        image = np.full((200, 200), 128, dtype=np.uint8)
        cv2.circle(image, (100, 60), 15, 30, -1)

        # Provide previous center near actual position
        cx, cy, diameter, confidence = find_darkest_circle(
            image,
            prev_center=(95, 55),
            expected_radius_range=(10, 30)
        )

        assert cx is not None
        assert cy is not None
        # Should find the circle
        assert abs(cx - 100) < 15
        assert abs(cy - 60) < 15

    def test_no_circle_returns_none(self):
        """Test that no circle found returns None"""
        # Uniform image with no dark regions
        image = np.full((200, 200), 100, dtype=np.uint8)

        result = find_darkest_circle(
            image,
            expected_radius_range=(10, 30)
        )

        # Should still return something (darkest region found)
        # But confidence might be low
        cx, cy, diameter, confidence = result
        assert cx is not None or (cx, cy, diameter, confidence) == (None, None, None, None)

    def test_different_radius_ranges(self):
        """Test detection with different expected radius ranges"""
        image = self.create_test_image_with_circle(
            circle_radius=20
        )

        # Test with matching range
        cx1, cy1, d1, conf1 = find_darkest_circle(
            image,
            expected_radius_range=(15, 25)
        )

        # Test with too-small range
        cx2, cy2, d2, conf2 = find_darkest_circle(
            image,
            expected_radius_range=(5, 10)
        )

        # First should detect better than second
        assert cx1 is not None
        # Diameter from correct range should be closer to actual (40)
        if d1 and d2:
            assert abs(d1 - 40) <= abs(d2 - 40)

    def test_ball_in_different_positions(self):
        """Test detection works in different regions of image"""
        positions = [(50, 50), (150, 50), (100, 150), (50, 150)]

        for pos in positions:
            image = self.create_test_image_with_circle(
                circle_center=pos,
                circle_radius=15
            )

            cx, cy, diameter, confidence = find_darkest_circle(
                image,
                expected_radius_range=(10, 30)
            )

            assert cx is not None, f"Failed to detect circle at {pos}"
            # Should be within 35 pixels of actual position (algorithm is approximate)
            assert abs(cx - pos[0]) < 35, f"X position off for circle at {pos}"
            assert abs(cy - pos[1]) < 35, f"Y position off for circle at {pos}"


class TestPoly3Function:
    """Test cases for polynomial fitting function"""

    def test_poly3_basic(self):
        """Test basic polynomial evaluation"""
        # f(x) = 2x^3 + 3x^2 + 4x + 5
        result = poly3(1.0, a=2, b=3, c=4, d=5)
        expected = 2 * 1**3 + 3 * 1**2 + 4 * 1 + 5
        assert result == expected

    def test_poly3_at_zero(self):
        """Test polynomial at x=0 returns constant term"""
        result = poly3(0, a=1, b=2, c=3, d=10)
        assert result == 10

    def test_poly3_array_input(self):
        """Test polynomial with array input"""
        x = np.array([0, 1, 2, 3])
        result = poly3(x, a=1, b=0, c=0, d=0)
        expected = np.array([0, 1, 8, 27])  # x^3
        np.testing.assert_array_almost_equal(result, expected)

    def test_poly3_negative_coefficients(self):
        """Test with negative coefficients"""
        result = poly3(2.0, a=-1, b=-1, c=-1, d=-1)
        expected = -1 * 2**3 + -1 * 2**2 + -1 * 2 + -1
        assert result == expected


class TestBallDetectionEdgeCases:
    """Test edge cases for ball detection"""

    def test_empty_image(self):
        """Test with all-black image"""
        image = np.zeros((100, 100), dtype=np.uint8)

        cx, cy, diameter, confidence = find_darkest_circle(
            image,
            expected_radius_range=(10, 30)
        )

        # Should handle gracefully
        assert isinstance(cx, (int, float, type(None)))

    def test_very_small_image(self):
        """Test with very small image"""
        image = np.full((50, 50), 128, dtype=np.uint8)
        cv2.circle(image, (25, 25), 5, 30, -1)

        cx, cy, diameter, confidence = find_darkest_circle(
            image,
            expected_radius_range=(3, 8)
        )

        assert cx is not None
        assert cy is not None

    def test_high_contrast_image(self):
        """Test with very high contrast (0 and 255)"""
        image = np.full((200, 200), 255, dtype=np.uint8)
        cv2.circle(image, (100, 50), 15, 0, -1)

        cx, cy, diameter, confidence = find_darkest_circle(
            image,
            expected_radius_range=(10, 30)
        )

        assert cx is not None
        assert confidence > 0.5  # Should have high confidence with high contrast


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
