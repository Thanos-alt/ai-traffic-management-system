"""
AI Traffic Management System
Real-time traffic monitoring using YOLOv26n detection
with voice alerts and HSR monitoring
"""

import cv2
import time
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.config import (
    MODEL_PATH, MODEL_NAME, HIGH_TRAFFIC_MESSAGE, INCIDENT_MESSAGE, 
    NORMAL_TRAFFIC_MESSAGE, FPS_UPDATE_INTERVAL,
    FRAME_WIDTH, FRAME_HEIGHT, FPS
)
from src.logger import logger
from src.camera_handler import CameraHandler
from src.traffic_detector import TrafficDetector
from src.voice_alert import VoiceAlertSystem
from src.dashboard import TrafficDashboard
from src.hsr_monitor import HSRMonitor
from src.alert import AlertManager
from src.lane_detector import LaneDetector
from src.traffic_signal_manager import TrafficSignalManager
from src.emergency_vehicle_detector import EmergencyVehicleDetector
from src.gps_tracker import GPSTracker

class TrafficManagementApp:
    """Main AI Traffic Management Application"""
    
    def __init__(self, camera_source=0):
        logger.info("=" * 70)
        logger.info("Initializing AI Traffic Management System")
        logger.info(f"Model: {MODEL_NAME} | Resolution: {FRAME_WIDTH}x{FRAME_HEIGHT}")
        logger.info("=" * 70)
        
        self.camera_source = camera_source
        self.camera = None
        self.detector = None
        self.voice_alert = None
        self.dashboard = None
        self.hsr_monitor = None
        self.alert_manager = None
        self.lane_detector = None
        self.signal_manager = None
        self.emergency_detector = None
        self.gps_tracker = None
        
        self.running = False
        self.paused = False
        self.frame_count = 0
        self.fps = 0
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        
        self.last_alert_time = {}
        self.alert_cooldown = 3  # seconds between similar alerts
        self.emergency_vehicle = None
        
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all application components"""
        try:
            logger.info("Initializing camera...")
            self.camera = CameraHandler(self.camera_source)
            
            logger.info("Loading traffic detector (YOLOv26n)...")
            self.detector = TrafficDetector()
            
            logger.info("Initializing voice alert system...")
            self.voice_alert = VoiceAlertSystem()
            
            logger.info("Initializing dashboard...")
            self.dashboard = TrafficDashboard()
            
            logger.info("Initializing HSR monitor...")
            self.hsr_monitor = HSRMonitor()
            
            logger.info("Initializing alert manager...")
            self.alert_manager = AlertManager()
            
            logger.info("Initializing lane detector...")
            self.lane_detector = LaneDetector(num_lanes=2)
            
            logger.info("Initializing traffic signal manager...")
            self.signal_manager = TrafficSignalManager(num_lanes=2)
            
            logger.info("Initializing emergency vehicle detector...")
            self.emergency_detector = EmergencyVehicleDetector()
            
            logger.info("Initializing GPS tracker...")
            self.gps_tracker = GPSTracker(
                default_lat=40.7128,
                default_lon=-74.0060,
                location_name="Traffic Management Center"
            )
            
            logger.info("✓ All components initialized successfully!")
            logger.info("=" * 70)
        
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    def should_alert(self, alert_type: str) -> bool:
        """Check if enough cooldown time has passed for alert"""
        current_time = time.time()
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = current_time
            return True
        
        if current_time - self.last_alert_time[alert_type] >= self.alert_cooldown:
            self.last_alert_time[alert_type] = current_time
            return True
        
        return False
    
    def draw_detection_panel(self, frame, person_count, motorcycle_count, vehicle_count):
        """Draw detection counts panel with Person, Motorcycle, Vehicle sections"""
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
    
    def draw_organized_ui_panels(self, frame, person_count, motorcycle_count, vehicle_count, 
                                   lane_data, hsr_status, fps, emergency_info=None):
        """
        Draw all UI panels in organized positions without overlapping
        
        Layout:
        - Top: Header (full width)
        - Top-left: Detection Analysis panel
        - Top-right: Lane Status panel
        - Bottom-left: HSR Monitor
        - Bottom-center: Traffic Statistics
        - Bottom-right: FPS Counter
        - Emergency banner when active
        
        Args:
            frame: Video frame
            person_count, motorcycle_count, vehicle_count: Detection counts
            lane_data: Lane information dictionary
            hsr_status: HSR monitor status
            fps: Current FPS
            emergency_info: Emergency vehicle information
            
        Returns:
            Frame with all organized panels
        """
        frame_h, frame_w = frame.shape[:2]
        
        # ========== HEADER (TOP - FULL WIDTH) ==========
        header_height = 50
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame_w, header_height), (40, 40, 40), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        cv2.rectangle(frame, (0, 0), (frame_w, header_height), (0, 255, 255), 2)
        
        if emergency_info and emergency_info.get("active"):
            header_text = "🚨 AI TRAFFIC MGMT - EMERGENCY MODE ACTIVE"
            text_color = (255, 0, 255)
        else:
            header_text = "AI TRAFFIC MANAGEMENT - YOLOv26n - LANE-BASED"
            text_color = (0, 255, 255)
        
        cv2.putText(frame, header_text, (15, 32),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
        
        # ========== TOP-LEFT: DETECTION ANALYSIS PANEL ==========
        panel_width = 320
        panel_height = 200
        panel_x, panel_y = 10, header_height + 10
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), 
                      (panel_x + panel_width, panel_y + panel_height),
                      (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (panel_x, panel_y),
                      (panel_x + panel_width, panel_y + panel_height),
                      (0, 255, 255), 2)
        
        cv2.putText(frame, "DETECTION ANALYSIS", (panel_x + 15, panel_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        cv2.line(frame, (panel_x + 10, panel_y + 38), 
                 (panel_x + panel_width - 10, panel_y + 38), (100, 100, 100), 1)
        
        # Person
        cv2.putText(frame, "PERSON", (panel_x + 15, panel_y + 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, f"{person_count}", (panel_x + 250, panel_y + 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.line(frame, (panel_x + 10, panel_y + 75), 
                 (panel_x + panel_width - 10, panel_y + 75), (100, 100, 100), 1)
        
        # Motorcycle
        cv2.putText(frame, "MOTORCYCLE", (panel_x + 15, panel_y + 102),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"{motorcycle_count}", (panel_x + 250, panel_y + 102),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.line(frame, (panel_x + 10, panel_y + 112), 
                 (panel_x + panel_width - 10, panel_y + 112), (100, 100, 100), 1)
        
        # Vehicles
        cv2.putText(frame, "VEHICLES", (panel_x + 15, panel_y + 139),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv2.putText(frame, f"{vehicle_count}", (panel_x + 250, panel_y + 139),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        cv2.line(frame, (panel_x + 10, panel_y + 149), 
                 (panel_x + panel_width - 10, panel_y + 149), (100, 100, 100), 1)
        
        # Total
        total = person_count + motorcycle_count + vehicle_count
        cv2.putText(frame, "TOTAL", (panel_x + 15, panel_y + 176),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"{total}", (panel_x + 250, panel_y + 176),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # ========== TOP-RIGHT: LANE STATUS PANEL ==========
        right_panel_x = frame_w - panel_width - 10
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (right_panel_x, panel_y),
                      (right_panel_x + panel_width, panel_y + panel_height),
                      (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (right_panel_x, panel_y),
                      (right_panel_x + panel_width, panel_y + panel_height),
                      (255, 255, 0), 2)
        
        cv2.putText(frame, "LANE STATUS", (right_panel_x + 15, panel_y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2)
        cv2.line(frame, (right_panel_x + 10, panel_y + 38),
                 (right_panel_x + panel_width - 10, panel_y + 38), (100, 100, 100), 1)
        
        # Lane status for each lane
        y_offset = panel_y + 55
        for i in range(min(2, self.lane_detector.num_lanes)):
            lane_num = f"lane_{i}"
            info = lane_data[lane_num]
            level = info["level"]
            vehicle_in_lane = len(info["vehicles"])
            
            # Color based on level
            if level == "CRITICAL":
                color = (0, 0, 255)
                level_text = "🔴 RED"
            elif level == "HIGH":
                color = (0, 165, 255)
                level_text = "🟠 ORANGE"
            elif level == "MODERATE":
                color = (0, 255, 255)
                level_text = "🟡 YELLOW"
            else:
                color = (0, 255, 0)
                level_text = "🟢 GREEN"
            
            cv2.putText(frame, f"Lane {i+1}", (right_panel_x + 15, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, level_text, (right_panel_x + 130, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
            cv2.putText(frame, f"({vehicle_in_lane}v)", (right_panel_x + 230, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            
            y_offset += 40
        
        # ========== MID-RIGHT: GPS LOCATION PANEL ==========
        gps_panel_height = 100
        gps_panel_y = panel_y + panel_height + 10
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (right_panel_x, gps_panel_y),
                      (right_panel_x + panel_width, gps_panel_y + gps_panel_height),
                      (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (right_panel_x, gps_panel_y),
                      (right_panel_x + panel_width, gps_panel_y + gps_panel_height),
                      (0, 255, 255), 2)
        
        cv2.putText(frame, "GPS LOCATION", (right_panel_x + 15, gps_panel_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
        cv2.line(frame, (right_panel_x + 10, gps_panel_y + 32),
                 (right_panel_x + panel_width - 10, gps_panel_y + 32), (100, 100, 100), 1)
        
        # Location name
        location_name = self.gps_tracker.location_name[:20]
        cv2.putText(frame, location_name, (right_panel_x + 15, gps_panel_y + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 200, 255), 1)
        
        # Coordinates
        coord_text = f"{self.gps_tracker.latitude:.4f}°N"
        cv2.putText(frame, coord_text, (right_panel_x + 15, gps_panel_y + 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
        
        coord_text = f"{self.gps_tracker.longitude:.4f}°E"
        cv2.putText(frame, coord_text, (right_panel_x + 15, gps_panel_y + 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 255), 1)
        
        # Show hotspots count
        hotspots = self.gps_tracker.get_traffic_hotspots()
        cv2.putText(frame, f"Hotspots: {len(hotspots)}", (right_panel_x + 180, gps_panel_y + 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        # ========== BOTTOM-LEFT: HSR MONITOR ==========
        bottom_panel_h = 80
        bottom_y = frame_h - bottom_panel_h - 10
        hsr_panel_w = 200
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, bottom_y), (10 + hsr_panel_w, bottom_y + bottom_panel_h),
                      (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (10, bottom_y), (10 + hsr_panel_w, bottom_y + bottom_panel_h),
                      (0, 255, 0), 2)
        
        cv2.putText(frame, "HSR STATUS", (20, bottom_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)
        # Convert hsr_status to string
        hsr_text = str(hsr_status) if hsr_status else "UNKNOWN"
        cv2.putText(frame, hsr_text, (20, bottom_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, "(Shoulder Resp.)", (20, bottom_y + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (150, 150, 150), 1)
        
        # ========== BOTTOM-CENTER: TRAFFIC STATISTICS ==========
        stats_panel_w = 280
        stats_x = (frame_w - stats_panel_w) // 2
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (stats_x, bottom_y), (stats_x + stats_panel_w, bottom_y + bottom_panel_h),
                      (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (stats_x, bottom_y), (stats_x + stats_panel_w, bottom_y + bottom_panel_h),
                      (100, 100, 255), 2)
        
        density_percent = min(100, int(len(lane_data.get("lane_0", {}).get("vehicles", [])) * 20))
        overall_level = "LOW"
        for i in range(self.lane_detector.num_lanes):
            if lane_data[f"lane_{i}"]["level"] == "CRITICAL":
                overall_level = "CRITICAL"
                break
            elif lane_data[f"lane_{i}"]["level"] == "HIGH" and overall_level != "CRITICAL":
                overall_level = "HIGH"
        
        cv2.putText(frame, "TRAFFIC DENSITY", (stats_x + 25, bottom_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 255), 2)
        cv2.putText(frame, f"Level: {overall_level}", (stats_x + 25, bottom_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 255), 1)
        cv2.putText(frame, f"Density: {density_percent}%", (stats_x + 25, bottom_y + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 255), 1)
        
        # ========== BOTTOM-RIGHT: FPS COUNTER ==========
        fps_panel_w = 150
        fps_x = frame_w - fps_panel_w - 10
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (fps_x, bottom_y), (fps_x + fps_panel_w, bottom_y + bottom_panel_h),
                      (50, 50, 50), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(frame, (fps_x, bottom_y), (fps_x + fps_panel_w, bottom_y + bottom_panel_h),
                      (0, 255, 255), 2)
        
        cv2.putText(frame, "PERFORMANCE", (fps_x + 10, bottom_y + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(frame, f"FPS: {fps:.1f}", (fps_x + 10, bottom_y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame, "frames/sec", (fps_x + 10, bottom_y + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (150, 150, 150), 1)
        
        return frame
    
    def process_frame(self, frame):
        """Process single frame for traffic analysis with lane management and emergency detection"""
        try:
            # Detect ALL objects (persons, motorcycles, vehicles)
            detection_result = self.detector.detect_all_objects(frame)
            all_detections = detection_result["all_detections"]
            person_count = detection_result["person_count"]
            motorcycle_count = detection_result["motorcycle_count"]
            vehicle_count = detection_result["vehicle_count"]
            
            # Combine for vehicle-only analysis (traffic is only vehicles)
            vehicle_detections = all_detections["vehicle"]
            
            # ========== LANE-BASED TRAFFIC ANALYSIS ==========
            # Divide frame into lanes and calculate density per lane
            lane_data = self.lane_detector.divide_frame_into_lanes(
                frame.shape[1], frame.shape[0], vehicle_detections
            )
            
            # Update lane history
            self.lane_detector.update_lane_history(lane_data)
            
            # ========== EMERGENCY VEHICLE DETECTION ==========
            emergency_vehicle = self.emergency_detector.detect_emergency_vehicles(
                detection_result["detections"], frame
            )
            
            if emergency_vehicle:
                # Find which lane the emergency vehicle is in
                center_x, center_y = emergency_vehicle["center"]
                lane_width = self.lane_detector.lane_width
                if lane_width is None:
                    lane_width = frame.shape[1] / 2
                
                emergency_lane_idx = min(int(center_x / lane_width), self.lane_detector.num_lanes - 1)
                emergency_lane = f"lane_{emergency_lane_idx}"
                self.emergency_vehicle = emergency_vehicle
                
                # Activate emergency mode
                self.signal_manager.activate_emergency_mode(emergency_lane)
                
                # Voice alert
                emoji = self.emergency_detector.get_emergency_type_emoji(emergency_vehicle["type"])
                self.voice_alert.speak(f"Emergency alert! {emergency_vehicle['type']} detected in lane {emergency_lane_idx + 1}")
                logger.warning(f"{emoji} Emergency vehicle detected: {emergency_vehicle['type']}")
            else:
                # Clear emergency if signal expired or no more emergency detected
                if self.emergency_vehicle:
                    self.emergency_detector.clear_detection()
                    self.emergency_vehicle = None
                    self.signal_manager.deactivate_emergency_mode()
                
                # Update signals based on traffic density (adaptive)
                self.signal_manager.update_signals_adaptive(lane_data)
            
            # Get current signal states for all lanes
            all_signals = self.signal_manager.get_all_signals()
            signal_state = {ln: info["color"] for ln, info in all_signals.items()}
            
            # Overall traffic analysis (based on vehicles only)
            traffic_analysis = self.detector.analyze_traffic_density(
                frame.shape[1], frame.shape[0], vehicle_detections
            )
            
            # Update traffic history
            self.detector.update_traffic_history(traffic_analysis)
            traffic_trend = self.detector.get_traffic_trend()
            
            # Update HSR status
            is_incident = traffic_analysis["level"] == "HIGH"
            self.hsr_monitor.update_status(is_incident)
            hsr_status = self.hsr_monitor.get_status()
            
            # Mark high traffic zones in GPS
            if traffic_analysis["level"] == "HIGH" or traffic_analysis["level"] == "CRITICAL":
                self.gps_tracker.mark_high_traffic_zone(traffic_analysis["level"])
            
            # Generate alerts
            if traffic_analysis["level"] == "HIGH":
                if self.should_alert("high_traffic"):
                    alert = self.alert_manager.high_traffic_alert(
                        "Main Lane",
                        vehicle_count,
                        traffic_analysis["density"]
                    )
                    self.voice_alert.alert_high_traffic("main lane")
                    logger.warning(f"HIGH TRAFFIC: {vehicle_count} vehicles | {person_count} persons | {motorcycle_count} motorcycles")
            
            elif traffic_analysis["level"] == "LOW":
                if self.should_alert("normal_traffic"):
                    self.alert_manager.normal_traffic_alert("Main Lane")
                    logger.info(f"Traffic normalized: {vehicle_count} vehicles | {person_count} persons | {motorcycle_count} motorcycles")
            
            # Draw all detections on frame
            frame_with_boxes = frame.copy()
            
            # Draw persons (Yellow)
            for detection in all_detections["person"]:
                x1, y1, x2, y2 = detection["bbox"]
                confidence = detection["confidence"]
                cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (0, 255, 255), 2)
                cv2.putText(frame_with_boxes, f"Person {confidence:.2f}", (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            # Draw motorcycles (Cyan)
            for detection in all_detections["motorcycle"]:
                x1, y1, x2, y2 = detection["bbox"]
                confidence = detection["confidence"]
                cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (255, 255, 0), 2)
                cv2.putText(frame_with_boxes, f"Motorcycle {confidence:.2f}", (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
            # Draw vehicles (Blue)
            for detection in all_detections["vehicle"]:
                x1, y1, x2, y2 = detection["bbox"]
                confidence = detection["confidence"]
                class_name = detection["class_name"]
                cv2.rectangle(frame_with_boxes, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame_with_boxes, f"{class_name} {confidence:.2f}", (x1, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Draw lane divisions with traffic signals
            frame_with_lanes = self.lane_detector.draw_lanes_on_frame(
                frame_with_boxes, lane_data, signal_state
            )
            
            # If emergency vehicle, highlight its lane
            if self.emergency_vehicle and emergency_lane:
                frame_with_lanes = self.lane_detector.highlight_lane(
                    frame_with_lanes, emergency_lane, 
                    color=(255, 0, 255), alpha=0.15  # Magenta highlight
                )
            
            # Get emergency info if active
            emergency_info = None
            if self.emergency_vehicle:
                emergency_info = self.signal_manager.get_emergency_info()
            
            # Draw all organized UI panels (no overlapping)
            final_frame = self.draw_organized_ui_panels(
                frame_with_lanes,
                person_count, motorcycle_count, vehicle_count,
                lane_data, hsr_status, self.fps,
                emergency_info=emergency_info
            )
            
            self.frame_count += 1
            return final_frame
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
            import traceback
            traceback.print_exc()
            return frame
    
    def update_fps(self):
        """Update FPS counter"""
        self.fps_frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.fps = self.fps_frame_count / elapsed
            self.fps_frame_count = 0
            self.fps_start_time = current_time
    
    def display_controls_help(self):
        """Display keyboard controls"""
        print("\n" + "=" * 70)
        print("KEYBOARD CONTROLS:")
        print("  [Q]     - Quit application")
        print("  [P]     - Pause/Resume")
        print("  [S]     - Save screenshot")
        print("  [H]     - Show HSR status")
        print("  [A]     - Show active alerts")
        print("  [SPACE] - Pause for inspection")
        print("=" * 70 + "\n")
    
    def run(self):
        """Main application loop"""
        logger.info("Starting main loop...")
        self.display_controls_help()
        self.running = True
        
        try:
            while self.running:
                # Get frame
                frame = self.camera.get_frame()
                if frame is None:
                    logger.warning("Failed to get frame")
                    time.sleep(0.1)
                    continue
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Update FPS
                self.update_fps()
                
                # Display
                cv2.imshow("AI Traffic Management System - YOLOv26n", processed_frame)
                
                # Handle keyboard
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == 27:
                    logger.info("Quit command received")
                    break
                
                elif key == ord('p'):
                    self.paused = not self.paused
                    status = "PAUSED" if self.paused else "RUNNING"
                    logger.info(f"Application {status}")
                    if self.paused:
                        cv2.waitKey(0)
                
                elif key == ord('s'):
                    filename = f"traffic_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(filename, processed_frame)
                    logger.info(f"Screenshot saved: {filename}")
                
                elif key == ord('h'):
                    hsr_status = self.hsr_monitor.get_status()
                    logger.info(f"HSR Status: {hsr_status}")
                
                elif key == ord('a'):
                    active_alerts = self.alert_manager.get_active_alerts()
                    logger.info(f"Active Alerts: {len(active_alerts)}")
                    for alert in active_alerts:
                        logger.info(f"  [{alert['severity']}] {alert['message']}")
                
                # Log periodically
                if self.frame_count % max(1, int(self.fps * FPS_UPDATE_INTERVAL)) == 0:
                    logger.info(f"Processed {self.frame_count} frames | FPS: {self.fps:.1f}")
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.camera:
            self.camera.stop_capture()
        
        if self.voice_alert:
            self.voice_alert.shutdown()
        
        # Save GPS data and traffic hotspots
        if self.gps_tracker:
            self.gps_tracker.save_location_data()
        
        cv2.destroyAllWindows()
        
        # Print statistics
        alerts_stats = self.alert_manager.get_alert_stats()
        logger.info("=" * 70)
        logger.info("APPLICATION STATISTICS")
        logger.info(f"  Total frames processed: {self.frame_count}")
        logger.info(f"  Average FPS: {self.fps:.1f}")
        logger.info(f"  Total alerts: {alerts_stats['total_alerts']}")
        logger.info(f"  Active alerts: {alerts_stats['active_alerts']}")
        logger.info("=" * 70)
        
        # Print GPS and traffic hotspot statistics
        if self.gps_tracker:
            logger.info("=" * 70)
            logger.info("GPS & TRAFFIC HOTSPOTS")
            logger.info(f"  Current Location: {self.gps_tracker.get_location_string()}")
            logger.info(f"  Map URL: {self.gps_tracker.get_map_url()}")
            
            hotspots = self.gps_tracker.get_traffic_hotspots()
            logger.info(f"  High-Traffic Zones Detected: {len(hotspots)}")
            
            for idx, hotspot in enumerate(hotspots[:5], 1):
                logger.info(f"    {idx}. {hotspot['name']} ({hotspot['lat']:.4f}°N, {hotspot['lon']:.4f}°E) - {hotspot['count']} detections")
            
            logger.info("=" * 70)

def main():
    """Entry point"""
    try:
        # Check if model exists
        model_path = Path(MODEL_PATH)
        if not model_path.exists():
            logger.warning(f"Model not found at {model_path}")
            logger.info("Model will be auto-downloaded on startup...")
        
        # Create and run application
        app = TrafficManagementApp(camera_source=0)
        app.run()
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
