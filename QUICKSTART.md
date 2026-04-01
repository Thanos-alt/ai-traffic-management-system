"""Quick start guide"""

# AI Traffic Management System - Quick Start

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Verify Installation
```bash
python test_detector.py
```

## Step 3: Run Main Application
```bash
python main.py
```

## Configuration Options

### Edit config/config.py to customize:

### Model Settings
- `CONFIDENCE_THRESHOLD`: 0.5 (lower = more detections)
- `IOU_THRESHOLD`: 0.45 (IoU for NMS)

### Camera Settings
- `CAMERA_SOURCES`: Dict of camera definitions
- `FRAME_WIDTH`: 640
- `FRAME_HEIGHT`: 480
- `FPS`: 30

### Traffic Settings
- `MIN_VEHICLES_ALERT`: 10 (alert threshold)
- `TRAFFIC_DENSITY_THRESHOLD`: 0.7 (70% for HIGH)

### Voice Settings
- `ENABLE_VOICE`: True/False
- `VOICE_RATE`: 150 (words per minute)
- `VOICE_VOLUME`: 0.9

## Keyboard Controls While Running

- `q` - Quit
- `p` - Pause/Resume
- `s` - Save screenshot

## Troubleshooting

### Application won't start
- Check Python version (3.8+)
- Verify all dependencies installed
- Check logs in logs/ directory

### No camera detected
- Check if camera is connected
- Try different camera source (0, 1, 2, etc.)
- Verify no other app is using camera

### Model not loading
- Models are auto-downloaded on first run (~50MB)
- Check internet connection
- Manual download: `python -c "from ultralytics import YOLO; YOLO('yolov11n')"`

### Slow performance
- Reduce FRAME_WIDTH/FRAME_HEIGHT in config
- Lower CONFIDENCE_THRESHOLD slightly
- Check CPU/GPU usage in Task Manager

## System Requirements

- Windows/Linux/Mac
- Python 3.8+
- 4GB RAM minimum
- Webcam or IP camera with RTSP support
- GPU optional but recommended for real-time processing
