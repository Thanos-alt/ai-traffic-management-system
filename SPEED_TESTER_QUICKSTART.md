# ⚡ Speed Tester - Quick Start (30 seconds)

## 🚀 Launch

```bash
# Install dependencies (first time only)
pip install -r requirements.txt

# Run Speed Tester
python speed_tester.py
```

---

## 🎯 First Test (2 minutes)

### Step 1: Load Video
1. Click **📁 Load Video**
2. Select any MP4/AVI video with vehicles
3. Video appears on screen

### Step 2: Calibrate
1. Click **⚙️ Calibration Mode**
2. In the video, draw a line across a known object (lane, car, etc.)
3. If lane = 3 meters and pixels = 60:
   - **Pixels/Meter = 60 ÷ 3 = 20**
   - Enter `20` in spinbox

### Step 3: Record Speed
1. Click **📏 Measure Speed**
2. Enter Vehicle ID: `1`
3. Enter Speed: `60` (km/h)
4. Click **Record**
5. Check statistics update at bottom!

### Step 4: Export
1. Click **💾 Export Results**
2. Save as `test_results.csv`
3. ✓ Done! Open in Excel

---

## 📊 Live Camera Test

```bash
python speed_tester.py
```

1. Click **📷 Load Camera**
2. Calibrate using stationary reference
3. Record measurements
4. View live statistics

---

## 💡 What To Expect

| Component | What You'll See |
|-----------|-----------------|
| Video Display | Frame by frame or live camera |
| Progress Bar | Seek through video |
| Statistics | 🚗 Vehicles, 📊 Avg Speed, ⬆️ Max Speed |
| Graph | Speed trend over time |

---

## ⚙️ One Critical Setting

**Pixels Per Meter (PPM)** = How many pixels = 1 real meter

```
How to get it:
1. Find known distance in video (road lane = 3m typical)
2. Measure pixels between points
3. PPM = pixels ÷ meters

Example: 60 pixels for 3 meter lane → PPM = 20
```

---

## 🎮 Main Buttons

| Button | What It Does |
|--------|-------------|
| 📁 **Load Video** | Open video file |
| 📷 **Load Camera** | Use webcam |
| 🎬 **Play/Pause** | Control playback |
| ⚙️ **Calibration** | Set pixels/meter |
| 📏 **Measure Speed** | Record manual speed |
| 📊 **Show Graph** | Visualize speed data |
| 💾 **Export** | Save results (CSV/JSON/TXT) |

---

## 📈 View Results

### In Real-time
- Bottom panel shows live statistics
- 🚗 Vehicles: How many unique vehicles
- 📊 Avg Speed: Average km/h
- ⬆️ Max Speed: Fastest recorded

### Export & Analyze
```bash
# After export, open CSV in Excel
# Or view JSON in text editor
cat results.json
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|-------|-----|
| Video won't load | Check file format (MP4/AVI) |
| Speed wrong | Recalibrate! Update PPM value |
| Camera not working | Check permissions, close other apps |
| No data in graph | Record at least 2 measurements |

---

## 📦 What's New (2 Files Added)

1. **`opencv_speed_detection.py`** (380 lines)
   - Core speed measurement engine
   - Calibration tools
   - Data export functions

2. **`speed_tester.py`** (450 lines)
   - Full Tkinter GUI
   - Video display
   - Real-time statistics
   - Graph visualization

3. **Documentation** (3 files)
   - This quick start guide
   - Detailed usage guide
   - Technical reference

---

## 🎯 Use Cases

✅ **Test video processing speed**  
✅ **Verify calibration values**  
✅ **Create training data**  
✅ **Analyze traffic patterns**  
✅ **Export for reports**  

---

## 📚 More Info

- **[Full Guide](SPEED_TESTER_GUIDE.md)** - Complete instructions
- **[Technical Docs](OPENCV_SPEED_DETECTION_README.md)** - API reference
- **[ByteTrack Docs](BYTETRACK_INTEGRATION_GUIDE.md)** - Tracking algorithm

---

**That's it! Ready to test? Launch `python speed_tester.py` now!** 🚀
