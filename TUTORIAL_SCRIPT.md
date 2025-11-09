# Viscum Tutorial Recording Script

## Screen Recording Setup

### Recommended Tools:
- **macOS**: QuickTime Player (built-in) - File > New Screen Recording
- **Alternative**: OBS Studio (free, more features)
- **Simple**: macOS Screenshot tool (Cmd+Shift+5)

### Recording Settings:
- Resolution: 1920x1080 or 1280x720
- Frame rate: 30 fps
- Audio: Optional (can add voiceover later or use captions)
- Save as: `viscum_tutorial.mp4`

---

## Tutorial Script - Step by Step

### Scene 1: Introduction (5 seconds)
**Action**: Show the Viscum project folder
**Say/Caption**: "Welcome to Viscum - Measure viscosity using computer vision"

---

### Scene 2: Launching the Application (10 seconds)
**Action**:
1. Open Terminal
2. Navigate to Viscum folder
3. Run: `./run_gui.sh`
4. Show the GUI window opening

**Say/Caption**: "Launch Viscum by running ./run_gui.sh"

---

### Scene 3: Load Video (15 seconds)
**Action**:
1. Click "Browse Video" button
2. Navigate to `examples/mineral_oil.mp4`
3. Select and open
4. Show video info displayed (FPS, frames)

**Say/Caption**: "Step 1: Load your video of a ball falling through fluid"

**Highlight**: FPS and frame count displayed

---

### Scene 4: Select ROI (20 seconds)
**Action**:
1. Click "Select ROI on Video" button
2. Click and drag to select the region where the ball falls
3. Show the green rectangle on the preview
4. Alternatively, show manual coordinate entry

**Say/Caption**: "Step 2: Select the Region of Interest where the ball travels"

**Tip**: "Make sure the ROI captures the full path of the ball"

---

### Scene 5: Set Frame Range (25 seconds)
**Action**:
1. Use the frame navigation slider
2. Find the frame where ball enters ROI (note the number)
3. Enter in "Start Frame" field
4. Navigate to find where ball exits ROI
5. Enter in "End Frame" field
6. Click "Preview Frame" to verify

**Say/Caption**: "Step 3: Set the start and end frames for tracking"

**Highlight**:
- Use navigation buttons (◀◀ ◀ ▶ ▶▶)
- Frame counter shows current position

---

### Scene 6: Enter Ball Properties (15 seconds)
**Action**:
1. Enter ball diameter: e.g., "3.0" mm
2. Enter ball density: e.g., "880" kg/m³

**Say/Caption**: "Step 4: Enter the known properties of your ball"

**Show example values**:
- Diameter: 3.0 mm
- Density: 880 kg/m³

---

### Scene 7: Enter Liquid Properties (15 seconds)
**Action**:
1. Enter liquid density: e.g., "872" kg/m³
2. Enter gravity: e.g., "9.79" m/s²

**Say/Caption**: "Step 5: Enter your liquid properties and local gravity"

**Show example values**:
- Density: 872 kg/m³
- Gravity: 9.79 m/s²

---

### Scene 8: Optional Calibration (10 seconds)
**Action**:
1. Check "This is a calibration test" (if applicable)
2. Show the additional fields appearing
3. Enter temperature and manufacturer values

**Say/Caption**: "Optional: Enable calibration mode to validate results"

---

### Scene 9: Run Tracking (30 seconds)
**Action**:
1. Click "Run Tracking" button
2. Show progress bar moving
3. Show status changing to "Running tracking..."
4. Wait for completion
5. Show "Tracking complete!" status

**Say/Caption**: "Step 6: Click Run Tracking and wait for the analysis to complete"

**Highlight**: Progress bar and status updates

---

### Scene 10: View Results (30 seconds)
**Action**:
1. Results window pops up
2. Scroll through the results showing:
   - Average Ball Diameter
   - Final Velocity (pixels/s)
   - Pixel to mm Conversion
   - Velocity (mm/s)
   - **MEASURED VISCOSITY** (highlighted)
3. Show calibration results if applicable (Activation Energy, Error)
4. Scroll through full output at bottom

**Say/Caption**: "Step 7: Review your results - the measured viscosity is shown here"

**Highlight**: The measured viscosity value in the results

---

### Scene 11: Interpreting Results (15 seconds)
**Action**:
1. Point to key metrics in results window
2. Show the confidence metric if visible
3. Show full output log

**Say/Caption**: "The tool provides detailed metrics including velocity, diameter measurements, and final viscosity"

---

### Scene 12: Closing (5 seconds)
**Action**:
1. Close results window
2. Show the main GUI again

**Say/Caption**: "That's it! Viscum makes viscosity measurement simple and accessible"

---

## After Recording Checklist

- [ ] Review the video for clarity
- [ ] Add captions/annotations if needed
- [ ] Trim any unnecessary parts
- [ ] Export as MP4 (H.264 codec recommended)
- [ ] Keep file size under 25MB for GitHub
- [ ] Name it: `viscum_tutorial.mp4` or `tutorial_demo.mp4`

## Adding Video to Repository

### Option 1: Add to Repository
```bash
mv ~/path/to/your/recording.mp4 examples/tutorial_demo.mp4
git add examples/tutorial_demo.mp4
git commit -m "Add tutorial video demonstrating Viscum workflow"
git push origin main
```

### Option 2: Upload to YouTube/Vimeo (Recommended for large files)
- Upload to YouTube as unlisted/public
- Add link to README.md
- Keep repository size smaller

### Option 3: GitHub Release
- Create a release on GitHub
- Attach video as release asset
- Link in README

---

## Tips for Better Recording

1. **Clean workspace**: Close unnecessary windows
2. **Zoom in**: Make sure UI elements are clearly visible
3. **Slow down**: Move cursor deliberately, pause between actions
4. **Highlight**: Use cursor to point at important elements
5. **No mistakes**: If you make a mistake, pause and start that section again
6. **Lighting**: If showing hardware setup, ensure good lighting
7. **Audio**: If adding voiceover, use a quiet room
8. **Length**: Keep it under 3 minutes for engagement

---

## Sample Parameters for mineral_oil.mp4

You can use these as example values:

- **Ball Diameter**: 3.0 mm
- **Ball Density**: 880 kg/m³ (typical for polyethylene)
- **Liquid Density**: 872 kg/m³ (mineral oil)
- **Gravity**: 9.79 m/s² (varies by location)
- **ROI**: Adjust based on where ball travels in video
- **Frame Range**: Find frames where ball is in steady motion

For calibration (if mineral oil specs are known):
- **Temperature**: Actual test temperature
- **Viscosity @ 40°C**: Check manufacturer data
- **Viscosity @ 100°C**: Check manufacturer data
