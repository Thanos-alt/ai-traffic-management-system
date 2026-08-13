"""Lane-based traffic detection and density analysis"""

import cv2
import numpy as np
from src.logger import logger


class LaneDetector:
    """Detects and analyzes traffic density per lane"""
    
    def __init__(self, num_lanes=2):
        """
        Initialize lane detector
        
        Args:
            num_lanes: Number of lanes to detect (default 2 for left/right)
        """
        self.num_lanes = num_lanes
        self.lane_history = {f"lane_{i}": [] for i in range(num_lanes)}
        self.max_history = 30
        self.lane_width = None
        self.frame_width = None
        
    def divide_frame_into_lanes(self, frame_width, frame_height, detections):
        """
        Divide frame into lanes and assign vehicles to lanes
        
        Args:
            frame_width: Width of frame
            frame_height: Height of frame
            detections: List of detection dictionaries with 'center' key
            
        Returns:
            Dictionary with lane assignments and density
        """
        self.frame_width = frame_width
        self.lane_width = frame_width / self.num_lanes
        
        lane_data = {}
        
        for i in range(self.num_lanes):
            lane_num = f"lane_{i}"
            lane_data[lane_num] = {
                "vehicles": [],
                "x_start": int(i * self.lane_width),
                "x_end": int((i + 1) * self.lane_width),
                "density": 0.0,
                "level": "LOW"
            }
        
        # Assign detections to lanes
        for detection in detections:
            center_x, center_y = detection["center"]
            
            # Find which lane this vehicle belongs to
            lane_idx = min(int(center_x / self.lane_width), self.num_lanes - 1)
            lane_num = f"lane_{lane_idx}"
            
            lane_data[lane_num]["vehicles"].append(detection)
        
        # Calculate density for each lane
        for i in range(self.num_lanes):
            lane_num = f"lane_{i}"
            vehicle_count = len(lane_data[lane_num]["vehicles"])
            lane_area = self.lane_width * frame_height
            
            # Density = vehicles per 1000 pixels
            density = (vehicle_count * 1000) / lane_area if lane_area > 0 else 0
            lane_data[lane_num]["density"] = density
            
            # Determine traffic level
            if vehicle_count == 0:
                lane_data[lane_num]["level"] = "LOW"
            elif vehicle_count <= 2:
                lane_data[lane_num]["level"] = "MODERATE"
            elif vehicle_count <= 5:
                lane_data[lane_num]["level"] = "HIGH"
            else:
                lane_data[lane_num]["level"] = "CRITICAL"
        
        return lane_data
    
    def update_lane_history(self, lane_data):
        """Update history for trend analysis"""
        for lane_num in lane_data:
            self.lane_history[lane_num].append(lane_data[lane_num]["density"])
            
            # Keep only last N frames
            if len(self.lane_history[lane_num]) > self.max_history:
                self.lane_history[lane_num].pop(0)
    
    def get_lane_trend(self, lane_num):
        """Get traffic trend for a lane (INCREASING/STABLE/DECREASING)"""
        if lane_num not in self.lane_history or len(self.lane_history[lane_num]) < 2:
            return "STABLE"
        
        recent = self.lane_history[lane_num][-5:] if len(self.lane_history[lane_num]) >= 5 else self.lane_history[lane_num]
        
        if len(recent) < 2:
            return "STABLE"
        
        avg_increase = sum(recent[i+1] - recent[i] for i in range(len(recent)-1)) / (len(recent) - 1)
        
        if avg_increase > 2:
            return "INCREASING"
        elif avg_increase < -2:
            return "DECREASING"
        else:
            return "STABLE"
    
    def draw_lanes_on_frame(self, frame, lane_data, signal_state=None):
        """
        Draw lane divisions and density info on frame
        
        Args:
            frame: Video frame
            lane_data: Lane information dictionary
            signal_state: Dictionary with signal colors per lane {lane_num: color}
            
        Returns:
            Frame with lane overlays
        """
        if signal_state is None:
            signal_state = {}
        
        for i in range(self.num_lanes):
            lane_num = f"lane_{i}"
            lane_info = lane_data[lane_num]
            
            x_start = lane_info["x_start"]
            x_end = lane_info["x_end"]
            density = lane_info["density"]
            level = lane_info["level"]
            vehicle_count = len(lane_info["vehicles"])
            
            # Get signal color (default based on level)
            if lane_num in signal_state:
                signal_color = signal_state[lane_num]
            else:
                # Default colors: red for high, yellow for moderate, green for low
                if level == "CRITICAL":
                    signal_color = (0, 0, 255)  # Red
                elif level == "HIGH":
                    signal_color = (0, 165, 255)  # Orange
                elif level == "MODERATE":
                    signal_color = (0, 255, 255)  # Yellow
                else:
                    signal_color = (0, 255, 0)  # Green
            
            # Draw lane divider (vertical line)
            if i < self.num_lanes - 1:
                x_divider = x_end
                cv2.line(frame, (x_divider, 0), (x_divider, frame.shape[0]), 
                        (200, 200, 200), 2)
            
            # Draw lane info panel
            panel_height = 80
            overlay = frame.copy()
            cv2.rectangle(overlay, (x_start, 0), (x_end, panel_height),
                         signal_color, -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
            
            # Draw border
            cv2.rectangle(frame, (x_start, 0), (x_end, panel_height),
                         signal_color, 3)
            
            # Draw lane label and signal
            lane_label = f"LANE {i+1}"
            cv2.putText(frame, lane_label, (x_start + 10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, signal_color, 2)
            
            # Draw signal status
            if level == "CRITICAL" or level == "HIGH":
                signal_text = "🔴 RED"
                signal_color_text = (0, 0, 255)
            elif level == "MODERATE":
                signal_text = "🟡 YELLOW"
                signal_color_text = (0, 255, 255)
            else:
                signal_text = "🟢 GREEN"
                signal_color_text = (0, 255, 0)
            
            cv2.putText(frame, signal_text, (x_start + 10, 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, signal_color_text, 2)
            
            # Draw vehicle count
            vehicle_text = f"Vehicles: {vehicle_count}"
            cv2.putText(frame, vehicle_text, (x_start + 10, 105),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def highlight_lane(self, frame, lane_num, color=(0, 255, 0), alpha=0.2):
        """
        Highlight a specific lane (e.g. for emergency vehicle)
        
        Args:
            frame: Video frame
            lane_num: Lane to highlight (e.g. 'lane_0')
            color: BGR color tuple
            alpha: Transparency (0-1)
            
        Returns:
            Frame with highlighted lane
        """
        if lane_num not in self.lane_history:
            return frame
        
        lane_data = {}
        for i in range(self.num_lanes):
            ln = f"lane_{i}"
            if ln == lane_num:
                x_start = int(i * self.lane_width)
                x_end = int((i + 1) * self.lane_width)
                
                overlay = frame.copy()
                cv2.rectangle(overlay, (x_start, 0), (x_end, frame.shape[0]),
                             color, -1)
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        
        return frame
