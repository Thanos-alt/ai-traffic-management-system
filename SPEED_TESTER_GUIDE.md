# Speed Tester - Usage Guide

## 🚀 Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Launch Speed Tester

```bash
python speed_tester.py
```

---

## 🎯 Features Overview

The **Speed Tester** is an interactive GUI tool with the following capabilities:

✅ **Load & Analyze Videos** - Import video files or use live camera  
✅ **Calibration Tool** - Measure pixels-to-meter ratio accurately  
✅ **Manual Speed Input** - Record speeds manually  
✅ **Real-time Graphs** - Visualize speed over time  
✅ **Statistics** - Track avg, max, min speeds  
✅ **Export Results** - Save to CSV, JSON, or TXT  

---

## 📋 Step-by-Step Guide

### 1️⃣ Load a Video or Camera

**Option A: Load Video File**
- Click **📁 Load Video**
- Select your video file (.mp4, .avi, .mov, etc.)
- Video will load and display

**Option B: Load Camera** 
- Click **📷 Load Camera**
- Live camera feed will start

### 2️⃣ Calibrate (Critical for Accuracy!)

**Why calibrate?** Speed calculation depends on knowing how many pixels = 1 meter in the real world.

**Method 1: Using Known Reference Object**
1. Click **⚙️ Calibration Mode**
2. In the video, identify an object with known size (e.g., car width = 1.8m, lane = 3.3m)
3. Click on video to draw measurement line
4. Update **Pixels/Meter** value based on calculation
5. Click **⚙️ Calibration Mode** again to exit

**Method 2: Direct Input**
- If you know the calibration value, enter it in **Pixels/Meter** spinbox
- Example: Lane = 3m, measured pixels = 60 → PPM = 20

### 3️⃣ Record Speed Measurements

**Automatic (Future Enhancement)**
- System detects vehicles and calculates speeds

**Manual Input**
1. Click **📏 Measure Speed**
2. Enter Vehicle ID (e.g., 1, 2, 3)
3. Enter Speed in km/h
4. Click **Record**
5. Repeat for multiple vehicles

### 4️⃣ Analyze Results

**Live Statistics**
- Watch stats update in real-time:
  - 🚗 Vehicles (unique vehicles tracked)
  - 📊 Avg Speed (average km/h)
  - ⬆️ Max Speed (highest recorded)
  - ⬇️ Min Speed (lowest recorded)
  - 📈 Measurements (total data points)
  - ⚙️ PPM (pixels per meter)

**View Graph**
- Click **📊 Show Graph** to see speed trend
- Visual representation of speed over time

### 5️⃣ Export Results

**Supported Formats**
- CSV (Excel-compatible)
- JSON (Data interchange format)
- TXT (Plain text report)

**Export Steps**
1. Click **💾 Export Results**
2. Choose location and format
3. File will be saved

---

## 🎮 Keyboard Controls

| Control | Action |
|---------|--------|
| **Play/Pause** | Toggle video playback |
| **Reset** | Clear all data and start over |
| **Progress Bar** | Drag to seek through video |

---

## ⚙️ Configuration

### Pixels Per Meter (Most Important!)

**How to calculate:**
```
PPM = pixel_distance / real_world_distance

Example:
- You see a 3-meter lane in video
- Lane spans 60 pixels
- PPM = 60 / 3 = 20 pixels/meter
```

**Common values:**
- Highway view: 15-25 PPM
- Close-up view: 30-50 PPM
- Wide view: 5-15 PPM

### FPS (Frames Per Second)

**Auto-detected** from video file or camera  
**Default**: 30 FPS

---

## 📊 Understanding Statistics

### Average Speed
```
Average of all recorded speeds
= Sum of speeds / Number of vehicles
```

### Max/Min Speed
```
Highest/Lowest speed recorded
Useful for:
- Identifying fastest/slowest vehicles
- Detecting anomalies
```

### Measurements Count
```
Total number of speed recordings
Higher count = More reliable data
```

---

## 💾 Export Formats and Usage

### CSV Format
```csv
Vehicle ID,Speed (km/h),Speed (mph),Distance (m),Timestamp
1,65.50,40.68,15.3,2024-03-29T10:30:45
2,72.10,44.80,18.5,2024-03-29T10:30:46
```
**Best for:** Excel, data analysis, spreadsheets

### JSON Format
```json
[
  {
    "vehicle_id": 1,
    "speed_kmh": 65.50,
    "speed_mph": 40.68,
    "distance_meters": 15.3,
    "timestamp": "2024-03-29T10:30:45"
  }
]
```
**Best for:** Data interchange, APIs, databases

### TXT Format
```
Speed Measurement Report
==================================================

Vehicle 1:
  Speed: 65.50 km/h (40.68 mph)
  Distance: 15.30 meters
  Time: 2024-03-29T10:30:45
```
**Best for:** Human reading, documentation

---

## 🎯 Use Cases

### 1. **Calibration Verification**
- Load test video with known reference objects
- Verify PPM calculation
- Fine-tune for accuracy

### 2. **Speed Analysis**
- Record multiple vehicles passing same point
- Compare speeds
- Identify patterns

### 3. **Training Data**
- Record manual measurements
- Create ground truth dataset
- Export for machine learning

### 4. **Speed Enforcement**
- Identify speeding vehicles
- Document evidence
- Export for reports

---

## 🐛 Troubleshooting

### Problem: Video won't load
**Solution:**
- Check file format (.mp4, .avi, .mov)
- Ensure file isn't corrupted
- Try another video file

### Problem: Speed seems wrong
**Solution:**
- **Recalibrate!** Most common issue
- Verify PPM value matches your reference
- Check camera FPS setting
- Ensure vehicle is in frame fully

### Problem: Camera won't open
**Solution:**
- Ensure camera is connected
- Check camera drivers
- Close other camera applications
- Try different camera device (change 0 to 1, 2, etc.)

### Problem: Graph shows no data
**Solution:**
- Record at least 2 measurements first
- Use "📏 Measure Speed" to add manual data
- Export requires clicking button after recording

---

## 📈 Advanced Tips

### Getting Accurate Measurements

1. **Use multiple reference points**
   - Don't rely on single PPM value
   - Average across several measurements

2. **Record at consistent frame rate**
   - Check FPS matches video actual FPS
   - Auto-detected from file info

3. **Mark measurement zone clearly**
   - Use lane markings or known objects
   - Ensure vehicle fully visible

4. **Take multiple samples**
   - Record same vehicle multiple times
   - Average for more accurate result

### Exporting for Analysis

**Regular data analysis:**
```python
import pandas as pd
df = pd.read_csv('speed_data.csv')
print(df['Speed (km/h)'].describe())  # Statistics
```

**Create visualizations:**
```bash
# Open CSV in Excel and create charts
# Or use matplotlib to create custom plots
```

---

## 🔧 Integration with Main System

The Speed Tester uses same core components as main system:

```python
from opencv_speed_detection import OpenCVSpeedDetector

# Create detector
detector = OpenCVSpeedDetector(
    pixels_per_meter=20.0,
    fps=30.0
)

# Calculate speed
measurement = detector.calculate_speed(
    vehicle_id=1,
    current_pos=(150, 200),
    prev_pos=(130, 200),
    frames_elapsed=5
)

print(f"Speed: {measurement.speed_kmh} km/h")
```

---

## 📚 Keyboard Shortcuts (Planned)

| Shortcut | Action |
|----------|--------|
| Space | Play/Pause |
| R | Reset |
| C | Calibration mode |
| M | Measure speed |
| G | Show graph |
| E | Export |

---

## ✅ Checklist Before Using

- [ ] Video file exists and playable
- [ ] Calibration value ready (PPM calculated)
- [ ] Camera working (if using live feed)
- [ ] Enough disk space for export
- [ ] Know reference distance in video

---

## 🎓 Learning Resources

- **OpenCV Documentation**: https://docs.opencv.org/
- **Speed Measurement Theory**: https://en.wikipedia.org/wiki/Velocity_estimation
- **Video Processing**: OpenCV Tutorials

---

## 📞 Common Questions

**Q: Can I use any video format?**  
A: Most formats work (MP4, AVI, MOV). Use H.264 encoded MP4 for best compatibility.

**Q: How accurate is the speed measurement?**  
A: Accuracy depends on calibration (PPM). With proper calibration, ±2-3 km/h error is typical.

**Q: Can I track multiple vehicles?**  
A: Yes! Record measurements for different vehicle IDs separately.

**Q: What's the maximum video resolution?**  
A: 4K supported, but 1080p recommended for performance.

**Q: Do I need internet?**  
A: No, everything runs locally.

---

**Ready to test!** Launch Speed Tester and start measuring! 🚀
