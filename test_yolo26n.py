"""Test yolo26n model loading"""

from src.traffic_detector import TrafficDetector
import sys

print('Loading yolo26n traffic detector...')
try:
    detector = TrafficDetector()
    print('✓ Detector loaded successfully!')
    print(f'  Model: {detector.model.model_name}')
    print(f'  Vehicle classes: {detector.vehicle_classes}')
    sys.exit(0)
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
