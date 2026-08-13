# QUICK START - Speed Monitoring and Emergency Alert System

## Installation

Make sure you have all requirements installed:
```bash
pip install -r requirements.txt
```

## Key Configuration (config/config.py)

### 1. Enable Speed Tracking
```python
ENABLE_SPEED_TRACKING = True
SPEED_LIMIT_KMH = 60  # Your desired speed limit
SPEEDING_THRESHOLD_KMH = 80  # Speed above which police is called
```

### 2. Enable Incident Detection
```python
ENABLE_INCIDENT_DETECTION = True
ENABLE_FIRE_DETECTION = True
```

### 3. Emergency Services Setup
```python
ENABLE_EMERGENCY_CALLS = False  # Set to True when ready
ENABLE_ALARM_SOUND = True
```

### 4. IMPORTANT: Calibrate Camera Speed
```python
# This is critical for accurate speed measurement!
PIXELS_PER_METER = 20  
# Calibration Steps:
# 1. Measure a known distance in your camera view (e.g., road lane = 3.5m)
# 2. Note how many pixels that distance is in the video
# 3. Calculate: PIXELS_PER_METER = pixels / meters
```

## Running the System

```bash
python main_fixed.py
```

## What to Expect

### Speed Tracking Display
- Detected vehicles show: `[Vehicle Class] [Confidence] | [Current Speed] km/h`
- Color coded boxes:
  - **Green**: Normal speed (under limit)
  - **Orange**: Over limit warning
  - **Red**: Critical speeding (should trigger police)

### Voice Alerts
You will hear voice warnings for:
- Speeding violations
- Collisions detected
- Fire detected
- Sudden stops

### Alarm Sounds
The system will beep/ring for:
- Speeding above 80 km/h
- Collisions
- Fire detection
- Other critical incidents

### Emergency Logging
Check logs for emergency call records:
```
📞 EMERGENCY CALL: POLICE (100) - Incident: SPEEDING_VIOLATION
📞 EMERGENCY CALL: AMBULANCE (102) - Incident: ACCIDENT
🔥 FIRE DETECTED: flame
```

## Testing Without Camera

To test with a video file instead of camera:

1. Save a video file to your project folder: `test_video.mp4`
2. Edit `main_fixed.py`, change:
```python
# Change this:
app = TrafficManagementApp(camera_source=0)

# To this:
app = TrafficManagementApp(camera_source="test_video.mp4")
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| Q | Quit |
| P | Pause/Resume |
| S | Save screenshot |

## Emergency Service Features

### Speed Violation Response
- Vehicle speed > 80 km/h 
  - ✓ Alarm rings
  - ✓ Voice alert with speed info
  - ✓ Police called (mock)
  - ✓ Logged with vehicle details

### Collision Detection
- Two vehicles overlapping (IoU > 0.3)
  - ✓ Alarm rings
  - ✓ Voice alert
  - ✓ Police called
  - ✓ Ambulance called

### Fire Detection
- YOLO detects fire/smoke/flame
  - ✓ Alarm rings
  - ✓ Voice alert
  - ✓ Police called
  - ✓ Ambulance called
  - ✓ Fire brigade called

### Accident Detection
- Sudden deceleration or vehicle standstill
  - ✓ Voice warning
  - ✓ Logged for analysis

## Viewing Logs

Main log file: `logs/traffic_management.log`

View real-time logs:
```bash
# On Windows PowerShell
Get-Content logs/traffic_management.log -Tail 50 -Wait

# On Linux/Mac
tail -f logs/traffic_management.log
```

## Statistics on Exit

When you quit the application (press Q), you'll see:
```
============================================================
EMERGENCY SERVICE STATISTICS
============================================================
Total Emergency Calls: X
Today's Calls: Y
Calls by Service Type:
  - police: Z
  - ambulance: W
  - fire: V
Calls by Incident Type:
  - SPEEDING_VIOLATION: Z
  - ACCIDENT: W
  - FIRE_INCIDENT: V
============================================================
```

## Troubleshooting

### Speed values look wrong
→ Recalibrate PIXELS_PER_METER in config.py

### No voice alerts
→ Check audio settings, ensure speakers are on

### No alarm beep
→ Check ENABLE_ALARM_SOUND = True in config.py

### Collisions not detected
→ Lower COLLISION_IOU_THRESHOLD in config.py

### Fire not detected
→ Ensure YOLO model has fire/smoke classes

## Next Steps

1. **Calibrate your camera** for accurate speeds
2. **Test with a video file** to verify all features work
3. **Review logs** to understand system behavior
4. **Adjust thresholds** based on your specific traffic conditions
5. **Enable real emergency calls** when ready for production

## Production Deployment

When ready for real emergency calls:
1. Set `ENABLE_EMERGENCY_CALLS = True`
2. Integrate with actual emergency service APIs
3. Add location tracking (GPS/geolocation)
4. Implement database for call history
5. Add web dashboard for monitoring
6. Set up failure notifications
7. Add rate limiting to prevent call spam
8. Implement call confirmation system

## Support

For issues or questions:
- Check logs in `logs/traffic_management.log`
- Review settings in `config/config.py`
- Ensure all dependencies are installed
- Test with sample video first
