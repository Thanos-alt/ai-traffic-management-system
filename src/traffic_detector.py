"""Traffic detection using YOLOv11n"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from config.config import (
    MODEL_NAME, MODEL_PATH, CONFIDENCE_THRESHOLD, IOU_THRESHOLD,
    VEHICLE_CLASSES, MIN_VEHICLES_ALERT, TRAFFIC_DENSITY_THRESHOLD,
    FRAME_WIDTH, FRAME_HEIGHT, DETECTION_LINE_THICKNESS, DETECTION_FONT_SIZE
)
from src.logger import logger

class TrafficDetector:
    """Vehicle detection and traffic analysis using YOLOv11n"""
    
    def __init__(self):
        self.model = None
        self.vehicle_classes = VEHICLE_CLASSES
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.iou_threshold = IOU_THRESHOLD
        self.traffic_history = []
        self.max_history = 30  # Store last 30 frames
        self.load_model()
    
    def load_model(self):
        """Load YOLO model"""
        try:
            logger.info(f"Loading YOLO model: {MODEL_NAME}")
            
            # Check if model file exists locally
            if MODEL_PATH.exists():
                logger.info(f"Loading from local path: {MODEL_PATH}")
                self.model = YOLO(str(MODEL_PATH))
            else:
                # Ultralytics will download if needed
                logger.info(f"Model not found locally, downloading: {MODEL_NAME}")
                self.model = YOLO(f'{MODEL_NAME}.pt')
                
                # Copy to models directory for future use
                import shutil
                if self.model and MODEL_PATH.parent.exists():
                    try:
                        yolo_home = Path.home() / '.ultralytics' / 'models'
                        for f in yolo_home.glob(f'{MODEL_NAME}.pt'):
                            shutil.copy2(f, MODEL_PATH)
                            logger.info(f"Cached model to: {MODEL_PATH}")
                            break
                    except:
                        pass
            
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect_vehicles(self, frame: np.ndarray) -> dict:
        """Detect vehicles in frame using YOLOv11n"""
        if self.model is None:
            logger.warning("Model not loaded")
            return {"detections": [], "count": 0}
        
        try:
            results = self.model(frame, conf=self.confidence_threshold, iou=self.iou_threshold)
            
            detections = []
            vehicle_count = 0
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    
                    # Filter for vehicle classes
                    if class_id in self.vehicle_classes:
                        vehicle_count += 1
                        confidence = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        detections.append({
                            "class_id": class_id,
                            "class_name": self.model.names[class_id],
                            "confidence": confidence,
                            "bbox": (x1, y1, x2, y2),
                            "center": ((x1 + x2) // 2, (y1 + y2) // 2)
                        })
            
            return {
                "detections": detections,
                "count": vehicle_count,
                "frame": frame
            }
        
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return {"detections": [], "count": 0}
    
    def detect_all_objects(self, frame: np.ndarray) -> dict:
        """Detect ALL objects in frame (including persons, vehicles, etc.)"""
        if self.model is None:
            logger.warning("Model not loaded")
            return {"detections": [], "all_detections": {}}
        
        try:
            results = self.model(frame, conf=self.confidence_threshold, iou=self.iou_threshold)
            
            detections = []
            all_detections = {
                "person": [],
                "motorcycle": [],
                "vehicle": []
            }
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    detection_dict = {
                        "class_id": class_id,
                        "class_name": self.model.names[class_id],
                        "confidence": confidence,
                        "bbox": (x1, y1, x2, y2),
                        "center": ((x1 + x2) // 2, (y1 + y2) // 2)
                    }
                    
                    detections.append(detection_dict)
                    
                    # Categorize detections
                    if class_id == 0:  # Person
                        all_detections["person"].append(detection_dict)
                    elif class_id == 3:  # Motorcycle
                        all_detections["motorcycle"].append(detection_dict)
                    elif class_id in [2, 5, 7]:  # Car, Bus, Truck
                        all_detections["vehicle"].append(detection_dict)
            
            return {
                "detections": detections,
                "all_detections": all_detections,
                "person_count": len(all_detections["person"]),
                "motorcycle_count": len(all_detections["motorcycle"]),
                "vehicle_count": len(all_detections["vehicle"])
            }
        
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return {"detections": [], "all_detections": {}, "person_count": 0, "motorcycle_count": 0, "vehicle_count": 0}
    
    def analyze_traffic_density(self, frame_width: int, frame_height: int, 
                                detections: list) -> dict:
        """Analyze traffic density based on vehicle distribution"""
        if not detections:
            return {
                "density": 0.0,
                "level": "LOW",
                "vehicles": 0,
                "congestion_score": 0
            }
        
        vehicle_count = len(detections)
        frame_area = frame_width * frame_height
        
        # Calculate density as percentage of frame
        bbox_areas = [
            (det["bbox"][2] - det["bbox"][0]) * (det["bbox"][3] - det["bbox"][1])
            for det in detections
        ]
        total_vehicle_area = sum(bbox_areas)
        density = min(total_vehicle_area / frame_area, 1.0)
        
        # Determine traffic level
        if density > TRAFFIC_DENSITY_THRESHOLD:
            level = "HIGH"
        elif density > 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        # Congestion score (0-100)
        congestion_score = int(density * 100)
        
        return {
            "density": density,
            "level": level,
            "vehicles": vehicle_count,
            "congestion_score": congestion_score
        }
    
    def draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
        """Draw bounding boxes and labels on frame"""
        # Ensure frame is contiguous and correct dtype
        frame = frame.copy()
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8)
        if not frame.flags['C_CONTIGUOUS']:
            frame = np.ascontiguousarray(frame)
        
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            confidence = det["confidence"]
            class_name = det["class_name"]
            
            # Draw bounding box
            color = (0, 255, 0)  # Green for vehicles
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, DETECTION_LINE_THICKNESS)
            
            # Draw label
            label = f"{class_name} {confidence:.2f}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = DETECTION_FONT_SIZE
            font_thickness = 1
            text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
            
            # Background for text
            cv2.rectangle(frame, (x1, y1 - text_size[1] - 4),
                         (x1 + text_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 2),
                       font, font_scale, (0, 0, 0), font_thickness)
        
        return frame
    
    def update_traffic_history(self, traffic_analysis: dict):
        """Update traffic history for trend analysis"""
        self.traffic_history.append(traffic_analysis)
        if len(self.traffic_history) > self.max_history:
            self.traffic_history.pop(0)
    
    def get_traffic_trend(self) -> str:
        """Get traffic trend (INCREASING, DECREASING, STABLE)"""
        if len(self.traffic_history) < 2:
            return "STABLE"
        
        recent = self.traffic_history[-5:] if len(self.traffic_history) >= 5 else self.traffic_history
        congestion_scores = [t["congestion_score"] for t in recent]
        
        avg_recent = sum(congestion_scores[-3:]) / 3
        avg_earlier = sum(congestion_scores[:max(1, len(congestion_scores)-3)]) / max(1, len(congestion_scores)-3)
        
        if avg_recent > avg_earlier + 5:
            return "INCREASING"
        elif avg_recent < avg_earlier - 5:
            return "DECREASING"
        else:
            return "STABLE"
