"""Pure camera display - no processing"""
import cv2
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.camera_handler import CameraHandler
from src.logger import logger

def main():
    logger.info("Starting pure camera display test...")
    
    try:
        camera = CameraHandler(0)
        running = True
        frame_count = 0
        
        while running and frame_count < 100:
            # Get raw frame
            frame = camera.get_frame()
            
            if frame is None:
                logger.warning("Failed to get frame")
                time.sleep(0.1)
                continue
            
            # Create a copy to display
            display = frame.copy()
            
            # Add frame counter
            cv2.putText(display, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show the frame
            cv2.imshow("Camera Feed (Raw)", display)
            
            # Handle input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                running = False
            
            frame_count += 1
            
            if frame_count % 30 == 0:
                logger.info(f"Displayed {frame_count} frames")
        
        camera.stop_capture()
        cv2.destroyAllWindows()
        logger.info(f"Test completed. Total frames: {frame_count}")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
