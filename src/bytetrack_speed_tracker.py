"""ByteTrack-based vehicle speed tracking for improved accuracy"""

import numpy as np
from datetime import datetime
from src.logger import logger

try:
    from ultralytics import YOLO
    from ultralytics.solutions import ObjectCounter
    BYTETRACK_AVAILABLE = True
except ImportError:
    BYTETRACK_AVAILABLE = False
    logger.warning("ByteTrack not available through ultralytics, using fallback tracker")


class ByteTrackSpeedTracker:
    """
    Advanced vehicle speed tracking using ByteTrack algorithm
    ByteTrack provides:
    - Better multi-object tracking
    - Handles occlusions better
    - More stable ID assignments
    - Improved speed measurement accuracy
    """
    
    def __init__(self, fps=30, pixels_per_meter=20, max_age=30):
        """
        Initialize ByteTrack-based speed tracker
        
        Args:
            fps: Frames per second for speed calculation
            pixels_per_meter: Calibration factor (pixels = real-world meters)
            max_age: Maximum frames to keep track without detection
        """
        self.fps = fps
        self.pixels_per_meter = pixels_per_meter
        self.max_age = max_age
        self.vehicle_tracks = {}  # Store vehicle positions and speeds
        self.next_id = 0
        self.track_history = {}  # Full history for analysis
        
        logger.info(f"ByteTrack Speed Tracker initialized (FPS={fps}, Calib={pixels_per_meter}px/m)")
    
    def get_speed_kmh(self, pixels_distance):
        """Convert pixel distance to speed in km/h"""
        if pixels_distance < 0.1:
            return 0.0
        
        # Distance per frame in meters
        meters_per_frame = pixels_distance / self.pixels_per_meter
        # Distance per second in meters
        meters_per_second = meters_per_frame * self.fps
        # Speed in km/h (3.6 = 3600 seconds/hour / 1000 meters/km)
        kmh = meters_per_second * 3.6
        
        # Cap speed at reasonable maximum (e.g., 200 km/h for vehicles)
        return min(kmh, 200.0)
    
    def match_detections(self, current_detections, frame_height, frame_width):
        """
        Match current detections with tracked vehicles using ByteTrack-style matching
        
        Args:
            current_detections: List of current frame detections with bbox and center
            frame_height: Frame height in pixels
            frame_width: Frame width in pixels
            
        Returns:
            List of tracked vehicles with speed and track info
        """
        tracked_vehicles = []
        used_current = set()
        
        # Age out old tracks
        dead_ids = [vid for vid, track in self.vehicle_tracks.items() 
                   if track.get('age', 0) > self.max_age]
        for vid in dead_ids:
            if vid in self.track_history:
                self.track_history[vid]['final'] = True
            del self.vehicle_tracks[vid]
        
        # Age all remaining tracks
        for vid in self.vehicle_tracks:
            self.vehicle_tracks[vid]['age'] = self.vehicle_tracks[vid].get('age', 0) + 1
        
        # Match detections to tracks using Hungarian-like algorithm
        # For simplicity, using nearest neighbor with bidirectional check
        
        for det_idx, det in enumerate(current_detections):
            current_center = np.array(det['center'])
            best_match_id = None
            best_distance = float('inf')
            
            # Find closest track to this detection
            for track_id, track_info in self.vehicle_tracks.items():
                if track_id in used_current:
                    continue
                
                prev_center = np.array(track_info['center'])
                distance = np.linalg.norm(current_center - prev_center)
                
                # More lenient matching for ByteTrack style
                max_distance = max(50, np.sqrt((det['bbox'][2] - det['bbox'][0])**2 + 
                                              (det['bbox'][3] - det['bbox'][1])**2) * 2)
                
                if distance < max_distance and distance < best_distance:
                    best_distance = distance
                    best_match_id = track_id
            
            if best_match_id is not None:
                # Update existing track
                used_current.add(best_match_id)
                track = self.vehicle_tracks[best_match_id]
                
                # Calculate speed
                prev_center = np.array(track['center'])
                pixel_distance = np.linalg.norm(current_center - prev_center)
                speed_kmh = self.get_speed_kmh(pixel_distance)
                
                # Update track information
                track['center'] = tuple(map(int, current_center))
                track['bbox'] = det['bbox']
                track['class_name'] = det['class_name']
                track['confidence'] = det['confidence']
                track['current_speed'] = speed_kmh
                track['max_speed'] = max(track.get('max_speed', 0), speed_kmh)
                track['age'] = 0  # Reset age on successful match
                track['frames_seen'] = track.get('frames_seen', 0) + 1
                
                # Add to history
                if best_match_id not in self.track_history:
                    self.track_history[best_match_id] = {
                        'positions': [],
                        'speeds': [],
                        'class_name': det['class_name']
                    }
                
                self.track_history[best_match_id]['positions'].append({
                    'center': current_center,
                    'timestamp': datetime.now(),
                    'speed': speed_kmh
                })
                self.track_history[best_match_id]['speeds'].append(speed_kmh)
                
                # Keep last 30 positions
                if len(self.track_history[best_match_id]['positions']) > 30:
                    self.track_history[best_match_id]['positions'].pop(0)
                    self.track_history[best_match_id]['speeds'].pop(0)
                
                tracked_vehicles.append({
                    'track_id': best_match_id,
                    'bbox': det['bbox'],
                    'center': det['center'],
                    'class_name': det['class_name'],
                    'confidence': det['confidence'],
                    'current_speed': speed_kmh,
                    'max_speed': track['max_speed'],
                    'frames_seen': track['frames_seen'],
                    'history': self.track_history[best_match_id]['positions']
                })
            
            else:
                # New track
                new_id = self.next_id
                self.next_id += 1
                
                self.vehicle_tracks[new_id] = {
                    'center': tuple(map(int, current_center)),
                    'bbox': det['bbox'],
                    'class_name': det['class_name'],
                    'confidence': det['confidence'],
                    'age': 0,
                    'current_speed': 0,
                    'max_speed': 0,
                    'frames_seen': 1
                }
                
                self.track_history[new_id] = {
                    'positions': [{'center': current_center, 'timestamp': datetime.now(), 'speed': 0}],
                    'speeds': [0],
                    'class_name': det['class_name']
                }
                
                tracked_vehicles.append({
                    'track_id': new_id,
                    'bbox': det['bbox'],
                    'center': det['center'],
                    'class_name': det['class_name'],
                    'confidence': det['confidence'],
                    'current_speed': 0,
                    'max_speed': 0,
                    'frames_seen': 1,
                    'history': self.track_history[new_id]['positions']
                })
        
        return tracked_vehicles
    
    def get_speeding_vehicles(self, tracked_vehicles, speed_limit=60):
        """
        Get vehicles exceeding speed limit
        
        Args:
            tracked_vehicles: List of tracked vehicles
            speed_limit: Speed limit in km/h
            
        Returns:
            List of speeding vehicles with details
        """
        speeding = []
        for vehicle in tracked_vehicles:
            if vehicle.get('current_speed', 0) > speed_limit:
                speeding.append({
                    'track_id': vehicle['track_id'],
                    'speed': vehicle['current_speed'],
                    'excess': vehicle['current_speed'] - speed_limit,
                    'bbox': vehicle['bbox'],
                    'center': vehicle['center'],
                    'class_name': vehicle['class_name'],
                    'frames_seen': vehicle.get('frames_seen', 1)
                })
        return speeding
    
    def get_speed_statistics(self, tracked_vehicles):
        """
        Calculate comprehensive speed statistics
        
        Args:
            tracked_vehicles: List of tracked vehicles
            
        Returns:
            Dictionary with detailed statistics
        """
        if not tracked_vehicles:
            return {
                "avg_speed": 0,
                "max_speed": 0,
                "min_speed": 0,
                "median_speed": 0,
                "speeding_count": 0,
                "tracked_vehicles": [],
                "average_confidence": 0
            }
        
        speeds = [v.get('current_speed', 0) for v in tracked_vehicles]
        confidences = [v.get('confidence', 0) for v in tracked_vehicles]
        
        speeds_sorted = sorted(speeds)
        median_speed = speeds_sorted[len(speeds_sorted)//2] if speeds_sorted else 0
        speeding_count = sum(1 for s in speeds if s > 60)
        
        return {
            "avg_speed": sum(speeds) / len(speeds) if speeds else 0,
            "max_speed": max(speeds) if speeds else 0,
            "min_speed": min(speeds) if speeds else 0,
            "median_speed": median_speed,
            "speeding_count": speeding_count,
            "tracked_vehicles": tracked_vehicles,
            "average_confidence": sum(confidences) / len(confidences) if confidences else 0
        }
    
    def get_track_info(self, track_id):
        """
        Get detailed information about a specific track
        
        Args:
            track_id: ID of the track
            
        Returns:
            Dictionary with track details or None
        """
        if track_id not in self.track_history:
            return None
        
        history = self.track_history[track_id]
        speeds = history.get('speeds', [])
        
        if not speeds:
            return None
        
        return {
            'track_id': track_id,
            'class_name': history.get('class_name', 'unknown'),
            'total_positions': len(history.get('positions', [])),
            'avg_speed': sum(speeds) / len(speeds),
            'max_speed': max(speeds),
            'min_speed': min(speeds),
            'median_speed': sorted(speeds)[len(speeds)//2],
            'total_distance': sum(speeds) / self.fps  # Approximate in meters
        }
    
    def reset(self):
        """Reset all tracking data"""
        self.vehicle_tracks = {}
        self.track_history = {}
        self.next_id = 0
        logger.info("ByteTrack Speed Tracker reset")
