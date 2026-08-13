"""Incident detection - accidents, collisions, and fires"""

import cv2
import numpy as np
from collections import defaultdict
from src.logger import logger

class IncidentDetector:
    """Detect traffic incidents - accidents, collisions, fires"""
    
    def __init__(self):
        self.collision_threshold = 0.3  # IoU threshold for collision detection
        self.accident_history = []
        self.near_miss_threshold = 50  # pixels - distance threshold for near miss
        self.speed_drop_threshold = 10  # km/h - threshold for sudden stop
        self.suspicious_stationary_frames = 30  # frames threshold
        
    def check_collision(self, bbox1, bbox2):
        """
        Check if two bounding boxes collide (IoU > threshold)
        
        Args:
            bbox1: (x1, y1, x2, y2)
            bbox2: (x1, y1, x2, y2)
            
        Returns:
            (is_collision, iou_value)
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection area
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        if xi2 < xi1 or yi2 < yi1:
            return False, 0.0
        
        intersection = (xi2 - xi1) * (yi2 - yi1)
        
        # Calculate union area
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return False, 0.0
        
        iou = intersection / union
        return iou > self.collision_threshold, iou
    
    def detect_collision_between_vehicles(self, tracked_vehicles):
        """
        Detect collisions between vehicles
        
        Args:
            tracked_vehicles: List of tracked vehicles with bbox
            
        Returns:
            List of collision incidents
        """
        collisions = []
        
        for i, vehicle1 in enumerate(tracked_vehicles):
            for vehicle2 in tracked_vehicles[i+1:]:
                is_collision, iou = self.check_collision(vehicle1['bbox'], vehicle2['bbox'])
                
                if is_collision:
                    collisions.append({
                        'type': 'COLLISION',
                        'vehicle1_id': vehicle1['track_id'],
                        'vehicle2_id': vehicle2['track_id'],
                        'vehicle1_class': vehicle1['class_name'],
                        'vehicle2_class': vehicle2['class_name'],
                        'center': (
                            (vehicle1['center'][0] + vehicle2['center'][0]) // 2,
                            (vehicle1['center'][1] + vehicle2['center'][1]) // 2
                        ),
                        'iou': iou
                    })
        
        return collisions
    
    def detect_sudden_stop(self, vehicle, prev_speed=None):
        """
        Detect sudden deceleration (possible accident)
        
        Args:
            vehicle: Current vehicle with speed info
            prev_speed: Previous frame speed
            
        Returns:
            Incident dict if detected, else None
        """
        if prev_speed is None:
            return None
        
        speed_drop = prev_speed - vehicle['current_speed']
        
        if speed_drop >= self.speed_drop_threshold:
            return {
                'type': 'SUDDEN_STOP',
                'vehicle_id': vehicle['track_id'],
                'vehicle_class': vehicle['class_name'],
                'center': vehicle['center'],
                'prev_speed': prev_speed,
                'current_speed': vehicle['current_speed'],
                'speed_drop': speed_drop
            }
        
        return None
    
    def detect_standstill(self, vehicle, frames_count=None):
        """
        Detect vehicle standing still (possible accident or breakdown)
        
        Args:
            vehicle: Vehicle with history
            frames_count: Number of frames vehicle has been stationary
            
        Returns:
            Incident dict if suspicious, else None
        """
        if len(vehicle['history']) < 2:
            return None
        
        # Check if vehicle hasn't moved much in last few frames
        recent_positions = vehicle['history'][-5:]
        
        if len(recent_positions) >= 2:
            positions = np.array([h['center'] for h in recent_positions])
            distances = np.linalg.norm(np.diff(positions, axis=0), axis=1)
            avg_distance = np.mean(distances)
            
            # If average distance moved is very small and speed is low
            if avg_distance < 5 and vehicle['current_speed'] < 2:
                frames_held = len([h for h in vehicle['history'] if np.linalg.norm(h['center'] - positions[-1]) < 10])
                
                if frames_held > self.suspicious_stationary_frames:
                    return {
                        'type': 'STANDSTILL',
                        'vehicle_id': vehicle['track_id'],
                        'vehicle_class': vehicle['class_name'],
                        'center': vehicle['center'],
                        'frames_held': frames_held,
                        'current_speed': vehicle['current_speed']
                    }
        
        return None
    
    def detect_fire(self, detections):
        """
        Detect fire in detections (by class)
        
        Args:
            detections: List of detections from YOLO
            
        Returns:
            List of fire detections
        """
        fires = []
        
        for det in detections:
            # Check if class is fire-related (you may need to update based on your YOLO model)
            # Common fire classes: 'fire', 'smoke', 'flame', 'burning'
            class_name = det['class_name'].lower()
            
            if 'fire' in class_name or 'flame' in class_name or 'smoke' in class_name or 'burn' in class_name:
                fires.append({
                    'type': 'FIRE',
                    'class_name': det['class_name'],
                    'bbox': det['bbox'],
                    'center': det['center'],
                    'confidence': det['confidence']
                })
        
        return fires
    
    def analyze_incidents(self, tracked_vehicles, all_detections):
        """
        Comprehensive incident detection
        
        Args:
            tracked_vehicles: List of tracked vehicles
            all_detections: All YOLO detections from frame
            
        Returns:
            Dict with all detected incidents
        """
        incidents = {
            'collisions': self.detect_collision_between_vehicles(tracked_vehicles),
            'fires': self.detect_fire(all_detections),
            'sudden_stops': [],
            'standstills': []
        }
        
        # Check for sudden stops and standstills
        for vehicle in tracked_vehicles:
            if len(vehicle['history']) > 1:
                prev_speed = vehicle['history'][-2].get('speed_kmh', 0)
                
                sudden_stop = self.detect_sudden_stop(vehicle, prev_speed)
                if sudden_stop:
                    incidents['sudden_stops'].append(sudden_stop)
                
                standstill = self.detect_standstill(vehicle)
                if standstill:
                    incidents['standstills'].append(standstill)
        
        return incidents
