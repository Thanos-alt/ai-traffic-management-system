# Speed Tracking Integration to main.py

## Summary
Added comprehensive speed tracking and incident detection to **main.py** (threading-based fast FPS version). The system now monitors vehicle speeds in real-time with emergency alerts.

## Changes Made

### 1. **Imports Added** (Lines 14-16)
```python
from src.speed_tracker import SpeedTracker
from src.incident_detector import IncidentDetector
from src.emergency_service import EmergencyServiceManager
```

### 2. **Component Initialization** (Lines 32-34, 79-84)
Added three new components:
- `self.speed_tracker` - Vehicle tracking and speed calculation
- `self.incident_detector` - Collision/fire/accident detection
- `self.emergency_service` - Emergency service calls

### 3. **Speed Stats Storage** (Line 47)
```python
self.last_speed_stats = {
    "avg_speed": 0,
    "max_speed": 0, 
    "speeding_count": 0,
    "tracked_vehicles": []
}
```

### 4. **Process Worker Thread Enhanced** (Lines 120-190)
Integrated speed tracking into the background processing thread:

**Speed Tracking:**
```python
tracked_vehicles = self.speed_tracker.match_detections(
    detections, frame.shape[0], frame.shape[1]
)
speeding_vehicles = self.speed_tracker.get_speeding_vehicles(tracked_vehicles, 60)
speed_stats = self.speed_tracker.get_speed_statistics(tracked_vehicles)
```

**Incident Detection:**
```python
incidents = self.incident_detector.analyze_incidents(tracked_vehicles, detections)
# Handles: collisions, fires, accidents
```

**Emergency Response:**
- Collision: Calls `emergency_service.handle_collision()`
- Fire: Calls `emergency_service.handle_fire()`
- Accident: Calls `emergency_service.handle_accident()`
- Speeding (>80 km/h): Calls `emergency_service.handle_speeding()`

**Alert System:**
- Collision alerts with voice and police call
- Fire alerts with emergency services (police, ambulance, fire)
- Speeding alerts (>80 km/h critical, 60-80 km/h warning)

### 5. **Console Output** (Lines 230-237)
Every second, prints:
```
Frame N: Vehicles=X | Avg Speed=X.X km/h | Max Speed=X.X km/h | Speeding=X | FPS=X.X
```

### 6. **Speed Display on Bounding Boxes** (Lines 305-338)
Each vehicle box now shows:
- **Green** (< 60 km/h): `Car 0.95 | 45.2 km/h`
- **Orange** (60-80 km/h): `Car 0.95 | 72.5 km/h`
- **Red** (> 80 km/h): `Car 0.95 | 85.3 km/h ⚠`

### 7. **Dashboard Speed Panel** (Lines 347-370)
Dashboard now displays:
- **Row 3 (Speed Stats):**
  - `Avg Speed: X.X km/h` (color-coded: green/orange/red)
  - `Speeding: X | Max: X.X` (red, only shown if speeders detected)

Dashboard sizing expanded from 125px to 145px height to accommodate speed row.

## Speed Measurement Formula
```
Speed (km/h) = (pixels_distance / PIXELS_PER_METER) * FPS * 3.6
```
- **Default PIXELS_PER_METER**: 20
- **Calibration**: Adjust in `config.config.py` for accuracy

## Speed Thresholds
- **Speed Limit**: 60 km/h
- **Warning Threshold**: 60-80 km/h (orange alert)
- **Critical Threshold**: >80 km/h (red alert, police call)

## Features

### Real-time Monitoring
✓ Vehicle speed tracking frame-to-frame
✓ Average and maximum speed calculation
✓ Speeding vehicle counting
✓ Density and traffic level analysis

### Visual Feedback
✓ Color-coded speed labels on boxes (green/orange/red)
✓ Speed display in dashboard panel
✓ Speed statistics in console output
✓ HSR incident status indicator

### Event Handling
✓ Collision detection → Emergency call
✓ Fire detection → Multi-agency alert
✓ Accident detection → Police + Ambulance
✓ Critical speeding (>80 km/h) → Police call
✓ Warning speeding (60-80 km/h) → Console log

### Alert Cooldown
- 3-second cooldown between repeated alerts
- Prevents alert flooding
- Prevents duplicate emergency calls

## Threading Model
- **Main Thread**: Frame capture and display
- **Processing Thread**: YOLO detection, speed tracking, incident analysis
- **Queue-based**: Frame transfer between threads
- **Thread-safe**: Results stored in `self.last_*` variables

## Testing
Run with:
```bash
python main.py
```

Monitor console for:
- Periodic frame statistics (every 1 second)
- Speed warnings (when > 60 km/h)
- Incident alerts (collisions, fires, accidents)
- Emergency service activations

## Integration with Existing System
- Uses same emergency service manager as main_fixed.py
- Same speed tracking algorithm
- Same incident detection logic
- Compatible with all voice alerts and configs

## Next Steps
1. Calibrate PIXELS_PER_METER for accurate speed readings
2. Test with actual camera feed
3. Adjust alert thresholds per traffic regulations
4. Monitor emergency service integration
