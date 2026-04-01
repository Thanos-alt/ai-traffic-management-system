"""
Demo script showing the new speed monitoring and emergency alert features
Run this to test individual components before running the full system
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.speed_tracker import SpeedTracker
from src.incident_detector import IncidentDetector
from src.emergency_service import EmergencyServiceManager
from src.logger import logger

def demo_speed_tracking():
    """Demonstrate speed tracking"""
    print("\n" + "="*60)
    print("DEMO 1: SPEED TRACKING")
    print("="*60)
    
    # Create speed tracker
    tracker = SpeedTracker(fps=30, pixels_per_meter=20)
    
    # Simulate detections (from YOLO)
    # Format: {center, bbox, class_name, confidence}
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
    
    # Track vehicles over multiple frames (simulating movement)
    for frame in range(5):
        # Update positions (simulate vehicle movement)
        detections[0]['center'] = (100 + frame * 20, 100)  # Moving right at ~20 pixels/frame
        detections[1]['center'] = (200 + frame * 30, 150)  # Moving right faster
        
        tracked = tracker.match_detections(detections, 720, 1280)
        
        print(f"\nFrame {frame}:")
        for vehicle in tracked:
            print(f"  Vehicle {vehicle['track_id']}: {vehicle['class_name']}")
            print(f"    Current Speed: {vehicle['current_speed']:.1f} km/h")
            print(f"    Max Speed: {vehicle['max_speed']:.1f} km/h")
    
    # Check speeding
    speeding = tracker.get_speeding_vehicles(tracked, speed_limit=60)
    if speeding:
        print(f"\n⚠️  SPEEDING VEHICLES DETECTED:")
        for vehicle in speeding:
            print(f"  - {vehicle['class_name']}: {vehicle['speed']:.1f} km/h "
                  f"(+{vehicle['excess']:.1f} km/h over limit)")
    else:
        print(f"\n✓ No speeding vehicles detected")


def demo_incident_detection():
    """Demonstrate incident detection"""
    print("\n" + "="*60)
    print("DEMO 2: INCIDENT DETECTION")
    print("="*60)
    
    detector = IncidentDetector()
    
    # Test 1: Collision detection
    print("\nTest 1: Collision Detection (IoU-based)")
    bbox1 = (100, 100, 150, 150)  # First vehicle
    bbox2 = (140, 120, 190, 170)  # Second vehicle (overlapping)
    
    is_collision, iou = detector.check_collision(bbox1, bbox2)
    print(f"  BBox1: {bbox1}")
    print(f"  BBox2: {bbox2}")
    print(f"  IoU Value: {iou:.3f}")
    print(f"  Collision: {'YES ⚠️ ' if is_collision else 'NO ✓'}")
    
    # No collision
    bbox3 = (200, 200, 250, 250)  # Third vehicle (far away)
    is_collision, iou = detector.check_collision(bbox1, bbox3)
    print(f"\n  BBox1: {bbox1}")
    print(f"  BBox3: {bbox3}")
    print(f"  IoU Value: {iou:.3f}")
    print(f"  Collision: {'YES ⚠️ ' if is_collision else 'NO ✓'}")
    
    # Test 2: Sudden stop detection
    print("\nTest 2: Sudden Stop Detection")
    vehicle = {
        'track_id': 1,
        'class_name': 'car',
        'center': (100, 100),
        'current_speed': 5.0,  # Very slow
        'history': []
    }
    
    incident = detector.detect_sudden_stop(vehicle, prev_speed=30.0)
    if incident:
        print(f"  ⚠️ SUDDEN STOP DETECTED!")
        print(f"    Previous Speed: {incident['prev_speed']:.1f} km/h")
        print(f"    Current Speed: {incident['current_speed']:.1f} km/h")
        print(f"    Speed Drop: {incident['speed_drop']:.1f} km/h")
    else:
        print(f"  ✓ No sudden stop detected")
    
    # Test 3: Fire detection
    print("\nTest 3: Fire Detection")
    detections = [
        {'class_name': 'car', 'bbox': (100, 100, 150, 150), 'center': (125, 125), 'confidence': 0.95},
        {'class_name': 'fire', 'bbox': (200, 100, 250, 150), 'center': (225, 125), 'confidence': 0.88},
        {'class_name': 'person', 'bbox': (300, 100, 350, 200), 'center': (325, 150), 'confidence': 0.92},
    ]
    
    fires = detector.detect_fire(detections)
    if fires:
        print(f"  🔥 FIRE DETECTED!")
        for fire in fires:
            print(f"    - {fire['class_name']} (confidence: {fire['confidence']:.2f})")
    else:
        print(f"  ✓ No fire detected")


def demo_emergency_services():
    """Demonstrate emergency service system"""
    print("\n" + "="*60)
    print("DEMO 3: EMERGENCY SERVICE SYSTEM")
    print("="*60)
    
    # Initialize emergency service manager
    emergency = EmergencyServiceManager(enable_calls=False)  # Mock mode
    
    print("\n1. Ringing Alarm...")
    print("  (In real system, you would hear a beep)")
    # emergency.ring_alarm(duration=1, frequency=1000)
    
    print("\n2. Handling Speeding Vehicle...")
    speeding_vehicle = {
        'track_id': 1,
        'class_name': 'car',
        'speed': 95.0,
        'center': (100, 100)
    }
    emergency.handle_speeding_vehicle(speeding_vehicle, excess_speed=15.0)
    
    print("\n3. Handling Accident/Collision...")
    accident_info = {
        'type': 'COLLISION',
        'vehicle1_id': 1,
        'vehicle2_id': 2,
        'vehicle1_class': 'car',
        'vehicle2_class': 'truck',
        'center': (150, 150),
        'iou': 0.45
    }
    emergency.handle_accident(accident_info)
    
    print("\n4. Handling Fire Incident...")
    fire_info = {
        'class_name': 'fire',
        'confidence': 0.92,
        'bbox': (200, 100, 250, 150),
        'center': (225, 125)
    }
    emergency.handle_fire_incident(fire_info)
    
    print("\n5. Call History & Statistics...")
    stats = emergency.get_call_statistics()
    print(f"  Total Emergency Calls: {stats['total_calls']}")
    print(f"  Today's Calls: {stats['today_calls']}")
    print(f"  Calls by Service Type:")
    for service, count in stats['by_service'].items():
        print(f"    - {service}: {count}")
    print(f"  Calls by Incident Type:")
    for incident, count in stats['by_incident_type'].items():
        print(f"    - {incident}: {count}")


def demo_integrated_workflow():
    """Demonstrate integrated workflow"""
    print("\n" + "="*60)
    print("DEMO 4: INTEGRATED WORKFLOW")
    print("="*60)
    
    print("\nSimulating a traffic scene with speed monitoring and incident detection...")
    
    tracker = SpeedTracker(fps=30, pixels_per_meter=20)
    detector = IncidentDetector()
    emergency = EmergencyServiceManager(enable_calls=False)
    
    # Simulate 10 frames of traffic
    for frame_num in range(10):
        print(f"\n--- Frame {frame_num} ---")
        
        # Simulate detections
        detections = [
            {
                'center': (50 + frame_num * 15, 100 + frame_num * 2),  # Car speeding
                'bbox': (30 + frame_num * 15, 80 + frame_num * 2, 70 + frame_num * 15, 120 + frame_num * 2),
                'class_name': 'car',
                'confidence': 0.95,
                'track_id': 1
            },
            {
                'center': (200 - frame_num * 5, 200),  # Normal car
                'bbox': (180 - frame_num * 5, 180, 220 - frame_num * 5, 220),
                'class_name': 'car',
                'confidence': 0.92,
                'track_id': 2
            }
        ]
        
        # If vehicles get too close, they collide (for frames 6-8)
        if 6 <= frame_num <= 8:
            detections[1]['center'] = (60 + frame_num * 15, 100 + frame_num * 2 + 10)
            detections[1]['bbox'] = (40 + frame_num * 15, 80 + frame_num * 2, 80 + frame_num * 15, 120 + frame_num * 2)
        
        # Track vehicles
        tracked = tracker.match_detections(detections, 720, 1280)
        
        # Check for incidents
        incidents = detector.analyze_incidents(tracked, detections)
        
        # Check for speeding
        speeding = tracker.get_speeding_vehicles(tracked, speed_limit=60)
        if speeding:
            for v in speeding:
                print(f"⚠️ SPEEDING: {v['class_name']} at {v['speed']:.1f} km/h")
                if v['speed'] > 80:
                    print(f"   → POLICE CALLED")
        
        # Check for collisions
        if incidents.get('collisions'):
            print(f"🚗 COLLISION DETECTED: {len(incidents['collisions'])} collision(s)")
            print(f"   → POLICE AND AMBULANCE CALLED")
        
        if not speeding and not incidents.get('collisions'):
            print("✓ Normal traffic conditions")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI TRAFFIC MANAGEMENT - FEATURE DEMO")
    print("Speed Monitoring & Emergency Alert System")
    print("="*60)
    
    try:
        demo_speed_tracking()
        demo_incident_detection()
        demo_emergency_services()
        demo_integrated_workflow()
        
        print("\n" + "="*60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nNext Steps:")
        print("1. Review the demo output above")
        print("2. Check config/config.py for calibration")
        print("3. Run: python main_fixed.py")
        print("4. Monitor: tail -f logs/traffic_management.log")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
