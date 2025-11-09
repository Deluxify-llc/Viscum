"""
Integration tests using real video files
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import pytest
from viscum_core import find_darkest_circle, KalmanTracker


class TestMineralOilVideo:
    """Integration tests using the mineral_oil.mp4 sample video"""

    @pytest.fixture
    def video_path(self):
        """Fixture providing path to test video"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(project_root, "examples", "mineral_oil.mp4")

    @pytest.fixture
    def video_cap(self, video_path):
        """Fixture providing video capture object"""
        if not os.path.exists(video_path):
            pytest.skip(f"Test video not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            pytest.skip(f"Could not open video: {video_path}")

        yield cap
        cap.release()

    def test_video_file_exists(self, video_path):
        """Test that the mineral oil video exists"""
        assert os.path.exists(video_path), \
            "mineral_oil.mp4 should exist in examples/ directory"

    def test_video_properties(self, video_cap):
        """Test that video has expected properties"""
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        assert fps > 0, "FPS should be positive"
        assert frame_count > 0, "Should have at least one frame"
        assert width > 0, "Width should be positive"
        assert height > 0, "Height should be positive"

        print(f"\nVideo properties: {width}x{height} @ {fps}fps, {frame_count} frames")

    def test_can_read_frames(self, video_cap):
        """Test that we can read frames from the video"""
        ret, frame = video_cap.read()

        assert ret, "Should be able to read first frame"
        assert frame is not None, "Frame should not be None"
        assert len(frame.shape) == 3, "Frame should be color (3 channels)"
        assert frame.shape[2] == 3, "Frame should have RGB channels"

    def test_ball_detection_on_sample_frame(self, video_cap):
        """Test ball detection on a sample frame from the video"""
        # Read first frame
        ret, frame = video_cap.read()
        assert ret, "Should be able to read frame"

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Define a sample ROI (center portion of frame)
        height, width = gray.shape
        roi_x1, roi_y1 = width // 4, height // 4
        roi_x2, roi_y2 = 3 * width // 4, 3 * height // 4
        cropped = gray[roi_y1:roi_y2, roi_x1:roi_x2]

        # Try to detect ball
        cx, cy, diameter, confidence = find_darkest_circle(
            cropped,
            expected_radius_range=(5, 50)
        )

        # Should return valid results (even if no ball found)
        assert isinstance(cx, (int, float, type(None)))
        assert isinstance(cy, (int, float, type(None)))
        assert isinstance(diameter, (int, float, type(None)))
        assert isinstance(confidence, (float, type(None)))

        if cx is not None:
            print(f"\nDetected ball at ({cx:.1f}, {cy:.1f}), "
                  f"diameter={diameter:.1f}px, confidence={confidence:.2f}")

    def test_kalman_tracker_on_sequence(self, video_cap):
        """Test Kalman tracker on a short sequence of frames"""
        # Read first few frames and track positions
        positions = []
        tracker = None

        # Process 10 frames
        for i in range(10):
            ret, frame = video_cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            height, width = gray.shape

            # Use center region as ROI
            roi = gray[height//4:3*height//4, width//4:3*width//4]

            # Detect ball
            cx, cy, diameter, confidence = find_darkest_circle(
                roi,
                prev_center=positions[-1] if positions else None,
                expected_radius_range=(5, 50)
            )

            if cx is not None and cy is not None:
                # Initialize tracker on first detection
                if tracker is None:
                    dt = 1.0 / video_cap.get(cv2.CAP_PROP_FPS)
                    tracker = KalmanTracker(cx, cy, dt)

                # Predict and update
                tracker.predict()
                updated = tracker.update([cx, cy])
                positions.append((updated[0], updated[1]))

        # Should have tracked at least a few frames
        assert len(positions) >= 1, "Should detect ball in at least one frame"

        if len(positions) > 1:
            print(f"\nTracked {len(positions)} frames successfully")


class TestVideoProcessingWorkflow:
    """Test the complete video processing workflow"""

    def test_roi_extraction(self):
        """Test ROI extraction from a sample frame"""
        # Create a test frame
        frame = np.random.randint(0, 255, (1080, 1920), dtype=np.uint8)

        # Define ROI
        roi_x1, roi_y1 = 100, 200
        roi_x2, roi_y2 = 300, 400

        # Extract ROI
        roi = frame[roi_y1:roi_y2, roi_x1:roi_x2]

        # Check dimensions
        expected_height = roi_y2 - roi_y1
        expected_width = roi_x2 - roi_x1

        assert roi.shape[0] == expected_height
        assert roi.shape[1] == expected_width

    def test_time_vector_calculation(self):
        """Test time vector calculation from frame numbers"""
        fps = 30.0
        frame_nums = np.array([0, 1, 2, 3, 4, 5])

        time_vec = (frame_nums - frame_nums[0]) / fps

        expected = np.array([0.0, 1/30, 2/30, 3/30, 4/30, 5/30])
        np.testing.assert_array_almost_equal(time_vec, expected)

    def test_velocity_calculation(self):
        """Test velocity calculation from position data"""
        # Simulate ball falling at constant velocity
        fps = 30.0
        time = np.linspace(0, 1, 30)  # 1 second
        position = 100 + 50 * time    # Starting at 100, moving at 50 px/s

        # Calculate velocity using gradient
        velocity = np.gradient(position, time)

        # Velocity should be approximately 50 px/s
        mean_velocity = np.mean(velocity)
        assert 45 < mean_velocity < 55, f"Velocity should be ~50, got {mean_velocity}"

    def test_pixel_to_mm_conversion(self):
        """Test pixel to mm conversion calculation"""
        real_diameter_mm = 3.0
        pixel_diameter = 30.0

        mm_per_pixel = real_diameter_mm / pixel_diameter

        assert mm_per_pixel == pytest.approx(0.1)

        # Test conversion
        pixel_velocity = 100.0  # pixels/s
        mm_velocity = pixel_velocity * mm_per_pixel

        assert mm_velocity == pytest.approx(10.0)  # mm/s


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
