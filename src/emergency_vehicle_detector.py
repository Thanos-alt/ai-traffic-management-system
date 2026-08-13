"""Emergency vehicle detection system"""

import cv2
import numpy as np
from src.logger import logger


class EmergencyVehicleDetector:
    """Detects emergency vehicles (ambulance, police, fire truck)"""
    
    EMERGENCY_TYPES = {
        "ambulance": "🚑",
        "police": "🚔",
        "fire_truck": "🚒"
    }
    
    def __init__(self):
        """Initialize emergency vehicle detector"""
        self.detected_emergency = None
        self.emergency_lane = None
        self.confidence_threshold = 0.5
    
    def detect_emergency_vehicles(self, detections, frame=None):
        """
        Detect emergency vehicles from detections
        
        Method 1: Class name matching (if using custom model)
        Method 2: Color-based detection for known patterns
        
        Args:
            detections: List of all detections
            frame: Optional frame for color-based detection
            
        Returns:
            Dictionary with emergency vehicle info or None
        """
        emergency_vehicle = None
        
        for detection in detections:
            class_name = detection["class_name"].lower()
            bbox = detection["bbox"]
            center = detection["center"]
            
            # Method 1: Direct class name matching
            if "ambulance" in class_name:
                emergency_vehicle = {
                    "type": "ambulance",
                    "confidence": detection["confidence"],
                    "bbox": bbox,
                    "center": center,
                    "class_name": detection["class_name"]
                }
                break
            elif "police" in class_name or "police car" in class_name:
                emergency_vehicle = {
                    "type": "police",
                    "confidence": detection["confidence"],
                    "bbox": bbox,
                    "center": center,
                    "class_name": detection["class_name"]
                }
                break
            elif "fire" in class_name or "fire truck" in class_name:
                emergency_vehicle = {
                    "type": "fire_truck",
                    "confidence": detection["confidence"],
                    "bbox": bbox,
                    "center": center,
                    "class_name": detection["class_name"]
                }
                break
            
            # Method 2: Color-based detection for cars
            elif class_name == "car" and frame is not None:
                detected_type = self._detect_by_color(frame, bbox)
                if detected_type:
                    emergency_vehicle = {
                        "type": detected_type,
                        "confidence": detection["confidence"],
                        "bbox": bbox,
                        "center": center,
                        "class_name": detection["class_name"],
                        "method": "color_detection"
                    }
                    break
        
        if emergency_vehicle:
            self.detected_emergency = emergency_vehicle
            logger.warning(f"🚨 EMERGENCY VEHICLE DETECTED: {emergency_vehicle['type'].upper()}")
        
        return emergency_vehicle
    
    def _detect_by_color(self, frame, bbox):
        """
        Detect emergency vehicle type by color patterns
        
        Args:
            frame: Video frame
            bbox: Bounding box (x1, y1, x2, y2)
            
        Returns:
            Emergency type or None
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # Extract region
            roi = frame[y1:y2, x1:x2]
            if roi.size == 0:
                return None
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Red color range (for ambulance and fire truck)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 100, 100])
            upper_red2 = np.array([180, 255, 255])
            
            mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
            red_pixels = np.count_nonzero(mask_red)
            
            # Blue color range (for police)
            lower_blue = np.array([100, 100, 100])
            upper_blue = np.array([130, 255, 255])
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            blue_pixels = np.count_nonzero(mask_blue)
            
            # White color range (common in ambulances)
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 30, 255])
            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            white_pixels = np.count_nonzero(mask_white)
            
            total_pixels = roi.size / 3  # HSV has 3 channels
            
            # Determine type based on dominant color
            red_ratio = red_pixels / total_pixels if total_pixels > 0 else 0
            blue_ratio = blue_pixels / total_pixels if total_pixels > 0 else 0
            white_ratio = white_pixels / total_pixels if total_pixels > 0 else 0
            
            # Red + White = likely ambulance
            if (red_ratio + white_ratio) > 0.15:
                return "ambulance"
            # Blue = likely police
            elif blue_ratio > 0.1:
                return "police"
            # Red only = likely fire truck
            elif red_ratio > 0.15:
                return "fire_truck"
            
            return None
        
        except Exception as e:
            logger.debug(f"Color detection error: {e}")
            return None
    
    def get_emergency_type_emoji(self, emergency_type):
        """Get emoji for emergency type"""
        return self.EMERGENCY_TYPES.get(emergency_type, "🚨")
    
    def clear_detection(self):
        """Clear current detection"""
        self.detected_emergency = None
        self.emergency_lane = None
    
    def has_active_emergency(self):
        """Check if emergency vehicle is currently detected"""
        return self.detected_emergency is not None
    
    def get_last_emergency(self):
        """Get last detected emergency"""
        return self.detected_emergency
