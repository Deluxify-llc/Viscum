# Viscum Algorithm Documentation

This document explains the complete algorithm for measuring fluid viscosity using video analysis and Stokes' Law.

## Overview

The algorithm tracks a ball falling through fluid, measures its terminal velocity, and calculates viscosity using Stokes' Law for drag on a sphere in laminar flow.

---

## Algorithm Steps

### Step 1: Video Input and Preprocessing

**Input:** Video file of ball falling through fluid

**Process:**
1. Load video file using OpenCV's `VideoCapture`
2. Extract video metadata:
   - Frame rate (fps)
   - Total frame count
   - Frame resolution (width × height)
3. Define Region of Interest (ROI):
   - User specifies rectangular area containing ball's path
   - ROI = (x₁, y₁, x₂, y₂) in pixel coordinates
4. Define frame range:
   - Start frame: After ball reaches terminal velocity
   - End frame: Before ball exits ROI

**Output:** Video stream with defined ROI and frame range

---

### Step 2: Ball Detection (Darkest Circle Algorithm)

**Purpose:** Locate the ball center in each frame

**Algorithm:** `find_darkest_circle(image, prev_center, expected_radius_range)`

**Process:**

1. **Localized Search** (if previous center available):
   ```
   search_region = prev_center ± (search_fraction × image_size)
   ```
   - Default search_fraction = 0.8 (80% of image)
   - Reduces false detections and improves speed

2. **Intensity-Based Scoring:**
   ```
   For each candidate position (x, y):
       For each radius r in expected_radius_range:
           circle_mask = create_circle(x, y, r)
           mean_intensity = average(image[circle_mask])
           score = -mean_intensity  (darker = higher score)
   ```
   - Ball must be darkest object in ROI
   - Circular shape assumption

3. **Best Candidate Selection:**
   ```
   (cx, cy, diameter) = argmax(score)
   confidence = normalized_score
   ```
   - Confidence ∈ [0, 1]
   - High confidence (>0.7): Strong detection
   - Low confidence (<0.4): Weak/predicted detection

**Output:** Ball center (cx, cy), diameter, confidence

---

### Step 3: Kalman Filtering (Trajectory Smoothing)

**Purpose:** Smooth noisy position measurements and predict next position

**Kalman Filter State:**
```
State vector: [x, y, vₓ, vᵧ]ᵀ
Where:
  x, y  = ball position (pixels)
  vₓ, vᵧ = ball velocity (pixels/second)
```

**Prediction Step:**
```
State transition matrix F:
F = [1  0  dt  0 ]
    [0  1  0   dt]
    [0  0  1   0 ]
    [0  0  0   1 ]

Predicted state: x̂ₖ₊₁ = F × xₖ
Predicted position: (x̂, ŷ) = x̂ₖ₊₁[0:2]
```

**Update Step:**
```
Measurement: zₖ = [cx, cy]ᵀ from ball detection
Kalman gain: Kₖ = Pₖ Hᵀ (H Pₖ Hᵀ + R)⁻¹
Updated state: xₖ = x̂ₖ + Kₖ(zₖ - H x̂ₖ)
```

**Fallback Strategy:**
- If detection fails: Use Kalman prediction
- If no detection and no tracker: Skip frame
- Confidence for predicted positions = 0.3

**Output:** Smoothed ball position (x, y) for each frame

---

### Step 4: Position Data Collection

**For each frame k in [start_frame, end_frame]:**

1. Detect ball → (cx, cy, diameter, confidence)
2. Kalman predict → (x_pred, y_pred)
3. Kalman update with measurement → (x_smooth, y_smooth)
4. Store data:
   ```
   xloc[k] = x_smooth
   yloc[k] = y_smooth
   frame_num[k] = k
   ball_diameters[k] = diameter
   confidences[k] = confidence
   ```

**Output:**
- Position arrays: xloc[], yloc[]
- Time array: time[] = frame_num[] / fps
- Average ball diameter (pixels)

---

### Step 5: Velocity Calculation

**Purpose:** Extract terminal velocity from position data

**Process:**

1. **Moving Average Filter:**
   ```
   window_size = min(20, max(3, num_frames / 3))
   yloc_filtered = moving_average(yloc, window_size)
   ```
   - Reduces high-frequency noise
   - Adaptive window size based on data length

2. **Skip Acceleration Phase:**
   ```
   skip_frames = min(24, max(0, num_frames - 5))
   ```
   - Removes initial acceleration period
   - Ensures only terminal velocity region is used

3. **Numerical Differentiation:**
   ```
   velocity = dy/dt = gradient(yloc_filtered, time)
   ```
   - Uses numpy.gradient for numerical derivative
   - Units: pixels/second

4. **Polynomial Smoothing (optional):**
   ```
   v(t) = at³ + bt² + ct + d
   Fit parameters [a, b, c, d] to velocity data
   ```
   - Further smooths velocity curve
   - Only if sufficient data (≥4 points)

5. **Terminal Velocity:**
   ```
   v_terminal = velocity_filtered[-1]  (last point)
   ```
   - Assumes terminal velocity reached
   - Units: pixels/second

**Output:** Terminal velocity in pixels/second

---

### Step 6: Unit Conversion (Pixels → Real World)

**Purpose:** Convert pixel measurements to physical units

**Calibration:**
```
Given:
  real_diameter_mm = actual ball diameter (mm)
  pixel_diameter = average measured diameter (pixels)

Conversion factor:
  mm_per_pixel = real_diameter_mm / pixel_diameter
```

**Velocity Conversion:**
```
velocity_mm_s = v_terminal × mm_per_pixel
velocity_m_s = velocity_mm_s / 1000
```

**Output:** Terminal velocity in m/s

---

### Step 7: Viscosity Calculation (Stokes' Law)

**Physical Principle:**

For a sphere falling at terminal velocity through viscous fluid under laminar flow (Re < 1):

```
Drag force = Gravitational force - Buoyancy force
6πηrv = (4/3)πr³(ρ_ball - ρ_fluid)g
```

**Stokes' Law for Viscosity:**
```
η = (d² g (ρ_ball - ρ_fluid)) / (18v)

Where:
  η = dynamic viscosity (Pa·s)
  d = ball diameter (m)
  g = gravitational acceleration (m/s²)
  ρ_ball = ball density (kg/m³)
  ρ_fluid = fluid density (kg/m³)
  v = terminal velocity (m/s)
```

**Implementation:**
```python
ball_diameter_m = real_diameter_mm / 1000
velocity_m_s = velocity_mm_s / 1000

viscosity = (ball_diameter_m² × g × (ρ_ball - ρ_fluid)) / (18 × velocity_m_s)
```

**Output:** Dynamic viscosity in Pa·s (Pascal-seconds)

---

## Optional: Calibration Validation (Arrhenius Equation)

**Purpose:** Validate measurement using known fluid properties

**Arrhenius Equation for Viscosity:**
```
η(T) = A × exp(Eₐ / (R×T))

Where:
  A = pre-exponential factor (Pa·s)
  Eₐ = activation energy (J/mol)
  R = universal gas constant (8.314 J/mol·K)
  T = absolute temperature (K)
```

**Parameter Calculation:**

Given manufacturer data at two temperatures:
```
η₁ at T₁ = 40°C
η₂ at T₂ = 100°C

Solve for Eₐ and A:
  Eₐ = R × ln(η₁/η₂) / (1/T₁ - 1/T₂)
  A = η₁ / exp(Eₐ/(R×T₁))
```

**Expected Viscosity:**
```
η_expected(T_test) = A × exp(Eₐ / (R×T_test))
```

**Error Calculation:**
```
relative_error = |η_expected - η_measured| / η_expected
```

---

## Mathematical Formulas Summary

### 1. Kalman Filter Equations

**State Transition:**
```
xₖ = F xₖ₋₁ + wₖ
zₖ = H xₖ + vₖ

F = [1  0  Δt  0 ]    H = [1 0 0 0]
    [0  1  0   Δt]        [0 1 0 0]
    [0  0  1   0 ]
    [0  0  0   1 ]
```

**Prediction:**
```
x̂ₖ⁻ = F xₖ₋₁
Pₖ⁻ = F Pₖ₋₁ Fᵀ + Q
```

**Update:**
```
Kₖ = Pₖ⁻ Hᵀ (H Pₖ⁻ Hᵀ + R)⁻¹
x̂ₖ = x̂ₖ⁻ + Kₖ(zₖ - H x̂ₖ⁻)
Pₖ = (I - Kₖ H) Pₖ⁻
```

### 2. Moving Average Filter

```
y_filtered[i] = (1/N) Σⱼ₌₀ᴺ⁻¹ y[i-j]
```

### 3. Numerical Gradient

```
dy/dt[i] ≈ (y[i+1] - y[i-1]) / (t[i+1] - t[i-1])
```

### 4. Stokes' Law

```
η = d²g(ρ_s - ρ_f) / (18v)

Reynolds number check:
Re = ρ_f v d / η < 1  (for laminar flow)
```

### 5. Arrhenius Equation

```
η(T) = A exp(Eₐ/RT)

ln(η) = ln(A) + Eₐ/(RT)  (linear form)
```

---

## Algorithm Complexity

**Time Complexity:**
- Ball detection per frame: O(w × h × r)
  - w, h: ROI dimensions
  - r: number of radius values tested
- Kalman filter per frame: O(1)
- Overall: O(n × w × h × r)
  - n: number of frames

**Space Complexity:** O(n)
- Stores position, diameter, confidence for n frames

---

## Assumptions and Limitations

### Assumptions:
1. **Laminar Flow:** Reynolds number Re < 1
2. **Terminal Velocity:** Ball has reached constant velocity
3. **Spherical Ball:** Perfect sphere geometry
4. **Newtonian Fluid:** Constant viscosity
5. **Infinite Fluid:** Wall effects negligible (container >> ball)
6. **Dark Ball:** Ball is darkest object in ROI

### Limitations:
1. **Accuracy:** Typical error 5-15%
2. **Resolution:** Ball must be > 8 pixels diameter
3. **Contrast:** Requires clear ball-fluid contrast
4. **Frame Rate:** Higher FPS improves velocity accuracy
5. **Container Size:** Must allow terminal velocity to develop

---

## Error Sources

1. **Measurement Errors:**
   - Ball diameter uncertainty: ±0.1 mm typical
   - Density uncertainties: ±1-5 kg/m³
   - Frame rate accuracy

2. **Detection Errors:**
   - Pixel quantization (±0.5 pixel)
   - Non-circular ball projection
   - Lighting variations

3. **Physical Errors:**
   - Wall effects (if container too small)
   - Temperature variations
   - Non-spherical ball
   - Ball rotation effects

4. **Processing Errors:**
   - Numerical differentiation noise
   - Insufficient terminal velocity region
   - Acceleration phase included

**Total Uncertainty:** Typically 5-15% for well-controlled experiments

---

## Validation Methods

1. **Calibration Mode:**
   - Test with known fluid (e.g., standard mineral oil)
   - Compare measured vs. manufacturer specifications
   - Validate Arrhenius equation parameters

2. **Consistency Checks:**
   - Average detection confidence > 0.6
   - Velocity curve shows plateau (terminal velocity)
   - Ball diameter consistent across frames (σ < 2 pixels)

3. **Reynolds Number:**
   ```
   Re = ρ_fluid × v × d / η
   ```
   - Must be < 1 for Stokes' Law validity
   - Warning if 0.1 < Re < 1 (transitional)
   - Error if Re > 1 (turbulent)

---

## References

1. **Stokes' Law:**
   - Stokes, G. G. (1851). "On the Effect of the Internal Friction of Fluids on the Pendulum"

2. **Kalman Filtering:**
   - Kalman, R. E. (1960). "A New Approach to Linear Filtering and Prediction Problems"

3. **Viscosity Measurement:**
   - ASTM D445 - Standard Test Method for Kinematic Viscosity

4. **Arrhenius Equation:**
   - Arrhenius, S. (1889). "Über die Reaktionsgeschwindigkeit bei der Inversion von Rohrzucker durch Säuren"
