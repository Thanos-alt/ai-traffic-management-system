"""Test: Save first frame to verify camera is working"""
import cv2
import numpy as np

print("Connecting to camera...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Failed to open camera!")
    exit(1)

# Set to 1280x720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Reading 5 frames...")

for i in range(5):
    ret, frame = cap.read()
    if ret:
        print(f"Frame {i}: shape={frame.shape}, min={frame.min()}, max={frame.max()}, mean={frame.mean():.1f}")
        
        # Save first good frame
        if i == 0:
            cv2.imwrite('test_frame.jpg', frame)
            print("Saved test_frame.jpg")
            
            # Display it
            cv2.imshow('Camera Test', frame)
            print("Displaying frame, press any key to continue...")
            cv2.waitKey(0)
    else:
        print(f"Frame {i}: Failed to read")

cap.release()
cv2.destroyAllWindows()

print("\nTest completed")
print("Check test_frame.jpg to verify camera data")
