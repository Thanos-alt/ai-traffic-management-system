# main.py Speed Integration - Quick Reference

## 🎯 What Changed

### BEFORE (Original main.py)
```
• Traffic detection only
• Vehicle counting
• Density analysis
• NO speed tracking
• NO incident detection
• NO emergency alerts
• Basic dashboard with vehicles/density/level
```

### AFTER (Updated main.py) ✨
```
✅ Traffic detection + Speed tracking
✅ Vehicle counting + Speed measurement
✅ Density analysis + Speed statistics
✅ Incident detection (collision/fire/accident)
✅ Emergency response (police/ambulance/fire)
✅ Enhanced dashboard with speed panel
✅ Real-time speed labels on vehicles
✅ Console output with speed metrics
✅ Voice alerts for speeding/incidents
✅ Color-coded speed display
```

## 📊 Expected Output

### Console (Every 1 Second)
```
Frame 1: Vehicles=5 | Avg Speed=45.3 km/h | Max Speed=78.2 km/h | Speeding=0 | FPS=28.5
Frame 2: Vehicles=5 | Avg Speed=46.1 km/h | Max Speed=82.1 km/h | Speeding=1 | FPS=29.1
Frame 3: Vehicles=6 | Avg Speed=52.8 km/h | Max Speed=85.5 km/h | Speeding=2 | FPS=28.8
```

### Speed Warnings (Console)
```
[INFO] Speed warning: Vehicle 3 at 65.3 km/h
[WARNING] SPEEDING ALERT: Vehicle 5 at 82.1 km/h
Emergency call originated: Police (100)
```

### Video Display (Live)
```
Dashboard:
┌──────────────────────┐
│ Vehicles: 5          │
│ Density: 45%         │
│ Level: HIGH          │
│ Trend: ↑             │
│ Avg Speed: 52.8 km/h │ ← NEW (Color: Green/Orange/Red)
│ Speeding: 2 | Max... │ ← NEW (Only if >60 km/h)
└──────────────────────┘

Video Boxes:
Car 0.95 | 45.2 km/h 🟢
Bike 0.88 | 28.1 km/h 🟢
Car 0.92 | 72.5 km/h 🟠
Car 0.89 | 82.1 km/h ⚠️🔴
Truck 0.94 | 35.8 km/h 🟢
```

## 🚀 Running It

```bash
# 1. Open terminal
python main.py

# 2. Watch console for speed data
# 3. Press 'q' to quit, 'p' to pause, 's' to save frame
# 4. Monitor log files for detailed events
```

## 🎨 Speed Color Coding

| Speed | Color | Label |
|-------|-------|-------|
| < 60 km/h | 🟢 Green | Normal |
| 60-80 km/h | 🟠 Orange | Warning |
| > 80 km/h | 🔴 Red | Critical |

## 🔧 Configuration

Most important setting: **PIXELS_PER_METER**

```python
# In config/config.py
PIXELS_PER_METER = 20  # Default (adjust for your camera)

# To calibrate:
# 1. Find a known distance in camera view (e.g., road lane = 3.7m)
# 2. Measure pixels covering that distance
# 3. Set: PIXELS_PER_METER = pixels / 3.7
```

## 📈 Key Metrics

| Metric | Purpose | Example |
|--------|---------|---------|
| **Vehicles** | Traffic density | 5 vehicles in view |
| **Avg Speed** | Average velocity | 45.3 km/h |
| **Max Speed** | Highest speedster | 85.5 km/h |
| **Speeding** | Count over limit | 2 vehicles (>60 km/h) |
| **FPS** | Performance | 28.5 frames/sec |

## ⚠️ Alert Thresholds

```python
WARNING: 60 km/h (Speed Limit)
├─ 60-80 km/h → Orange label, Console alert
├─ >80 km/h  → Red label, SPEEDING ALERT, Police call

INCIDENT: Collision/Fire/Accident
├─ Collision → Police + Voice alert
├─ Fire → Police + Ambulance + Fire brigade
└─ Accident → Police + Ambulance
```

## 🧵 Threading Model

```
Main Thread
├─ Camera capture
├─ Frame queueing
└─ Display loop (uses last_detections, last_speed_stats)

Processing Thread
├─ YOLO detection
├─ Speed tracking
├─ Incident analysis
├─ Emergency response
└─ Console output (every 1 sec)
```

## ✅ Verification Checklist

Before running, verify:
- [ ] Python environment configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Camera accessible
- [ ] main.py compiles (`python -m py_compile main.py`)
- [ ] All modules present:
  - src/speed_tracker.py
  - src/incident_detector.py
  - src/emergency_service.py
  - config/config.py with speed parameters

## 📝 Log Output Examples

### Normal Operation
```
[INFO] Initializing Live Stream Traffic System...
[INFO] Initializing camera...
[INFO] Loading traffic detector...
[INFO] Initializing speed tracker...
[INFO] Initializing incident detector...
[INFO] Initializing emergency service manager...
[INFO] All components initialized successfully!
Frame 1: Vehicles=3 | Avg Speed=40.2 km/h | Max Speed=58.1 km/h | Speeding=0 | FPS=28.5
```

### Speed Warning
```
[INFO] Speed warning: Vehicle 2 at 65.3 km/h
```

### Critical Alert
```
[WARNING] SPEEDING ALERT: Vehicle 4 at 85.7 km/h
[WARNING] Emergency call originated: Police (100)
```

### Incident Alert
```
[WARNING] Collision detected! Severity: high
[WARNING] Emergency call originated: Police (100)
```

## 🎯 Success Indicators

When running, you should see:
- ✅ Console output every second with speed stats
- ✅ Speed labels on all detected vehicles
- ✅ Dashboard showing average speed
- ✅ Colors changing based on speed thresholds
- ✅ FPS counter 25-30 range
- ✅ Alerts triggering for speeds > 80 km/h

## 🐛 Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| No speed showing | Check PIXELS_PER_METER calibration |
| No console output | Run with: `python -u main.py` |
| Alerts not triggering | Check minimum speed (> 60 km/h) |
| Crashes on start | Check camera source and dependencies |
| Low FPS | Reduce frame resolution or detection confidence |

## 📊 Performance Baseline

```
Expected Performance:
• FPS: 25-30 frames/second
• CPU: 30-50% one core
• Memory: 500-1000 MB
• Latency: <100ms
```

## 🎓 Learning the System

Understanding the flow:

```
1. Camera captures frame
2. Frame queued to processing thread
3. Processing thread:
   - Detects vehicles (YOLO)
   - Tracks vehicles (SpeedTracker)
   - Calculates speeds
   - Detects incidents
   - Handles emergencies
   - Stores results
4. Main display thread:
   - Gets results from queue
   - Draws boxes with speeds
   - Updates dashboard
   - Displays FPS
5. Output:
   - Console statistics
   - Video with labels
   - Log files
   - Voice alerts
```

---

**Ready to run:** `python main.py`
**Expected:** 🟢 Speed tracking active with 25-30 FPS
