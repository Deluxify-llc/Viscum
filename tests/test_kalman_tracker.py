"""
Unit tests for KalmanTracker class
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest
from viscum_core import KalmanTracker


class TestKalmanTracker:
    """Test cases for the Kalman filter tracking implementation"""

    def test_initialization(self):
        """Test that Kalman tracker initializes with correct state"""
        tracker = KalmanTracker(100.0, 200.0, dt=0.1)

        # Check initial state
        assert tracker.state[0] == 100.0  # x position
        assert tracker.state[1] == 200.0  # y position
        assert tracker.state[2] == 0.0    # x velocity
        assert tracker.state[3] == 0.0    # y velocity

        # Check state vector shape
        assert tracker.state.shape == (4,)

        # Check transition matrix has dt incorporated
        assert tracker.F[0, 2] == pytest.approx(0.1, abs=1e-6)  # dt in position-velocity coupling
        assert tracker.F[1, 3] == pytest.approx(0.1, abs=1e-6)

    def test_predict_no_velocity(self):
        """Test prediction when object is stationary"""
        tracker = KalmanTracker(100.0, 200.0, dt=1.0)

        # Predict next position (should stay same with zero velocity)
        predicted = tracker.predict()

        assert predicted[0] == pytest.approx(100.0, abs=0.01)
        assert predicted[1] == pytest.approx(200.0, abs=0.01)

    def test_predict_with_velocity(self):
        """Test prediction when object is moving"""
        tracker = KalmanTracker(100.0, 200.0, dt=1.0)

        # Set initial velocity
        tracker.state[2] = 10.0  # x velocity
        tracker.state[3] = 20.0  # y velocity

        # Predict next position
        predicted = tracker.predict()

        # Position should be initial + velocity * dt
        assert predicted[0] == pytest.approx(110.0, abs=0.01)
        assert predicted[1] == pytest.approx(220.0, abs=0.01)

    def test_update_measurement(self):
        """Test that update corrects position based on measurement"""
        tracker = KalmanTracker(100.0, 200.0, dt=1.0)

        # Update with a new measurement
        measurement = [105.0, 205.0]
        updated = tracker.update(measurement)

        # Updated position should move toward measurement
        assert 100.0 < updated[0] < 105.0
        assert 200.0 < updated[1] < 205.0

    def test_predict_update_cycle(self):
        """Test full predict-update cycle simulating ball falling"""
        tracker = KalmanTracker(100.0, 100.0, dt=0.1)

        # Simulate ball falling with constant velocity
        measurements = [
            [100.0, 110.0],
            [100.0, 120.0],
            [100.0, 130.0],
            [100.0, 140.0],
            [100.0, 150.0],
        ]

        for measurement in measurements:
            tracker.predict()
            updated = tracker.update(measurement)

        # After several updates, tracker should learn the velocity
        # Y velocity should be positive and significant (at least 50 pixels/second)
        assert tracker.state[3] > 50.0  # Y velocity should be positive and significant

    def test_noise_rejection(self):
        """Test that Kalman filter smooths noisy measurements"""
        tracker = KalmanTracker(100.0, 100.0, dt=1.0)

        # Measurements with noise around true trajectory
        true_positions = [(100, 100 + i * 10) for i in range(10)]
        noisy_measurements = [
            (x + np.random.normal(0, 2), y + np.random.normal(0, 2))
            for x, y in true_positions
        ]

        errors = []
        for i, measurement in enumerate(noisy_measurements):
            predicted = tracker.predict()
            updated = tracker.update(measurement)

            # Calculate error between filtered and true position
            true_y = true_positions[i][1]
            error = abs(updated[1] - true_y)
            errors.append(error)

        # After a few iterations, filtered position should be more accurate
        # than raw measurements (errors should decrease)
        assert np.mean(errors[-3:]) < 5.0  # Final errors should be small


class TestKalmanTrackerEdgeCases:
    """Test edge cases and error conditions"""

    def test_negative_dt(self):
        """Test that tracker works with small dt"""
        tracker = KalmanTracker(100.0, 200.0, dt=0.01)
        assert tracker.F[0, 2] == pytest.approx(0.01, abs=1e-6)

    def test_large_position_values(self):
        """Test with large coordinate values (e.g., 4K video)"""
        tracker = KalmanTracker(3840.0, 2160.0, dt=1.0)

        measurement = [3850.0, 2170.0]
        updated = tracker.update(measurement)

        assert updated[0] > 3840.0
        assert updated[1] > 2160.0

    def test_zero_position(self):
        """Test initialization at origin"""
        tracker = KalmanTracker(0.0, 0.0, dt=1.0)

        assert tracker.state[0] == 0.0
        assert tracker.state[1] == 0.0

        predicted = tracker.predict()
        assert predicted[0] == pytest.approx(0.0, abs=0.01)
        assert predicted[1] == pytest.approx(0.0, abs=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
