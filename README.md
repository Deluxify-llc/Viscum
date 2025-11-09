# Viscum

**Measure liquid viscosity using just a ball and a camera.**

Viscum is a computer vision-based tool that tracks a ball falling through fluid and calculates viscosity using Stokes' Law. It works well even with opaque or low-contrast fluids, making it ideal for educational and research applications.

## Features

- User-friendly GUI for easy operation
- Advanced ball tracking using Kalman filtering
- Works with low-contrast and opaque fluids
- Automatic ROI (Region of Interest) selection
- Real-time preview and frame navigation
- Calibration mode for validation
- Detailed results visualization with confidence metrics
- Cross-platform support (Windows, macOS, Linux)

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

- Python 3.8 or higher
- A video recording of a ball falling through fluid
- Known values for:
  - Ball diameter (mm)
  - Ball density (kg/m³)
  - Liquid density (kg/m³)
  - Local gravity (m/s²)

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

**Option B: System-wide Installation**

```bash
pip install -r requirements.txt
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
├── ViscumGUI.py           # Main GUI application
├── VideoProcessor.py      # Core tracking algorithm
├── requirements.txt       # Python dependencies
├── run_gui.bat           # Windows launcher
├── run_gui.sh            # macOS/Linux launcher
├── README.md             # This file
├── TUTORIAL_SCRIPT.md    # Video tutorial recording guide
├── examples/             # Sample video file
│   └── mineral_oil.mp4   # Example: ball falling through mineral oil
└── tests/                # Test and debug scripts
    ├── debug_frame.py
    ├── test_first_frame.py
    └── ...

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
- Check Python version: `python3 --version` (must be 3.8+)

### GUI not starting
- Make sure tkinter is available (comes with most Python installations)
- **On macOS**: If using Homebrew Python, install with: `brew install python-tk@3.13` (adjust version)
  - Or use the system Python: `/usr/bin/python3 ViscumGUI.py`
- **On Linux**: Install with: `sudo apt-get install python3-tk`
- Test tkinter availability: `python3 -c "import tkinter"`

## How It Works

Viscum uses:
1. **Darkest Circle Detection**: Finds the ball by looking for the darkest circular region
2. **Kalman Filtering**: Smooths tracking and predicts ball position
3. **Velocity Calculation**: Computes terminal velocity from position data
4. **Stokes' Law**: Calculates viscosity from terminal velocity:
   ```
   η = (d²g(ρ_ball - ρ_fluid)) / (18v)
   ```

## Tips for Best Results

- Use a high-contrast ball (dark ball in light fluid or vice versa)
- Record at high frame rate (60+ FPS recommended)
- Ensure stable lighting
- Keep camera steady (use tripod if possible)
- Use a transparent or semi-transparent container
- Let the ball reach terminal velocity before the ROI
- Use multiple measurements and average results

## License

Copyright 2025 Aryan Sinha

Licensed under the Apache License, Version 2.0

## Authors

- Aryan Sinha
- Vibhav Durgesh

## Contributing

Issues and pull requests are welcome!
