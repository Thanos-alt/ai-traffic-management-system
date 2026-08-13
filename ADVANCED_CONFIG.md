"""Advanced configuration examples"""

# Example 1: Multi-Camera Setup
# In config/config.py, update CAMERA_SOURCES:
CAMERA_SOURCES = {
    "main_road": 0,  # Webcam on main road
    "side_road": "rtsp://192.168.1.100:554/stream",  # IP camera
    "highway": "rtsp://192.168.1.101:554/stream",  # Another IP camera
}

# Example 2: Custom Detection Pipeline
from src.traffic_detector import TrafficDetector
from ultralytics import YOLO

def custom_detection():
    """Custom detection with modified classes"""
    detector = TrafficDetector()
    # Modify vehicle classes
    detector.vehicle_classes = [2, 3, 5, 7, 9]  # Add more classes
    
# Example 3: Real-time Dashboard
from src.dashboard import TrafficDashboard

def create_dashboard():
    """Create custom dashboard"""
    dashboard = TrafficDashboard()
    # Customize colors
    dashboard.text_color = (255, 0, 0)  # Blue
    dashboard.bg_color = (255, 255, 0)  # Cyan
    
# Example 4: Voice Alert Customization
from src.voice_alert import VoiceAlertSystem

def custom_voice_alerts():
    """Setup custom voice alerts"""
    voice = VoiceAlertSystem()
    voice.alert_high_traffic("Highway Exit 42")
    voice.alert_incident("Accident reported")
    
# Example 5: HSR Monitoring Custom Logic
from src.hsr_monitor import HSRMonitor

def monitor_hsr():
    """Custom HSR monitoring"""
    hsr = HSRMonitor()
    hsr.update_status(detected_incident=True)
    status = hsr.get_status()
    print(f"Current HSR Status: {status['status']}")
    
# Example 6: Multi-threaded Processing
import threading
from src.camera_handler import CameraHandler

def process_multiple_cameras():
    """Process multiple camera feeds"""
    cameras = {
        "cam1": CameraHandler(0),
        "cam2": CameraHandler("rtsp://192.168.1.100:554/stream")
    }
    
    for name, camera in cameras.items():
        camera.start_capture_thread()
        
# Example 7: Custom Frame Processing
import cv2

def apply_custom_filters(frame):
    """Apply custom image processing"""
    # Histogram equalization
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    equalized = cv2.equalizeHist(gray)
    
    # Gaussian blur for noise reduction
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    
    return blurred
    
# Example 8: Performance Optimization
def optimize_performance():
    """Tips for optimizing performance"""
    # 1. Lower resolution
    FRAME_WIDTH = 480
    FRAME_HEIGHT = 360
    
    # 2. Skip frames
    FRAME_SKIP_RATE = 2  # Process every 2nd frame
    
    # 3. Reduce model precision
    CONFIDENCE_THRESHOLD = 0.6  # Higher = faster but less sensitive
    
    # 4. Enable GPU
    # Requires CUDA-capable GPU and proper setup
