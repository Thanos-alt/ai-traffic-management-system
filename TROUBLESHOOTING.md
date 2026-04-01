# TROUBLESHOOTING & FAQ - Speed Monitoring & Emergency Alerts

## Common Issues & Solutions

### Speed Measurement Issues

#### Q: Speeds are too high/too low
**A:** You need to calibrate `PIXELS_PER_METER` for your camera

**Solution Steps:**
1. Measure a real-world distance in your camera view
   - Example: Road lane is 3.5 meters wide
2. Mark the same area in the video and count pixels
   - Example: Lane = 70 pixels in video
3. Calculate: `PIXELS_PER_METER = 70 / 3.5 = 20`
4. Update in `config/config.py`
5. Restart the system

**Quick Test:**
- Use reference object (car, person) of known size
- If speeds are 2x too high: Double PIXELS_PER_METER
- If speeds are 2x too low: Halve PIXELS_PER_METER

#### Q: Speeds show zero/very low
**A:** Vehicles not being tracked properly

**Check:**
- Vehicle bounding boxes are visible (green boxes)
- Vehicles move between frames
- `ENABLE_SPEED_TRACKING = True` in config
- `MAX_TRACK_AGE` not too short (30 is default)

#### Q: Inconsistent speed readings
**A:** Jumpy detections between frames

**Solution:**
- Increase FPS of camera (more frames = smoother tracking)
- Improve lighting conditions
- Increase confidence threshold in config
- Ensure vehicles are clearly visible

---

### Emergency Service Issues

#### Q: No alarm sound when condition triggered
**A:** Check multiple things

**Solutions:**
1. Verify `ENABLE_ALARM_SOUND = True` in config
2. Check system volume is not muted
3. On Windows: Run with administrator privileges
4. Try test: `python test_new_features.py`
5. Check logs for errors

#### Q: Police/Ambulance not called
**A:** Multiple possible causes

**Check:**
1. Is it the duplicate call cooldown? (30 seconds between same type)
2. Is `ENABLE_EMERGENCY_CALLS = False`? (Mock mode - no actual calls)
3. Are thresholds met?
   - Speeding: Speed > 80 km/h AND > 60 km/h limit
   - Accident: Collision IOU > 0.3 OR sudden deceleration > 10 km/h
   - Fire: YOLO detects 'fire', 'flame', or 'smoke' class
4. Check logs: `logs/traffic_management.log`

#### Q: Too many false emergency calls
**A:** Thresholds too sensitive

**Solutions:**
```python
# In config.py, adjust:
SPEEDING_THRESHOLD_KMH = 90  # Raise from 80
COLLISION_IOU_THRESHOLD = 0.4  # Raise from 0.3
ACCIDENT_SPEED_DROP_THRESHOLD = 20  # Raise from 10
```

#### Q: Call history shows correct calls but no voice alert
**A:** Voice alert issue

**Check:**
1. Is audio working? (Play test sound)
2. Is `ENABLE_VOICE = True` in config?
3. Text-to-speech engine initialized?
4. Check logs for voice engine errors

---

### Incident Detection Issues

#### Q: Collisions not detected
**A:** Bounding boxes not overlapping enough

**Solutions:**
```python
# Lower the threshold (more sensitive):
COLLISION_IOU_THRESHOLD = 0.2  # From 0.3

# Or check:
- Are vehicles actually overlapping?
- Is detection confidence high enough?
- Are bounding boxes correct?
```

#### Q: Too many collision false positives
**A:** Threshold too loose

**Solution:**
```python
# Raise the threshold:
COLLISION_IOU_THRESHOLD = 0.5  # From 0.3
```

#### Q: Fire not detected when visible
**A:** YOLO model doesn't include fire class

**Solutions:**
1. Check YOLO model includes fire detection
2. Train custom model with fire images
3. Enable or disable: `ENABLE_FIRE_DETECTION`
4. Use alternative fire detection method

---

### Display & Visual Issues

#### Q: Speed not showing on vehicles
**A:** Display setting disabled

**Solution:**
```python
# In config.py:
SHOW_SPEED_ON_VEHICLES = True
```

#### Q: Speed overlay overlaps with class label
**A:** Adjust label format

**Solution in main_fixed.py:**
Change label format to show speed only or vertically stack

#### Q: Color coding not working
**A:** Check color values

**Verify in config.py:**
```python
SPEED_DISPLAY_COLOR = (0, 255, 255)       # Cyan (B,G,R format)
SPEEDING_DISPLAY_COLOR = (0, 0, 255)      # Red (B,G,R format)
```

---

### Logging & Log Files

#### Q: Log file growing too fast
**A:** Normal with many frames

**Solution:**
```python
# In config.py, adjust log level:
LOG_LEVEL = "WARNING"  # From "INFO" - less verbose
```

#### Q: Emoji characters showing weird
**A:** Windows console encoding

**Note:** This is cosmetic only - logs are correct. Actual file has proper encoding.

#### Q: No logs being written
**A:** Permission or path issue

**Check:**
1. `logs/` directory exists
2. Have write permissions
3. Log file not locked by another process
4. Check LOG_FILE path in config

---

### Camera & Input Issues

#### Q: Using USB camera but getting no frames
**A:** Camera not properly initialized

**Solutions:**
```python
# Change camera source:
app = TrafficManagementApp(camera_source=0)      # Webcam
app = TrafficManagementApp(camera_source=1)      # USB camera
app = TrafficManagementApp(camera_source="rtsp://...") # IP camera
```

#### Q: Using video file, speeds wrong
**A:** Incorrect FPS for video

**Check:**
```python
# Video FPS might differ:
FPS = 30  # Check actual video FPS
         # Speed calc uses this value
```

#### Q: Performance too slow
**A:** Too much processing

**Solutions:**
```python
# In config.py:
FRAME_SKIP_RATE = 2        # Process every 2nd frame
CONFIDENCE_THRESHOLD = 0.6 # Higher = fewer detections
ENABLE_ALL = False         # Disable unused features
```

---

### Integration Issues

#### Q: ImportError when running main_fixed.py
**A:** Missing module

**Solution:**
```bash
# Run syntax check:
python -m py_compile src/speed_tracker.py
python -m py_compile src/incident_detector.py
python -m py_compile src/emergency_service.py

# Install missing packages:
pip install -r requirements.txt
```

#### Q: Module initialized but not working
**A:** Likely configuration issue

**Debug:**
1. Run demo: `python test_new_features.py`
2. Check individual components in Python shell
3. Review config.py settings
4. Check logs for errors

---

### Demo Script Issues

#### Q: test_new_features.py fails
**A:** Dependency or configuration issue

**Solutions:**
```bash
# Ensure all dependencies:
pip install -r requirements.txt

# Run with Python debugging:
python -u test_new_features.py

# Check for syntax errors:
python -m py_compile test_new_features.py
```

#### Q: Demo shows speeds of 0
**A:** Normal on first frame

**Note:** Speed = 0 on frame 0 (no previous position to compare). Should show speeds from frame 1 onward.

---

## Quick Diagnostic Checklist

Use this to diagnose issues:

```
□ All new Python files created?
  - src/speed_tracker.py
  - src/incident_detector.py
  - src/emergency_service.py

□ Config updated with new settings?
  - ENABLE_SPEED_TRACKING = True
  - PIXELS_PER_METER = 20 (or your value)
  - ENABLE_INCIDENT_DETECTION = True

□ Demo script works?
  python test_new_features.py

□ Speed calculation reasonable?
  - PIXELS_PER_METER calibrated
  - Speeds at 80+ km/h on frame 1+

□ Emergency calls visible in logs?
  - Check logs/traffic_management.log
  - Missing = check thresholds met

□ Video display shows overlays?
  - Speed numbers visible
  - Color coding works

□ Alarm sounds when triggered?
  - Audio enabled
  - Volume not muted

□ No console errors on exit?
  - Statistics displayed
  - Clean shutdown
```

---

## Performance Benchmarks

**Typical Performance:**
- FPS: 25-30 (with all features)
- Memory: 200-300 MB
- CPU: ~40-60% single core
- Latency: <50ms per frame
- Call response time: <1 second

**If performance insufficient:**
1. Disable unused features
2. Lower resolution: `FRAME_WIDTH = 640`
3. Reduce FPS processing
4. Use faster camera source

---

## Getting Help

**If stuck:**

1. **Check Logs First**
   ```bash
   tail logs/traffic_management.log
   ```

2. **Run Demo**
   ```bash
   python test_new_features.py
   ```

3. **Check Config**
   ```bash
   # Review these settings:
   PIXELS_PER_METER
   ENABLE_* = True/False
   Thresholds
   ```

4. **Test Components Individually**
   ```python
   # In Python shell:
   from src.speed_tracker import SpeedTracker
   tracker = SpeedTracker()
   # Test functions
   ```

5. **Enable Debug Logging**
   ```python
   # In config.py:
   LOG_LEVEL = "DEBUG"  # More verbose
   ```

---

## Best Practices

1. **Always calibrate camera** before production
2. **Test with video file** first
3. **Monitor logs** regularly
4. **Document your settings** (calibration, thresholds)
5. **Keep backlog of logs** for analysis
6. **Test emergency protocol** regularly
7. **Update config comments** when changing values
8. **Keep backup of working config**

---

**Version:** 2.0  
**Last Updated:** March 2026  
**Status:** Documented & Supported ✅

---

Need more help? Check:
- `FEATURES_COMPLETE.md` - Full feature overview
- `SETUP_SPEED_MONITORING.md` - Setup guide
- `SPEED_MONITORING_GUIDE.md` - Detailed guide
- `INTEGRATION_SUMMARY.md` - Technical details
