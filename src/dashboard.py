"""Real-time dashboard for traffic monitoring"""

import cv2
import numpy as np
from datetime import datetime
from config.config import FRAME_HEIGHT, FRAME_WIDTH

class TrafficDashboard:
    """Displays real-time traffic information on video frames"""
    
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_size = 0.6
        self.font_thickness = 1
        self.text_color = (255, 255, 255)  # White
        self.bg_color = (25, 25, 112)  # Midnight blue
    
    def _ensure_contiguous(self, frame: np.ndarray) -> np.ndarray:
        """Ensure frame is contiguous in memory and correct dtype"""
        if frame is None:
            return None
        # Ensure uint8 dtype and contiguous memory layout
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        if not frame.flags['C_CONTIGUOUS']:
            frame = np.ascontiguousarray(frame)
        return frame
    
    def add_header(self, frame: np.ndarray, title: str) -> np.ndarray:
        """Add header with title"""
        frame = self._ensure_contiguous(frame)
        
        # Add header border at the top
        header_height = 50
        result = cv2.copyMakeBorder(frame, header_height, 0, 0, 0, 
                                    cv2.BORDER_CONSTANT, value=self.bg_color)
        result = self._ensure_contiguous(result)
        
        # Put title text
        text_size = cv2.getTextSize(title, self.font, 0.8, 2)[0]
        text_x = (result.shape[1] - text_size[0]) // 2
        text_y = header_height - 15
        
        cv2.putText(result, title, (text_x, text_y),
                   self.font, 0.8, self.text_color, 2)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(result, timestamp, (10, text_y),
                   self.font, 0.5, self.text_color, 1)
        
        return result
    
    def add_traffic_stats(self, frame: np.ndarray, stats: dict) -> np.ndarray:
        """Add traffic statistics overlay with speed information"""
        frame = self._ensure_contiguous(frame)
        overlay = frame.copy()
        overlay = self._ensure_contiguous(overlay)
        
        # Determine panel height based on speed stats
        speed_stats = stats.get('speed_stats', {})
        has_speed = len(speed_stats) > 0
        panel_height = 180 if has_speed else 150
        
        cv2.rectangle(overlay, (10, frame.shape[0] - panel_height - 10),
                     (380 if has_speed else 300, frame.shape[0] - 10), self.bg_color, -1)
        
        # Apply transparency
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        frame = self._ensure_contiguous(frame)
        
        y_offset = frame.shape[0] - panel_height
        
        # Vehicle count
        vehicles_text = f"Vehicles: {stats.get('vehicles', 0)}"
        cv2.putText(frame, vehicles_text, (20, y_offset + 30),
                   self.font, self.font_size, self.text_color, self.font_thickness)
        
        # Traffic density
        density_text = f"Density: {stats.get('density', 0):.1%}"
        cv2.putText(frame, density_text, (20, y_offset + 60),
                   self.font, self.font_size, self.text_color, self.font_thickness)
        
        # Traffic level
        level = stats.get('level', 'LOW')
        level_color = (0, 255, 0)  # Green
        if level == 'HIGH':
            level_color = (0, 0, 255)  # Red
        elif level == 'MEDIUM':
            level_color = (0, 165, 255)  # Orange
        
        level_text = f"Level: {level}"
        cv2.putText(frame, level_text, (20, y_offset + 90),
                   self.font, self.font_size, level_color, self.font_thickness)
        
        # Trend
        trend_text = f"Trend: {stats.get('trend', 'STABLE')}"
        cv2.putText(frame, trend_text, (20, y_offset + 120),
                   self.font, self.font_size, self.text_color, self.font_thickness)
        
        # Speed statistics (if available)
        if has_speed:
            avg_speed = speed_stats.get('avg_speed', 0)
            max_speed = speed_stats.get('max_speed', 0)
            speeding_count = speed_stats.get('speeding_count', 0)
            
            # Average speed
            speed_color = (0, 255, 0) if avg_speed < 60 else (0, 165, 255) if avg_speed < 80 else (0, 0, 255)
            avg_speed_text = f"Avg Speed: {avg_speed:.1f} km/h"
            cv2.putText(frame, avg_speed_text, (200, y_offset + 30),
                       self.font, self.font_size, speed_color, self.font_thickness)
            
            # Max speed
            max_speed_color = (0, 0, 255) if max_speed > 80 else (0, 165, 255) if max_speed > 60 else (0, 255, 0)
            max_speed_text = f"Max Speed: {max_speed:.1f} km/h"
            cv2.putText(frame, max_speed_text, (200, y_offset + 60),
                       self.font, self.font_size, max_speed_color, self.font_thickness)
            
            # Speeding vehicles
            speeding_color = (0, 0, 255) if speeding_count > 0 else (0, 255, 0)
            speeding_text = f"Speeding: {speeding_count}"
            cv2.putText(frame, speeding_text, (200, y_offset + 90),
                       self.font, self.font_size, speeding_color, self.font_thickness)
        
        return self._ensure_contiguous(frame)
    
    def add_hsr_status(self, frame: np.ndarray, hsr_status: dict) -> np.ndarray:
        """Add HSR status indicator"""
        frame = self._ensure_contiguous(frame)
        status = hsr_status.get('status', 'OPEN')
        
        # HSR indicator (top-right)
        status_color = (0, 255, 0)  # Green for OPEN
        if status == 'CLOSED':
            status_color = (0, 0, 255)  # Red
        elif status == 'CLOSING':
            status_color = (0, 165, 255)  # Orange
        
        # Draw circle indicator
        cv2.circle(frame, (frame.shape[1] - 30, 30), 15, status_color, -1)
        
        # Draw text
        hsr_text = f"HSR: {status}"
        cv2.putText(frame, hsr_text, (frame.shape[1] - 130, 35),
                   self.font, self.font_size, self.text_color, self.font_thickness)
        
        return self._ensure_contiguous(frame)
    
    def add_fps_counter(self, frame: np.ndarray, fps: float) -> np.ndarray:
        """Add FPS counter"""
        frame = self._ensure_contiguous(frame)
        fps_text = f"FPS: {fps:.1f}"
        cv2.putText(frame, fps_text, (frame.shape[1] - 150, 30),
                   self.font, self.font_size, (0, 255, 0), self.font_thickness)
        return self._ensure_contiguous(frame)
    
    def add_message(self, frame: np.ndarray, message: str, 
                   position: str = "bottom", 
                   color: tuple = (0, 255, 0)) -> np.ndarray:
        """Add message banner"""
        frame = self._ensure_contiguous(frame)
        message_height = 40
        
        if position == "bottom":
            y_pos = frame.shape[0] - message_height
        else:  # top
            y_pos = 0
        
        # Background
        cv2.rectangle(frame, (0, y_pos), (frame.shape[1], y_pos + message_height),
                     (0, 0, 0), -1)
        
        # Message text
        text_size = cv2.getTextSize(message, self.font, self.font_size, 1)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = y_pos + (message_height + text_size[1]) // 2
        
        cv2.putText(frame, message, (text_x, text_y),
                   self.font, self.font_size, color, self.font_thickness)
        
        return self._ensure_contiguous(frame)
    
    def draw_attention_box(self, frame: np.ndarray, x1: int, y1: int, 
                          x2: int, y2: int, thickness: int = 3) -> np.ndarray:
        """Draw attention-grabbing box"""
        frame = self._ensure_contiguous(frame)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness)
        return frame
