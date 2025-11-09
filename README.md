# Viscum

**Measure liquid viscosity using just a ball and a camera.**

Viscum is a computer vision-based tool that tracks a ball falling through fluid and calculates viscosity using Stokes' Law. It works well even with opaque or low-contrast fluids, making it ideal for educational and research applications.

## Features

- **User-friendly GUI** with intuitive interface
- **Multi-language support** - Automatically detects your system language
  - Fully supported: English, Spanish (Español)
  - Partial support: Chinese (中文), Hindi (हिन्दी), French (Français), German (Deutsch)
  - Easy to add new languages
- **Interactive tooltips** - Hover over any field for detailed explanations
- **Advanced ball tracking** using Kalman filtering
- **Works with low-contrast and opaque fluids**
- **Automatic ROI** (Region of Interest) selection
- **Real-time preview** and frame navigation
- **Calibration mode** for validation with known fluids
- **Detailed results** visualization with confidence metrics
- **Cross-platform support** (Windows, macOS, Linux)

## Quick Start

```bash
# 1. Clone and enter the directory
git clone <repository-url>
cd Viscum

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux (Windows: venv\Scripts\activate)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the GUI
chmod +x run_gui.sh  # macOS/Linux only (only needed once)
./run_gui.sh         # macOS/Linux
# or double-click run_gui.bat on Windows
```

**Note:** If you encounter tkinter errors on macOS, see the Installation section below.

## Prerequisites

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
  - Make sure to check "Add Python to PATH" during installation on Windows
- A video recording of a ball falling through fluid
- Known values for:
  - Ball diameter (mm)
  - Ball density (kg/m³)
  - Liquid density (kg/m³)
  - Local gravity (m/s²)

**Check your Python installation:**
```bash
python --version   # or python3 --version
pip --version      # or pip3 --version
```

If Python is installed but `python` command is not found, try `python3` instead.

## Installation

### Step 1: Clone or Download the Repository

```bash
git clone <repository-url>
cd Viscum
```

Or download and extract the ZIP file.

### Step 2: Set Up Python Environment

**Option A: Using Virtual Environment (Recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

**If `pip` is not found**, try one of these alternatives:
```bash
pip3 install -r requirements.txt           # Use pip3 instead
python -m pip install -r requirements.txt  # Use python's pip module
python3 -m pip install -r requirements.txt # Use python3's pip module
```

**Option B: System-wide Installation**

```bash
pip install -r requirements.txt
```

Or if `pip` is not found:
```bash
pip3 install -r requirements.txt
# or
python3 -m pip install -r requirements.txt
```

**Note for macOS Users:** If you get tkinter errors, install python-tk:
```bash
brew install python-tk@3.13  # Adjust version as needed
```

Then recreate your virtual environment:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This will install:
- numpy (< 2.0)
- opencv-python
- scikit-image
- scipy
- matplotlib
- Pillow

## Running Viscum

### Option 1: GUI (Recommended)

**On Windows:**
- Double-click `run_gui.bat`

**On macOS/Linux:**

First, make the script executable (only needed once):
```bash
chmod +x run_gui.sh
```

Then run it:
```bash
./run_gui.sh
```

**Alternative:** If you have the virtual environment activated, run directly:
```bash
python ViscumGUI.py
```

Or without activating venv:
```bash
python3 ViscumGUI.py
```

### Option 2: Command Line

```bash
python3 VideoProcessor.py
```

Then follow the prompts to enter parameters.

## How to Use the GUI

### 1. Load Your Video
- Click **"Browse Video"** and select your video file (.mp4, .avi, .mov, .mkv)
- Video information (FPS, frame count) will be displayed

### 2. Select the ROI (Region of Interest)
- Click **"Select ROI on Video"**
- Click and drag on the preview to select the area where the ball falls
- Or manually enter coordinates in the X1, Y1, X2, Y2 fields

### 3. Set Frame Range
- Enter the **Start Frame** (when ball enters ROI)
- Enter the **End Frame** (before ball exits ROI)
- Use **"Preview Frame"** to navigate and find the right frames
- Use the navigation controls (◀◀ ◀ ▶ ▶▶) to scrub through the video

### 4. Enter Ball Properties
- **Diameter (mm)**: Real-world diameter of the ball
- **Density (kg/m³)**: Density of the ball material

### 5. Enter Liquid Properties
- **Density (kg/m³)**: Density of the liquid
- **Gravity (m/s²)**: Local gravitational acceleration (typically 9.79-9.81)

### 6. (Optional) Calibration Mode
- Check **"This is a calibration test"** if you want to validate results
- Enter:
  - Temperature (°C)
  - Manufacturer viscosity at 40°C (cP)
  - Manufacturer viscosity at 100°C (cP)
- The tool will calculate expected viscosity and show the error

### 7. Run Tracking
- Click **"Run Tracking"**
- Wait for processing to complete
- View results in the popup window

### Example Parameters (for mineral_oil.mp4)

Want to test the tool quickly? Use these values with the included `examples/mineral_oil.mp4`:

```
Video File: examples/mineral_oil.mp4
ROI Coordinates:
  - X1: 300
  - Y1: 100
  - X2: 500
  - Y2: 800

Frame Range:
  - Start Frame: 10
  - End Frame: 150

Ball Properties:
  - Diameter: 3 mm
  - Density: 880 kg/m³

Liquid Properties:
  - Density: 872 kg/m³
  - Gravity: 9.79 m/s²

Calibration (optional):
  - Temperature: 25°C
  - Viscosity at 40°C: 65 cP
  - Viscosity at 100°C: 8.8 cP
```

These values should give you a viscosity measurement around 0.06-0.08 Pa·s with ~5-10% error.

## Understanding Results

The results window will show:
- **Average Ball Diameter**: Measured ball size in pixels
- **Final Velocity**: Ball's terminal velocity
- **Pixel to mm Conversion**: Calibration factor
- **Velocity (mm/s)**: Terminal velocity in real units
- **Measured Viscosity**: Calculated fluid viscosity (Pa·s)

If in calibration mode:
- **Activation Energy & Pre-exponential Factor**: Arrhenius equation parameters
- **Expected Viscosity**: Calculated from manufacturer specs
- **Relative Error**: Accuracy of measurement

## Project Structure

```
Viscum/
├── ViscumGUI.py               # Main GUI application
├── VideoProcessor.py          # Core tracking script (command-line)
├── viscum_core.py             # Core library (reusable functions/classes)
├── translations.py            # Multi-language support (6 languages)
├── tooltip_helper.py          # Interactive tooltip system
├── requirements.txt           # Python dependencies (includes test deps)
├── pytest.ini                 # Test configuration
├── run_gui.bat                # Windows launcher
├── run_gui.sh                 # macOS/Linux launcher
├── README.md                  # This file
├── LICENSE                    # Apache 2.0 license
├── .gitignore                 # Git ignore rules
├── docs/                      # Documentation
│   ├── README.md              # Documentation index
│   ├── ALGORITHM.md           # Detailed algorithm documentation
│   ├── FLOWCHART.md           # Mermaid flowcharts
│   ├── TUTORIAL_SCRIPT.md     # Video tutorial recording guide
│   ├── flowchart-detailed.png # (Add this) Full algorithm flowchart
│   └── flowchart-simplified.png # (Add this) Simple flowchart for slides
├── examples/                  # Sample video file
│   └── mineral_oil.mp4        # Example: ball falling through mineral oil
└── tests/                     # Test suite
    ├── __init__.py            # Test package
    ├── README.md              # Test documentation
    ├── test_kalman_tracker.py # Kalman filter tests (9 tests)
    ├── test_ball_detection.py # Ball detection tests (13 tests)
    └── test_integration.py    # Integration tests (9 tests)

Note: A debug_detect/ directory will be created automatically when you run tracking.
```

## Troubleshooting

### "Could not open video file"
- Make sure the video file path is correct
- Try a different video format (.mp4 is most reliable)
- Check that opencv-python is properly installed

### Ball not detected
- Ensure the ROI captures the full path of the ball
- Adjust the frame range to capture smooth motion
- Try videos with better contrast
- Make sure the ball is the darkest object in the ROI

### Import errors
- Make sure all dependencies are installed: `pip install -r requirements.txt`
  - If `pip` not found, use: `python3 -m pip install -r requirements.txt`
- Check Python version: `python3 --version` (must be 3.8+)

### "pip: command not found" or "pip is not recognized"
- **Option 1**: Use `pip3` instead of `pip`
- **Option 2**: Use `python -m pip` or `python3 -m pip`
- **Option 3 (Windows)**: Reinstall Python and check "Add Python to PATH"
- **Option 4 (macOS/Linux)**: Install pip with `python3 -m ensurepip --upgrade`

### GUI not starting
- Make sure tkinter is available (comes with most Python installations)
- **On macOS**: If using Homebrew Python, install with: `brew install python-tk@3.13` (adjust version)
  - Or use the system Python: `/usr/bin/python3 ViscumGUI.py`
- **On Linux**: Install with: `sudo apt-get install python3-tk`
- Test tkinter availability: `python3 -c "import tkinter"`

## How It Works

Viscum measures viscosity through a 7-step computer vision and physics algorithm:

1. **Video Input**: Load video and define ROI (Region of Interest)
2. **Ball Detection**: Locate ball using darkest circle algorithm
3. **Kalman Filtering**: Smooth trajectory and predict position
4. **Position Tracking**: Record ball position over time
5. **Velocity Calculation**: Compute terminal velocity using numerical differentiation
6. **Unit Conversion**: Convert pixels to real-world measurements
7. **Stokes' Law**: Calculate viscosity from terminal velocity

**Core Equation (Stokes' Law):**
```
η = (d²g(ρ_ball - ρ_fluid)) / (18v)

Where:
  η = dynamic viscosity (Pa·s)
  d = ball diameter (m)
  g = gravity (m/s²)
  ρ = density (kg/m³)
  v = terminal velocity (m/s)
```

**📖 For detailed algorithm documentation, see [ALGORITHM.md](docs/ALGORITHM.md)**

## Tips for Best Results

- Use a high-contrast ball (dark ball in light fluid or vice versa)
- Record at high frame rate (60+ FPS recommended)
- Ensure stable lighting
- Keep camera steady (use tripod if possible)
- Use a transparent or semi-transparent container
- Let the ball reach terminal velocity before the ROI
- Use multiple measurements and average results

## Frequently Asked Questions (FAQ)

### What video formats work best?
MP4 format with H.264 encoding is most reliable across platforms. AVI, MOV, and MKV also work. Avoid heavily compressed formats.

### How do I know if my ROI is correct?
The ROI (Region of Interest) should:
- Fully contain the ball's path from top to bottom
- Have minimal extra space around the ball
- Not include container edges or other objects
- Be centered on the falling path

Use the **Preview Frame** feature to visually verify the ball stays within the ROI throughout its fall.

### What does 'confidence' mean in the results?
Confidence indicates how certain the algorithm is about ball detection:
- **Green (>0.7)**: High confidence - ball clearly detected
- **Yellow (0.4-0.7)**: Medium confidence - detection may be approximate
- **Red (<0.4)**: Low confidence - using Kalman prediction

Average confidence should be >0.6 for reliable results.

### My tracking fails or gives wrong results. What should I check?

1. **Ball contrast**: Is the ball the darkest object in the ROI?
2. **Lighting**: Are there shadows or reflections interfering?
3. **Frame range**: Did you skip the acceleration phase at the start?
4. **ROI size**: Is the ROI too large or including background objects?
5. **Ball size**: Is the ball within the expected radius range (8-35 pixels)?

### How accurate are the viscosity measurements?
Accuracy depends on:
- Video quality and frame rate
- Proper calibration (ball diameter, densities)
- Ball reaching terminal velocity
- Laminar flow conditions (Reynolds number < 1)

Typical accuracy: **5-15% error** for well-controlled experiments. Use calibration mode with known fluids to validate.

### Can I use this with transparent or light-colored balls?
The current algorithm works best with **dark balls** in light fluids. For light balls:
- Try inverting the video colors in a video editor first
- Or use a contrasting background
- Future versions may support bright object detection

### What ball sizes work best?
- **Too small** (<2mm): Hard to track accurately
- **Optimal**: 3-6mm diameter balls
- **Too large** (>10mm): May not reach terminal velocity in reasonable container height

The ball should be clearly visible but small enough to have measurable fall velocity.

### Why do I need manufacturer viscosity values for calibration?
Calibration mode uses the **Arrhenius equation** to predict viscosity at your test temperature based on manufacturer data at 40°C and 100°C. This helps validate your measurement accuracy. It's optional but recommended for learning.

### Can I use this for non-Newtonian fluids?
This tool assumes **Newtonian fluids** (constant viscosity). Non-Newtonian fluids (shear-thinning, shear-thickening) will give inconsistent results because Stokes' Law doesn't apply.

### What camera/phone should I use?
Any smartphone or camera that can record:
- **Minimum**: 30 FPS, 720p resolution
- **Recommended**: 60+ FPS, 1080p resolution
- **Best**: 120+ FPS for fast-falling balls

Higher frame rates improve velocity measurement accuracy.

### Can I use Viscum in my language?
Yes! Viscum supports multiple languages with automatic detection:
- **Fully translated**: English, Spanish (Español)
- **Partially translated**: Chinese (中文), Hindi (हिन्दी), French (Français), German (Deutsch)

The GUI automatically detects your system language. Missing translations fall back to English.

**To add or improve translations:**
1. Edit `translations.py`
2. Add your language code to `SUPPORTED_LANGUAGES`
3. Copy the English translations and translate the values
4. Submit a pull request!

**Tooltips**: Hover over any field for detailed explanations (available in all languages).

## Running Tests

Viscum includes a comprehensive test suite to ensure reliability.

### Install Test Dependencies

If you haven't already installed test dependencies:

```bash
pip install pytest pytest-cov
```

**If `pip` is not found**, try:
```bash
pip3 install pytest pytest-cov
# or
python -m pip install pytest pytest-cov
# or
python3 -m pip install pytest pytest-cov
```

Or use the requirements file (already includes test dependencies):

```bash
pip install -r requirements.txt
```

To update to the latest versions:

```bash
pip install --upgrade pytest pytest-cov
# or if pip is not found:
python3 -m pip install --upgrade pytest pytest-cov
```

### Run All Tests

```bash
# From project root
pytest

# Or with verbose output
pytest -v

# Or with coverage report
pytest --cov=viscum_core --cov-report=term-missing
```

### Run Specific Tests

```bash
# Run only Kalman tracker tests
pytest tests/test_kalman_tracker.py

# Run only ball detection tests
pytest tests/test_ball_detection.py

# Run only integration tests
pytest tests/test_integration.py -v
```

### View Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=viscum_core --cov-report=html

# Open in browser (macOS)
open htmlcov/index.html
```

### Test Coverage

The test suite includes:
- **31 tests total** covering core functionality
- **Unit tests**: Kalman filter, ball detection algorithm
- **Integration tests**: Real video processing with `mineral_oil.mp4`
- **97% code coverage** of core modules

See `tests/README.md` for detailed testing documentation.

## License

Copyright 2025 Aryan Sinha

Licensed under the Apache License, Version 2.0

## Authors

- Aryan Sinha
- Vibhav Durgesh

## Contributing

Issues and pull requests are welcome!
