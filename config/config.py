"""Configuration settings for AI Traffic Management System"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Model settings
MODEL_NAME = "yolo26n"  # Using YOLOv26 nano model
MODEL_PATH = MODELS_DIR / "yolo26n.pt"
CONFIDENCE_THRESHOLD = 0.5
IOU_THRESHOLD = 0.45

# Traffic detection settings
VEHICLE_CLASSES = [2, 3, 5, 7]  # car, motorcycle, bus, truck (actual vehicles on road)
MIN_VEHICLES_ALERT = 10
TRAFFIC_DENSITY_THRESHOLD = 0.7

# Video/Camera settings
CAMERA_SOURCES = {
    "camera_0": 0,  # Webcam
    "camera_1": "rtsp://example.com/stream1",  # Network camera
}
FPS = 30
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Camera image properties (for natural video quality)
CAMERA_BRIGHTNESS = 0          # -64 to 64 (0 = normal, negative = darker, positive = brighter)
CAMERA_CONTRAST = 50           # 0 to 100 (50 = normal)
CAMERA_SATURATION = 64         # 0 to 128 (64 = normal)
CAMERA_GAIN = 0                # 0 to 100 (camera gain, if supported)
CAMERA_EXPOSURE = -5           # -13 to -1 (lower = darker, for better detail in bright conditions)
CAMERA_AUTO_EXPOSURE = True    # Enable auto-exposure adjustment
CAMERA_WHITE_BALANCE = True    # Enable auto white balance
CAMERA_BUFFER_SIZE = 1         # Keep only latest frame (1), reduces latency
CAMERA_ENHANCE_CONTRAST = False # Use CLAHE for contrast enhancement (for very dark video)

# Voice settings
ENABLE_VOICE = True
VOICE_RATE = 150
VOICE_VOLUME = 0.9

# Speed tracking settings
TRACKER_TYPE = "bytetrack"  # Options: "basic" (simple centroid) or "bytetrack" (advanced)
PIXELS_PER_METER = 20       # Calibration: pixels representing 1 meter
SPEED_LIMIT_KMH = 60        # Normal speed limit
SPEEDING_THRESHOLD_KMH = 80 # Alert threshold for speeding
MAX_TRACK_AGE = 30          # Frames to keep track without detection

# Alert settings
HIGH_TRAFFIC_MESSAGE = "High traffic detected on lane"
INCIDENT_MESSAGE = "Traffic incident detected"
NORMAL_TRAFFIC_MESSAGE = "Traffic flow is normal"

# Logging settings
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "traffic_management.log"

# Detection output settings
SHOW_CONFIDENCE = True
SHOW_CLASS_LABELS = True
DETECTION_LINE_THICKNESS = 2
DETECTION_FONT_SIZE = 0.6

# FPS counter settings
FPS_UPDATE_INTERVAL = 10

# HSR (Human Shoulder Responsibility) Settings
HSR_STATUS_CHECK_INTERVAL = 5  # seconds
HSR_CLOSING_THRESHOLD = 10  # consecutive frames

# Processing settings
MAX_DETECTIONS_PER_FRAME = 100
FRAME_SKIP_RATE = 1  # Process every Nth frame (1 = all frames)

# ===== SPEED TRACKING SETTINGS =====
# Speed measurement and monitoring
ENABLE_SPEED_TRACKING = True
SPEED_LIMIT_KMH = 60  # Speed limit in km/h
SPEEDING_THRESHOLD_KMH = 80  # Speed above which alarm triggers and police called
SPEED_WARNING_THRESHOLD_KMH = 70  # Speed for warning (without police call)
PIXELS_PER_METER = 20  # Calibration factor for speed calculation (adjust based on your camera)
                        # Higher value = faster speeds measured
SPEED_SMOOTHING_FRAMES = 3  # Average speed over N frames for stability

# ===== INCIDENT DETECTION SETTINGS =====
ENABLE_INCIDENT_DETECTION = True
ENABLE_FIRE_DETECTION = True

# Collision detection
COLLISION_IOU_THRESHOLD = 0.3  # Intersection over Union threshold for collision
COLLISION_DISTANCE_THRESHOLD = 50  # pixels - max distance between frames

# Accident detection
ACCIDENT_SPEED_DROP_THRESHOLD = 10  # km/h - sudden deceleration threshold
ACCIDENT_STANDSTILL_FRAMES = 30  # frames - vehicle standstill detection

# ===== EMERGENCY SERVICE SETTINGS =====
ENABLE_EMERGENCY_CALLS = False  # Set to True to enable actual emergency calls
ENABLE_ALARM_SOUND = True  # Enable alarm beeping

# Emergency thresholds
TRIGGER_POLICE_ON_SPEEDING = True  # Call police on high-speed violations
TRIGGER_AMBULANCE_ON_COLLISION = True  # Call ambulance on collision detection
TRIGGER_FIRE_BRIGADE_ON_FIRE = True  # Call fire brigade on fire detection

# Emergency call cooldown (prevent spamming)
EMERGENCY_CALL_COOLDOWN_SECONDS = 30  # Cooldown period between same type alerts

# Emergency service phone numbers
POLICE_PHONE = "100"      # India: 100
AMBULANCE_PHONE = "102"   # India: 102
FIRE_BRIGADE_PHONE = "101"  # India: 101
UNIFIED_EMERGENCY = "112"  # Unified emergency number

# ===== SPEED DISPLAY SETTINGS =====
SHOW_SPEED_ON_VEHICLES = True  # Display current speed on detected vehicles
SPEED_DISPLAY_COLOR = (0, 255, 255)  # BGR: Cyan for normal speed
SPEEDING_DISPLAY_COLOR = (0, 0, 255)  # BGR: Red for speeding vehicles
SPEED_LIMIT_DISPLAY = True  # Show speed limit on display
