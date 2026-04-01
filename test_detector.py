"""Demo script - Quick test of the traffic detection system"""

import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.traffic_detector import TrafficDetector
from src.voice_alert import VoiceAlertSystem
from src.dashboard import TrafficDashboard
from src.logger import logger

def test_detector():
    """Test traffic detector with webcam"""
    logger.info("Starting detector test...")
    
    try:
        # Initialize detector
        detector = TrafficDetector()
        voice = VoiceAlertSystem()
        dashboard = TrafficDashboard()
        
        # Open webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("Cannot open webcam")
            return
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Detect vehicles
            result = detector.detect_vehicles(frame)
            detections = result["detections"]
            vehicle_count = result["count"]
            
            # Analyze
            analysis = detector.analyze_traffic_density(
                frame.shape[1], frame.shape[0], detections
            )
            
            # Draw
            frame = detector.draw_detections(frame, detections)
            stats = {
                "vehicles": vehicle_count,
                "density": analysis["density"],
                "level": analysis["level"],
                "trend": "STABLE"
            }
            frame = dashboard.add_traffic_stats(frame, stats)
            
            # Display
            cv2.imshow("Traffic Detection Test", frame)
            
            frame_count += 1
            if frame_count % 30 == 0:
                logger.info(f"Frame {frame_count}: {vehicle_count} vehicles, "
                           f"Level: {analysis['level']}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        logger.info("Test completed")
    
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    test_detector()
