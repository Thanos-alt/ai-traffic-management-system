#!/usr/bin/env python3
"""
Verification script to show speed tracking integration in main.py
"""

import sys
from pathlib import Path

def check_integration():
    """Verify speed tracking integration in main.py"""
    
    main_py = Path("main.py")
    if not main_py.exists():
        print("❌ main.py not found")
        return False
    
    content = main_py.read_text()
    
    checks = {
        "Imports": {
            "SpeedTracker": "from src.speed_tracker import SpeedTracker",
            "IncidentDetector": "from src.incident_detector import IncidentDetector",
            "EmergencyService": "from src.emergency_service import EmergencyServiceManager",
        },
        "Initialization": {
            "speed_tracker init": "self.speed_tracker = SpeedTracker()",
            "incident_detector init": "self.incident_detector = IncidentDetector()",
            "emergency_service init": "self.emergency_service = EmergencyServiceManager()",
        },
        "Speed Stats Storage": {
            "speed_stats dict": "self.last_speed_stats = {",
            "avg_speed": '"avg_speed"',
            "max_speed": '"max_speed"',
            "speeding_count": '"speeding_count"',
        },
        "Speed Tracking Logic": {
            "match_detections": "self.speed_tracker.match_detections(",
            "get_speeding_vehicles": "self.speed_tracker.get_speeding_vehicles(",
            "get_speed_statistics": "self.speed_tracker.get_speed_statistics(",
        },
        "Incident Detection": {
            "analyze_incidents": "self.incident_detector.analyze_incidents(",
            "handle_collision": "self.emergency_service.handle_collision(",
            "handle_fire": "self.emergency_service.handle_fire(",
            "handle_speeding": "self.emergency_service.handle_speeding(",
        },
        "Speed Display": {
            "speed_color logic": "speed_color = (0, 255, 0) if avg_speed < 60",
            "speed_info display": 'speed_info = f"{speed:.1f} km/h',
            "speed on label": 'label = f"{label} | {speed_info}"',
        },
        "Dashboard Updates": {
            "avg_speed display": 'f"Avg Speed: {avg_speed:.1f} km/h"',
            "max_speed display": 'f"Speeding: {speeding_count} | Max: {max_speed:.1f}"',
            "dashboard height": 'cv2.rectangle(frame, (5, 60), (170, 145)',
        },
        "Console Output": {
            "frame stats print": 'print(f"Frame {self.frame_count}: Vehicles={',
            "avg_speed output": 'Avg Speed={avg_speed:.1f}',
            "speeding output": 'Speeding={speeding_count}',
        },
    }
    
    total_checks = 0
    passed_checks = 0
    
    print("\n" + "="*70)
    print("SPEED TRACKING INTEGRATION VERIFICATION - main.py")
    print("="*70)
    
    for category, items in checks.items():
        print(f"\n📋 {category}:")
        for item_name, search_string in items.items():
            total_checks += 1
            if search_string in content:
                passed_checks += 1
                print(f"  ✅ {item_name}")
            else:
                print(f"  ❌ {item_name}")
    
    print("\n" + "="*70)
    print(f"RESULT: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("✅ ALL INTEGRATIONS VERIFIED - main.py is ready!")
    elif passed_checks >= total_checks * 0.9:
        print("⚠️  Most integrations OK, minor checks missing")
    else:
        print("❌ Integration incomplete, check above")
    
    print("="*70 + "\n")
    
    return passed_checks == total_checks

def show_features():
    """Show what features are now available"""
    print("\n" + "🚀 NEW FEATURES IN main.py:\n")
    
    features = [
        ("Real-time Speed Tracking", "Measures vehicle speed frame-to-frame"),
        ("Color-coded Speed Display", "Green (<60), Orange (60-80), Red (>80) km/h"),
        ("Dashboard Speed Panel", "Shows Avg Speed, Max Speed, Speeding count"),
        ("Incident Detection", "Collision, Fire, Accident detection"),
        ("Emergency Response", "Police call for >80 km/h speeding"),
        ("Console Speed Output", "Frame statistics with speed info every second"),
        ("HSR Integration", "Auto-activates for incidents/speeding"),
        ("Voice Alerts", "Audio warnings for speeding/collisions/fire"),
        ("Thread-safe Processing", "Separate detection thread, safe display thread"),
        ("Automatic Calibration", "Uses PIXELS_PER_METER from config"),
    ]
    
    for i, (feature, description) in enumerate(features, 1):
        print(f"  {i}. {feature}")
        print(f"     └─ {description}")
    
    print()

def show_usage():
    """Show how to use the new features"""
    print("\n" + "📖 HOW TO USE:\n")
    
    print("1. Run with speed tracking:")
    print("   $ python main.py\n")
    
    print("2. Monitor console output:")
    print("   Frame 1: Vehicles=5 | Avg Speed=45.3 | Max Speed=78.2 | Speeding=0\n")
    
    print("3. Watch video display for:")
    print("   • Speed labels on vehicles (color-coded)")
    print("   • Dashboard speed statistics (top-left)")
    print("   • Speed warnings in console\n")
    
    print("4. Listen for alerts:")
    print("   • Speeding (>80 km/h) → Police call")
    print("   • Incident detected → Emergency services\n")
    
    print("5. Controls:")
    print("   • Press 'q' to quit")
    print("   • Press 'p' to pause")
    print("   • Press 's' to save frame\n")

if __name__ == "__main__":
    try:
        # Check integration
        success = check_integration()
        
        # Show features
        show_features()
        
        # Show usage
        show_usage()
        
        # Exit code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
