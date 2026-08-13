"""
OpenCV-based Speed Detection Engine
Provides core tools for measuring vehicle speeds from video
"""

import cv2
import numpy as np
import math
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class SpeedMeasurement:
    """Single speed measurement data"""
    vehicle_id: int
    speed_kmh: float
    speed_mph: float
    distance_pixels: float
    distance_meters: float
    timestamp: datetime
    confidence: float


class OpenCVSpeedDetector:
    """
    Core OpenCV-based speed detection engine
    Handles video processing and speed calculations
    """
    
    def __init__(self, pixels_per_meter: float = 20.0, fps: float = 30.0):
        """
        Initialize speed detector
        
        Args:
            pixels_per_meter: Calibration value (pixels per 1 meter in real world)
            fps: Frames per second of video
        """
        self.pixels_per_meter = pixels_per_meter
        self.fps = fps
        self.frame_delay = 1 / fps
        
        # Speed measurement history
        self.speed_history: Dict[int, List[float]] = {}
        self.position_history: Dict[int, Tuple[float, float]] = {}
        self.measurements: List[SpeedMeasurement] = []
        self.next_vehicle_id = 1
        
    def pixels_to_meters(self, pixels: float) -> float:
        """Convert pixel distance to meters"""
        return pixels / self.pixels_per_meter
    
    def meters_to_kmh(self, meters: float, time_seconds: float) -> float:
        """Convert meter distance and time to km/h"""
        if time_seconds == 0:
            return 0
        mps = meters / time_seconds
        kmh = mps * 3.6
        return kmh
    
    def meters_to_mph(self, meters: float, time_seconds: float) -> float:
        """Convert meter distance and time to mph"""
        if time_seconds == 0:
            return 0
        mps = meters / time_seconds
        mph = mps * 2.237
        return mph
    
    def calculate_distance(self, point1: Tuple[float, float], 
                          point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def calculate_speed(self, vehicle_id: int, 
                       current_pos: Tuple[float, float],
                       prev_pos: Optional[Tuple[float, float]] = None,
                       frames_elapsed: int = 1) -> Optional[SpeedMeasurement]:
        """
        Calculate speed for a vehicle between two positions
        
        Args:
            vehicle_id: Unique vehicle identifier
            current_pos: Current position (x, y)
            prev_pos: Previous position (x, y). If None, uses last stored position
            frames_elapsed: Number of frames between measurements
            
        Returns:
            SpeedMeasurement object or None if insufficient data
        """
        if vehicle_id not in self.position_history and prev_pos is None:
            self.position_history[vehicle_id] = current_pos
            return None
        
        if prev_pos is None:
            prev_pos = self.position_history.get(vehicle_id, current_pos)
        
        # Calculate distance
        distance_pixels = self.calculate_distance(prev_pos, current_pos)
        distance_meters = self.pixels_to_meters(distance_pixels)
        
        # Calculate time
        time_seconds = frames_elapsed * self.frame_delay
        
        # Calculate speeds
        speed_kmh = self.meters_to_kmh(distance_meters, time_seconds)
        speed_mph = self.meters_to_mph(distance_meters, time_seconds)
        
        # Update history
        self.position_history[vehicle_id] = current_pos
        if vehicle_id not in self.speed_history:
            self.speed_history[vehicle_id] = []
        self.speed_history[vehicle_id].append(speed_kmh)
        
        # Create measurement
        measurement = SpeedMeasurement(
            vehicle_id=vehicle_id,
            speed_kmh=speed_kmh,
            speed_mph=speed_mph,
            distance_pixels=distance_pixels,
            distance_meters=distance_meters,
            timestamp=datetime.now(),
            confidence=0.95
        )
        
        self.measurements.append(measurement)
        return measurement
    
    def get_average_speed(self, vehicle_id: int) -> Tuple[float, float]:
        """Get average speed for a vehicle"""
        if vehicle_id not in self.speed_history:
            return 0.0, 0.0
        
        speeds = self.speed_history[vehicle_id]
        if not speeds:
            return 0.0, 0.0
        
        avg_kmh = np.mean(speeds)
        avg_mph = avg_kmh / 1.609
        return avg_kmh, avg_mph
    
    def get_max_speed(self, vehicle_id: int) -> Tuple[float, float]:
        """Get maximum speed recorded for a vehicle"""
        if vehicle_id not in self.speed_history:
            return 0.0, 0.0
        
        speeds = self.speed_history[vehicle_id]
        if not speeds:
            return 0.0, 0.0
        
        max_kmh = np.max(speeds)
        max_mph = max_kmh / 1.609
        return max_kmh, max_mph
    
    def calibrate_with_reference(self, reference_distance_meters: float,
                                 reference_distance_pixels: float) -> None:
        """
        Calibrate the system using a known reference distance
        
        Args:
            reference_distance_meters: Known real-world distance in meters
            reference_distance_pixels: Pixel distance measured in video
        """
        self.pixels_per_meter = reference_distance_pixels / reference_distance_meters
    
    def reset_vehicle(self, vehicle_id: int) -> None:
        """Reset tracking data for a specific vehicle"""
        if vehicle_id in self.speed_history:
            del self.speed_history[vehicle_id]
        if vehicle_id in self.position_history:
            del self.position_history[vehicle_id]
    
    def reset_all(self) -> None:
        """Reset all tracking data"""
        self.speed_history.clear()
        self.position_history.clear()
        self.measurements.clear()
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        if not self.measurements:
            return {
                'total_vehicles': 0,
                'avg_speed_kmh': 0,
                'max_speed_kmh': 0,
                'min_speed_kmh': 0,
                'measurements': 0
            }
        
        speeds_kmh = [m.speed_kmh for m in self.measurements]
        unique_vehicles = len(set(m.vehicle_id for m in self.measurements))
        
        return {
            'total_vehicles': unique_vehicles,
            'avg_speed_kmh': float(np.mean(speeds_kmh)),
            'max_speed_kmh': float(np.max(speeds_kmh)),
            'min_speed_kmh': float(np.min(speeds_kmh)),
            'measurements': len(self.measurements),
            'pixels_per_meter': self.pixels_per_meter,
            'fps': self.fps
        }


class CalibrationTool:
    """Tool for calibrating pixels-to-meter ratio"""
    
    def __init__(self):
        self.point1: Optional[Tuple[int, int]] = None
        self.point2: Optional[Tuple[int, int]] = None
        self.drawing = False
        
    def draw_calibration_line(self, frame: np.ndarray,
                             real_world_distance_m: float) -> np.ndarray:
        """
        Interactive calibration - draw a line on the frame
        Returns calibration line visualization
        """
        frame_copy = frame.copy()
        
        if self.point1 and self.point2:
            cv2.line(frame_copy, self.point1, self.point2, (0, 255, 0), 2)
            cv2.circle(frame_copy, self.point1, 5, (255, 0, 0), -1)
            cv2.circle(frame_copy, self.point2, 5, (255, 0, 0), -1)
            
            distance = math.sqrt((self.point2[0] - self.point1[0])**2 + 
                               (self.point2[1] - self.point1[1])**2)
            pixels_per_meter = distance / real_world_distance_m
            
            cv2.putText(frame_copy, 
                       f"Pixels/Meter: {pixels_per_meter:.1f}",
                       (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX,
                       1, (0, 255, 0), 2)
        
        return frame_copy
    
    def mouse_callback(self, event, x, y, flags, param):
        """Mouse callback for calibration drawing"""
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.point1:
                self.point1 = (x, y)
            elif not self.point2:
                self.point2 = (x, y)
        elif event == cv2.EVENT_RBUTTONDOWN:
            self.point1 = None
            self.point2 = None


class VideoAnalyzer:
    """Video analysis utilities"""
    
    @staticmethod
    def get_video_info(video_path: str) -> Dict:
        """Get video information"""
        cap = cv2.VideoCapture(video_path)
        
        info = {
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'duration_seconds': int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)),
            'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
        }
        
        cap.release()
        return info
    
    @staticmethod
    def draw_speed_overlay(frame: np.ndarray, 
                          speed_kmh: float,
                          speed_mph: float,
                          position: Tuple[int, int],
                          color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """Draw speed text on frame"""
        text = f"{speed_kmh:.1f} km/h ({speed_mph:.1f} mph)"
        cv2.putText(frame, text, position,
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        return frame
    
    @staticmethod
    def draw_trajectory(frame: np.ndarray,
                       trajectory: List[Tuple[int, int]],
                       color: Tuple[int, int, int] = (0, 255, 0),
                       thickness: int = 2) -> np.ndarray:
        """Draw vehicle trajectory"""
        if len(trajectory) < 2:
            return frame
        
        for i in range(len(trajectory) - 1):
            cv2.line(frame, trajectory[i], trajectory[i+1], color, thickness)
        
        return frame


class ExportManager:
    """Handle data export"""
    
    @staticmethod
    def export_measurements(measurements: List[SpeedMeasurement],
                           filepath: str,
                           format_type: str = 'json') -> bool:
        """
        Export measurements to file
        
        Args:
            measurements: List of speed measurements
            filepath: Output file path
            format_type: 'json', 'csv', or 'txt'
        """
        try:
            if format_type == 'json':
                data = [
                    {
                        'vehicle_id': m.vehicle_id,
                        'speed_kmh': m.speed_kmh,
                        'speed_mph': m.speed_mph,
                        'distance_meters': m.distance_meters,
                        'timestamp': m.timestamp.isoformat()
                    }
                    for m in measurements
                ]
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
            
            elif format_type == 'csv':
                import csv
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Vehicle ID', 'Speed (km/h)', 'Speed (mph)', 
                                   'Distance (m)', 'Timestamp'])
                    for m in measurements:
                        writer.writerow([m.vehicle_id, f"{m.speed_kmh:.2f}",
                                       f"{m.speed_mph:.2f}", f"{m.distance_meters:.2f}",
                                       m.timestamp.isoformat()])
            
            elif format_type == 'txt':
                with open(filepath, 'w') as f:
                    f.write("Speed Measurement Report\n")
                    f.write("=" * 50 + "\n\n")
                    for m in measurements:
                        f.write(f"Vehicle {m.vehicle_id}:\n")
                        f.write(f"  Speed: {m.speed_kmh:.2f} km/h ({m.speed_mph:.2f} mph)\n")
                        f.write(f"  Distance: {m.distance_meters:.2f} meters\n")
                        f.write(f"  Time: {m.timestamp.isoformat()}\n\n")
            
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
