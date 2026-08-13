"""Simple camera test"""
import cv2
import sys
import time

print("Testing camera access...")

for camera_id in range(5):
    print(f"\nTrying camera device: {camera_id}")
    cap = cv2.VideoCapture(camera_id)
    
    if cap.isOpened():
        print(f"✓ Camera {camera_id} opened successfully!")
        
        # Try to read a frame
        ret, frame = cap.read()
        if ret:
            print(f"✓ Successfully read frame from camera {camera_id}")
            print(f"  Frame shape: {frame.shape}")
            
            # Try to display it
            cv2.imshow(f"Camera {camera_id}", frame)
            print("✓ Frame displayed (press any key to continue)")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print(f"✗ Failed to read frame from camera {camera_id}")
        
        cap.release()
        break
    else:
        print(f"✗ Camera {camera_id} not available")
else:
    print("\n✗ No camera devices found!")
    sys.exit(1)

print("\nCamera test completed successfully!")
