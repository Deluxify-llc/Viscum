# Viscum
Measure liquid viscosity using just a ball and a camera.

## How to Use

**GUI (Easiest):**

Run `python ViscumGUI.py` or double-click `run_gui.bat` on Windows

1. Load your video
2. Select the ROI (region where ball falls)
3. Set frame range
4. Enter ball/liquid properties
5. Run tracking

**Command Line:**

```bash
python VideoProcessor.py
```

Then enter the parameters when prompted.

## What It Does

Tracks a ball falling through fluid and calculates viscosity using Stokes' Law.

Works well even with opaque/low-contrast fluids.

## Requirements

```bash
pip install -r requirements.txt
```
