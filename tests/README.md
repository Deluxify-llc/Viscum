# Viscum Test Suite

Automated tests for the Viscum ball tracking system.

## Test Structure

```
tests/
├── __init__.py                  # Package marker
├── test_kalman_tracker.py       # Unit tests for Kalman filter
├── test_ball_detection.py       # Unit tests for ball detection
├── test_integration.py          # Integration tests with real video
└── README.md                    # This file
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest

# Or with verbose output
pytest -v

# Or with coverage report
pytest --cov=. --cov-report=html
```

### Run Specific Test Files

```bash
# Run only Kalman tracker tests
pytest tests/test_kalman_tracker.py

# Run only ball detection tests
pytest tests/test_ball_detection.py

# Run only integration tests
pytest tests/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_kalman_tracker.py::TestKalmanTracker

# Run a specific test function
pytest tests/test_kalman_tracker.py::TestKalmanTracker::test_initialization
```

### Run Tests by Marker

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=. --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### Current Coverage

The test suite covers:
- **KalmanTracker class**: Initialization, prediction, update, edge cases
- **find_darkest_circle function**: Detection, confidence, edge cases
- **poly3 function**: Polynomial evaluation
- **Integration**: Video loading, frame processing, tracking workflow

## Test Categories

### Unit Tests

Fast tests that test individual functions/classes in isolation:
- `test_kalman_tracker.py` - Kalman filter mathematics
- `test_ball_detection.py` - Ball detection algorithm

### Integration Tests

Tests that use real video files and test the full workflow:
- `test_integration.py` - Tests with `mineral_oil.mp4`

## Writing New Tests

### Test Naming Convention

- File: `test_<module_name>.py`
- Class: `Test<Feature>`
- Function: `test_<what_it_tests>`

### Example Test

```python
import pytest
from VideoProcessor import KalmanTracker

class TestKalmanTracker:
    def test_initialization(self):
        """Test that Kalman tracker initializes correctly"""
        tracker = KalmanTracker(100.0, 200.0, dt=0.1)

        assert tracker.state[0] == 100.0
        assert tracker.state[1] == 200.0
```

### Using Fixtures

```python
@pytest.fixture
def sample_image():
    """Fixture providing a test image"""
    image = np.zeros((100, 100), dtype=np.uint8)
    return image

def test_with_fixture(sample_image):
    """Test using the fixture"""
    assert sample_image.shape == (100, 100)
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=. --cov-report=xml
```

## Troubleshooting

### Import Errors

If you get import errors, make sure you're running from the project root:
```bash
cd /path/to/Viscum
pytest
```

### Video File Not Found

Integration tests require `examples/mineral_oil.mp4`. If missing:
```bash
# Tests will be skipped with a message
pytest tests/test_integration.py -v
```

### Matplotlib Display Issues

Tests that use matplotlib may show plots. To run headless:
```bash
export MPLBACKEND=Agg
pytest
```

## Dependencies

Tests require:
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- All dependencies from requirements.txt

Install with:
```bash
pip install -r requirements.txt
```
