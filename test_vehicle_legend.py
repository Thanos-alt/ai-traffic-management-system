#!/usr/bin/env python
"""Test vehicle detection counts - Person, Motorcycle, and Vehicles"""

import cv2
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.config import CONFIDENCE_THRESHOLD, IOU_THRESHOLD
from src.camera_handler import CameraHandler
from src.traffic_detector import TrafficDetector
from src.logger import logger

print("✓ Testing detection counts: Person, Motorcycle, Vehicle")
print("=" * 60)

# Initialize components
camera = CameraHandler(0)
detector = TrafficDetector()

def draw_detection_stats(frame, person_count, motorcycle_count, vehicle_count):
    """Draw detection statistics on frame"""
    # Create background panel
    panel_width = 320
    panel_height = 200
    panel_x, panel_y = 10, 50
    
    # Semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (panel_x, panel_y), 
                  (panel_x + panel_width, panel_y + panel_height),
                  (50, 50, 50), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Draw border
    cv2.rectangle(frame, (panel_x, panel_y),
                  (panel_x + panel_width, panel_y + panel_height),
                  (0, 255, 255), 2)
    
    # Title
    cv2.putText(frame, "DETECTION ANALYSIS", (panel_x + 15, panel_y + 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    
    # Divider line
    cv2.line(frame, (panel_x + 10, panel_y + 38), 
             (panel_x + panel_width - 10, panel_y + 38), (100, 100, 100), 1)
    
    # Person section (Yellow)
    cv2.putText(frame, "PERSON", (panel_x + 15, panel_y + 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
    cv2.putText(frame, f"Count: {person_count}", (panel_x + 150, panel_y + 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
    
    # Divider line
    cv2.line(frame, (panel_x + 10, panel_y + 75), 
             (panel_x + panel_width - 10, panel_y + 75), (100, 100, 100), 1)
    
    # Motorcycle section (Cyan)
    cv2.putText(frame, "MOTORCYCLE", (panel_x + 15, panel_y + 102),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 1)
    cv2.putText(frame, f"Count: {motorcycle_count}", (panel_x + 150, panel_y + 102),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
    
    # Divider line
    cv2.line(frame, (panel_x + 10, panel_y + 112), 
             (panel_x + panel_width - 10, panel_y + 112), (100, 100, 100), 1)
    
    # Vehicle section (Blue)
    cv2.putText(frame, "VEHICLES", (panel_x + 15, panel_y + 139),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 1)
    cv2.putText(frame, f"Count: {vehicle_count}", (panel_x + 150, panel_y + 139),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)
    
    # Divider line
    cv2.line(frame, (panel_x + 10, panel_y + 149), 
             (panel_x + panel_width - 10, panel_y + 149), (100, 100, 100), 1)
    
    # Total section (Green)
    total = person_count + motorcycle_count + vehicle_count
    cv2.putText(frame, "TOTAL", (panel_x + 15, panel_y + 176),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)
    cv2.putText(frame, f"Count: {total}", (panel_x + 150, panel_y + 176),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
    
    return frame

print("\nStarting camera feed...")
print("Press:")
print("  [Q] - Quit")
print("  [P] - Pause/Resume")
print("=" * 60)

running = True
paused = False

try:
    while running:
        frame = camera.get_frame()
        if frame is None:
            continue
        
        # Get ALL detections including persons, motorcycles, and vehicles
        result = detector.detect_all_objects(frame)
        all_detections = result["all_detections"]
        person_count = result["person_count"]
        motorcycle_count = result["motorcycle_count"]
        vehicle_count = result["vehicle_count"]
        
        # Draw all detections with proper colors
        # Persons (Yellow)
        for detection in all_detections["person"]:
            x1, y1, x2, y2 = detection["bbox"]
            confidence = detection["confidence"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
            label = f"Person {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        
        # Motorcycles (Cyan)
        for detection in all_detections["motorcycle"]:
            x1, y1, x2, y2 = detection["bbox"]
            confidence = detection["confidence"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            label = f"Motorcycle {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        # Vehicles (Blue)
        for detection in all_detections["vehicle"]:
            x1, y1, x2, y2 = detection["bbox"]
            confidence = detection["confidence"]
            class_name = detection["class_name"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            label = f"{class_name} {confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Draw stats panel
        frame_with_stats = draw_detection_stats(frame, person_count, motorcycle_count, vehicle_count)
        
        # Display
        cv2.imshow("Detection: Person | Motorcycle | Vehicle", frame_with_stats)
        
        # Keyboard control
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            print("\nQuitting...")
            running = False
        elif key == ord('p'):
            paused = not paused
            status = "PAUSED" if paused else "RUNNING"
            print(f"Application {status}")
            if paused:
                cv2.waitKey(0)

except KeyboardInterrupt:
    print("\nInterrupted by user")
finally:
    camera.stop_capture()
    cv2.destroyAllWindows()
    print("✓ Test completed")
    print("\nDetection Legend:")
    print("  - YELLOW box  = Person (class 0)")
    print("  - CYAN box    = Motorcycle (class 3)")
    print("  - BLUE box    = Vehicles: Car, Bus, Truck (classes 2, 5, 7)")


