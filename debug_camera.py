"""Debug camera display - show raw frame"""
import cv2
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.camera_handler import CameraHandler
from src.logger import logger

print("Testing raw camera feed display...")

try:
    camera = CameraHandler(0)
    
    print("Got camera handler, reading frames...")
    
    for i in range(50):
        frame = camera.get_frame()
        
        if frame is None:
            print(f"Frame {i}: None")
            continue
        
        print(f"Frame {i}: shape={frame.shape}, dtype={frame.dtype}, min={frame.min()}, max={frame.max()}")
        
        # Display raw frame
        cv2.imshow("Raw Camera Frame", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    camera.stop_capture()
    cv2.destroyAllWindows()
    print("Test completed")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
