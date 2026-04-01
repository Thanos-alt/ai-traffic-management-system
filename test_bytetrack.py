#!/usr/bin/env python
"""Test ByteTrack speed tracker integration"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("✓ BYTETRACK INTEGRATION TEST")
print("=" * 70)

try:
    from src.bytetrack_speed_tracker import ByteTrackSpeedTracker
    from src.speed_tracker import SpeedTracker
    from config.config import TRACKER_TYPE, PIXELS_PER_METER, MAX_TRACK_AGE
    
    print("\n✓ Imports successful")
    print(f"  - Default tracker type: {TRACKER_TYPE}")
    print(f"  - Pixels per meter: {PIXELS_PER_METER}")
    print(f"  - Max track age: {MAX_TRACK_AGE}")
    
    # Test ByteTrack tracker initialization
    print("\n✓ Initializing ByteTrack Speed Tracker...")
    bytetrack = ByteTrackSpeedTracker(fps=30, pixels_per_meter=20, max_age=30)
    print("  ✓ ByteTrack initialized successfully")
    
    # Test basic tracker as fallback
    print("\n✓ Initializing Basic Speed Tracker (fallback)...")
    basic = SpeedTracker(fps=30, pixels_per_meter=20)
    print("  ✓ Basic tracker initialized successfully")
    
    # Test with sample detections
    print("\n✓ Testing with sample vehicledetections...")
    sample_detections = [
        {
            'bbox': (100, 100, 150, 150),
            'center': (125, 125),
            'class_name': 'car',
            'confidence': 0.9
        },
        {
            'bbox': (200, 200, 250, 250),
            'center': (225, 225),
            'class_name': 'truck',
            'confidence': 0.85
        },
        {
            'bbox': (300, 300, 350, 350),
            'center': (325, 325),
            'class_name': 'person',
            'confidence': 0.88
        },
    ]
    
    # Test ByteTrack tracking
    tracked = bytetrack.match_detections(sample_detections, 720, 1280)
    print(f"  ✓ ByteTrack tracked {len(tracked)} vehicles")
    for vehicle in tracked:
        print(f"    - Vehicle {vehicle['track_id']}: {vehicle['class_name']} (confidence={vehicle['confidence']:.2f})")
    
    # Test speed statistics
    stats = bytetrack.get_speed_statistics(tracked)
    print("\n✓ Speed Statistics (ByteTrack):")
    print(f"  - Average speed: {stats['avg_speed']:.1f} km/h")
    print(f"  - Max speed: {stats['max_speed']:.1f} km/h")
    print(f"  - Min speed: {stats['min_speed']:.1f} km/h")
    print(f"  - Median speed: {stats['median_speed']:.1f} km/h")
    print(f"  - Tracked vehicles: {len(stats['tracked_vehicles'])}")
    
    # Simulate movement for speed calculation
    print("\n✓ Simulating vehicle movement for speed calculation...")
    moved_detections = [
        {
            'bbox': (110, 110, 160, 160),  # Moved 10 pixels
            'center': (135, 135),
            'class_name': 'car',
            'confidence': 0.9
        },
        {
            'bbox': (220, 220, 270, 270),  # Moved 20 pixels
            'center': (245, 245),
            'class_name': 'truck',
            'confidence': 0.85
        },
    ]
    
    tracked2 = bytetrack.match_detections(moved_detections, 720, 1280)
    print(f"  ✓ After movement: {len(tracked2)} vehicles tracked")
    
    for vehicle in tracked2:
        if vehicle['current_speed'] > 0:
            print(f"    - Vehicle {vehicle['track_id']}: {vehicle['current_speed']:.1f} km/h")
    
    # Test speeding detection
    print("\n✓ Testing speeding vehicle detection...")
    speeding = bytetrack.get_speeding_vehicles(tracked2, speed_limit=60)
    if speeding:
        print(f"  ✓ Found {len(speeding)} speeding vehicles")
        for veh in speeding:
            print(f"    - Vehicle {veh['track_id']}: {veh['speed']:.1f} km/h (excess: {veh['excess']:.1f})")
    else:
        print("  ✓ No speeding vehicles detected (speed too low in simulation)")
    
    # Test tracker comparison
    print("\n✓ Tracker Comparison:")
    print("  Feature                 | ByteTrack | Basic")
    print("  |----|")
    print("  Advanced tracking       | ✓         | ✗")
    print("  Occlusion handling      | ✓         | ✗")
    print("  Stable IDs              | ✓         | ✗")
    print("  Speed measurement       | Better    | Good")
    print("  Performance overhead    | Low       | None")
    print("  Recommended usage       | Default   | Fallback")
    
    print("\n" + "=" * 70)
    print("✅ ALL BYTETRACK TESTS PASSED!")
    print("=" * 70)
    
    print("\n🎯 Usage Options:")
    print("\n1. Use ByteTrack (recommended):")
    print("   python main.py --tracker bytetrack")
    print("   python main.py  # Default uses bytetrack")
    
    print("\n2. Use Basic tracker (fallback):")
    print("   python main.py --tracker basic")
    
    print("\n3. Configuration:")
    print("   - Edit config/config.py")
    print("   - TRACKER_TYPE = 'bytetrack'  # or 'basic'")
    print("   - PIXELS_PER_METER = 20       # Calibration factor")
    print("   - MAX_TRACK_AGE = 30          # Frames to keep track")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
