"""Test to display raw camera feed without processing"""
import cv2
import sys

print("Opening raw camera feed test...")

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Failed to open camera!")
    sys.exit(1)

print("Camera opened. Press 'q' to quit")

frame_count = 0
while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Failed to read frame")
        break
    
    frame_count += 1
    
    # Add text to frame
    cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display
    cv2.imshow("Raw Camera Feed", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

print(f"Total frames: {frame_count}")
cap.release()
cv2.destroyAllWindows()
print("Test completed")
