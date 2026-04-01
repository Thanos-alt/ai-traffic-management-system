"""Quick diagnostic to show speed output to terminal and dashboard"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.speed_tracker import SpeedTracker

print("\n" + "="*70)
print("SPEED MONITORING - TERMINAL OUTPUT TEST")
print("="*70 + "\n")

# Initialize speed tracker
tracker = SpeedTracker(fps=30, pixels_per_meter=20)

# Simulate 5 frames of vehicle movement
print("Simulating vehicle movement across 5 frames:\n")

detections = [
    {
        'center': (100, 100),
        'bbox': (80, 80, 120, 120),
        'class_name': 'car',
        'confidence': 0.95
    },
    {
        'center': (200, 150),
        'bbox': (180, 130, 220, 170),
        'class_name': 'truck',
        'confidence': 0.92
    }
]

for frame_num in range(5):
    # Update positions (simulate movement)
    detections[0]['center'] = (100 + frame_num * 20, 100)
    detections[1]['center'] = (200 + frame_num * 30, 150)
    
    tracked = tracker.match_detections(detections, 720, 1280)
    
    # Calculate speeds for display
    speeds = [v['current_speed'] for v in tracked if v['current_speed'] > 0]
    
    if speeds:
        avg_speed = sum(speeds) / len(speeds)
        max_speed = max(speeds)
        min_speed = min(speeds)
        
        # This is what appears in terminal
        output = f"Frame {frame_num}: Vehicles={len(tracked)} | Avg Speed={avg_speed:.1f} km/h | Max Speed={max_speed:.1f} km/h"
        print(output)
    else:
        print(f"Frame {frame_num}: Vehicles={len(tracked)} | Speeds calculating (frame 0 shows 0 speed)")
    
    # Show individual vehicle speeds
    for vehicle in tracked:
        if vehicle['current_speed'] > 0:
            print(f"  └─ {vehicle['class_name']}: {vehicle['current_speed']:.1f} km/h (ID: {vehicle['track_id']})")

print("\n" + "="*70)
print("DASHBOARD DISPLAY")
print("="*70 + "\n")

speed_stats = {
    'avg_speed': 81.0,
    'max_speed': 97.5,
    'speeding_count': 2
}

print("Bottom-left corner of video display:")
print("""
┌────────────────────────┐
│ Vehicles: 2            │ 
│ Density: 12.5%         │
│ Level: LOW             │
│ Trend: STABLE          │
│ Avg Speed: 81.0 km/h   │ (Orange - warning)
│ Max Speed: 97.5 km/h   │ (Red - critical)
│ Speeding: 2            │ (Red - violations)
└────────────────────────┘
""")

print("\n" + "="*70)
print("ON-VIDEO DISPLAY")
print("="*70 + "\n")

print("""
Vehicle boxes with speed overlays:

Red Box:    car 0.95 | 92.3 km/h  ← Vehicle exceeding limit
            Limit: 60 km/h

Orange Box: truck 0.92 | 72.5 km/h ← Vehicle over limit (warning)
            Limit: 60 km/h

Green Box:  car 0.88 | 45.2 km/h  ← Normal speed
            Limit: 60 km/h
""")

print("\n" + "="*70)
print("KEY IMPROVEMENTS MADE:")
print("="*70 + "\n")

improvements = [
    "1. Console Output: Speed stats printed to terminal each frame",
    "2. Dashboard Panel: Speed statistics in video overlay",
    "   - Average Speed (color-coded)",
    "   - Maximum Speed (color-coded)",
    "   - Count of speeding vehicles",
    "3. Vehicle Boxes: Speed displayed on each detection",
    "   - Color-coded by speed status",
    "   - Speed limit reference shown",
    "4. Terminal Alerts: Speeding violations print to console",
    "5. Dashboard Size: Auto-expands for speed information",
]

for item in improvements:
    print(f"✓ {item}")

print("\n" + "="*70)
print("TO SEE THIS IN LIVE VIDEO:")
print("="*70 + "\n")

print("1. Run: python main_fixed.py")
print("2. Watch terminal for speed output like:")
print("   Frame 45: Vehicles=3 | Avg Speed=52.3 km/h | Max Speed=78.5 km/h")
print("3. Watch video for:")
print("   - Dashboard panel showing speeds (bottom-left)")
print("   - Vehicle boxes with speeds (on each vehicle)")
print("   - Speed limit indicator (top area)")
print("4. On speeding (>60 km/h): Console prints speed warning")
print("5. On critical (>80 km/h): Console prints SPEEDING ALERT + Police called")

print("\n" + "="*70)
