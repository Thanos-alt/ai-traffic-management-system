# Running main.py with Speed Tracking

## Quick Start

### 1. Ensure Dependencies are Installed
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

### 3. Monitor Output

#### Console Output (Every Second)
```
Frame 123: Vehicles=5 | Avg Speed=45.3 km/h | Max Speed=78.2 km/h | Speeding=1 | FPS=28.5
Frame 124: Vehicles=5 | Avg Speed=46.1 km/h | Max Speed=82.1 km/h | Speeding=2 | FPS=29.1
Frame 125: Vehicles=6 | Avg Speed=52.8 km/h | Max Speed=85.5 km/h | Speeding=3 | FPS=28.8
```

#### Speed Warnings (Console)
When vehicles exceed 60 km/h:
```
[INFO] Speed warning: Vehicle 3 at 65.3 km/h
[WARNING] SPEEDING ALERT: Vehicle 5 at 82.1 km/h
```

#### Live Video Display
- **Speed labels** on each vehicle (color-coded)
  - Green: < 60 km/h (normal)
  - Orange: 60-80 km/h (warning)
  - Red: > 80 km/h (critical)

- **Dashboard** (top-left, 5 rows):
  - Vehicles: X
  - Density: X%
  - Level: HIGH/MEDIUM/LOW
  - Trend: ↑/→/↓
  - Avg Speed: X.X km/h (color-coded)
  - Speeding: X | Max: X.X (if speeding detected)

## Controls

| Key | Action |
|-----|--------|
| `q` | Quit application |
| `p` | Pause/Resume |
| `s` | Save frame snapshot |

## What's Happening

### Background Processing (threading)
1. Frames captured to queue
2. Separate thread runs YOLO detection
3. Speed tracking matches vehicles frame-to-frame
4. Incident detection checks for collisions/fires
5. Emergency services handle critical events
6. Results stored for display thread

### Display Thread
1. Gets latest detections from queue result
2. Draws bounding boxes with speed labels
3. Updates FPS counter
4. Displays dashboard with speed stats
5. Shows HSR incidents if active

### Speed Tracking
- Tracks centroid of each vehicle
- Calculates motion between frames
- Converts pixels to km/h using calibration
- Formula: `(pixels/20) * FPS * 3.6`

## Expected Output

### Normal Traffic
```
Frame 50: Vehicles=3 | Avg Speed=35.2 km/h | Max Speed=55.8 km/h | Speeding=0 | FPS=29.2
Dashboard: Level=LOW, Avg Speed in GREEN
```

### Heavy Traffic
```
Frame 100: Vehicles=15 | Avg Speed=28.5 km/h | Max Speed=42.1 km/h | Speeding=0 | FPS=27.8
Dashboard: Level=HIGH, Traffic ALERT
```

### Speeding Detected
```
Frame 150: Vehicles=8 | Avg Speed=61.3 km/h | Max Speed=92.5 km/h | Speeding=2 | FPS=28.5
Dashboard: Avg Speed in ORANGE/RED, Speeding: 2 | Max: 92.5
Console: [WARNING] SPEEDING ALERT: Vehicle 4 at 92.5 km/h
Voice: "Alert! Vehicle speeding at 92 kilometers per hour"
```

### Incident Detected
```
[WARNING] Collision detected! Severity: high
Voice: "Alert! Collision detected! Emergency services notified!"
Emergency Call: Police (100) activated
```

## Troubleshooting

### No Speed Display
- Check PIXELS_PER_METER calibration in config.py
- Ensure speed_tracker is initialized (check logs)
- Verify vehicle detection is working (check vehicle count)

### Console Output Not Showing
- Run in terminal/IDE with output buffering disabled
- Use: `python -u main.py` (unbuffered)
- Check logs directory for detailed output

### Alerts Not Triggering
- Verify FPS is > 10 (minimum for speed calculation)
- Check alert cooldown (3 seconds minimum between alerts)
- Verify emergency service is initialized

### Camera/Detection Issues
- Check camera source (default: 0 for webcam)
- Verify YOLO model is loaded (check logs)
- Test with: `python test_camera_simple.py`

## Advanced Configuration

See `config/config.py` for:
- SPEED_LIMIT_KMH (default: 60)
- SPEEDING_THRESHOLD_KMH (default: 80)
- PIXELS_PER_METER (default: 20, **calibration required**)
- ENABLE_SPEED_TRACKING (default: True)
- ENABLE_INCIDENT_DETECTION (default: True)

## Log Files

Detailed logs available in:
```
logs/
  - traffic_system.log      (main system events)
  - speed_tracking.log      (speed calculations)
  - incident_detection.log  (collision/fire events)
  - emergency_service.log   (emergency calls)
```

## Performance Notes

- **FPS**: 25-30 on standard hardware
- **Memory**: ~500MB - 1GB
- **CPU**: 30-50% on multi-core machine
- **Threading**: Separate detection thread reduces display jitter

## Architecture Difference from main_fixed.py

| Aspect | main_fixed.py | main.py |
|--------|---------------|---------|
| **Architecture** | Single-threaded sequential | Multi-threaded with Queue |
| **FPS** | 15-20 (slower) | 25-30 (faster) |
| **Latency** | Higher (all in main thread) | Lower (async processing) |
| **Speed Display** | Integrated in main loop | Thread-safe via queue |
| **Best For** | Accuracy focus | Real-time streaming |

Both versions include identical speed tracking and emergency services logic.
