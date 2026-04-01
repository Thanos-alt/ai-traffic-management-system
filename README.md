# AI Traffic Management System

Real-time traffic monitoring and management using YOLOv11n object detection.

## Features

- **YOLOv11n Vehicle Detection**: Fast and accurate vehicle detection in real-time
- **Traffic Density Analysis**: Calculates traffic congestion levels based on vehicle distribution
- **Voice Alerts**: Text-to-speech alerts for traffic incidents
- **Multi-Camera Support**: Process multiple video streams simultaneously
- **HSR Status Monitoring**: Human Shoulder Responsibility status tracking
- **Real-time Dashboard**: Visual overlay with traffic statistics
- **FPS Monitoring**: Real-time performance metrics

## Project Structure

```
ai traffic management/
├── config/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   └── logging.py             # Logging setup
├── src/
│   ├── __init__.py
│   ├── camera_handler.py      # Video capture handling
│   ├── traffic_detector.py    # YOLOv11n detection
│   ├── voice_alert.py         # Voice alert system
│   ├── dashboard.py           # UI overlays
│   ├── hsr_monitor.py         # HSR status monitoring
│   └── logger.py              # Logging utilities
├── models/                     # Store YOLOv11n model here
├── logs/                       # Application logs
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. **Clone the repository**
```bash
cd "ai traffic management"
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download YOLOv11n model**
The model will be automatically downloaded on first run, or manually:
```bash
python -c "from ultralytics import YOLO; YOLO('yolov11n.pt')"
```

## Usage

### Basic Usage
```bash
python main.py
```

### Keyboard Controls
- `q` - Quit application
- `p` - Pause/Resume
- `s` - Save current frame

### Configuration

Edit `config/config.py` to customize:
- Model settings (confidence threshold, IOU)
- Camera sources
- Voice alert settings
- Traffic density thresholds
- HSR monitoring parameters

## Features Explanation

### Traffic Detection
- Detects vehicles (cars, motorcycles, buses, trucks)
- Calculates vehicle count and distribution
- Analyzes traffic density as percentage of frame area

### Traffic Levels
- **LOW**: Density < 40% (Green)
- **MEDIUM**: Density 40-70% (Orange)
- **HIGH**: Density > 70% (Red)

### Traffic Trend
- **INCREASING**: Traffic congestion rising
- **DECREASING**: Traffic congestion reducing
- **STABLE**: No significant change

### HSR (Human Shoulder Responsibility) Status
- **OPEN**: Normal operations
- **CLOSING**: High traffic detected
- **CLOSED**: Occupancy at 0%

### Voice Alerts
- High traffic alerts
- Incident notifications
- Lane closure announcements
- Normal flow confirmations

## Performance

- **YOLOv11n**: Fast lightweight model (~5-10ms inference per frame)
- **Real-time Processing**: 30+ FPS on modern systems
- **Multi-threaded**: Background frame capture for smooth operation

## System Requirements

- Python 3.8+
- OpenCV 4.8+
- CUDA-capable GPU (optional, for faster processing)
- 4GB RAM minimum

## Troubleshooting

### Camera Not Opening
- Check camera permissions
- Verify camera is not in use by another application
- Try different camera source in config

### Model Download Issues
- Check internet connection
- Verify disk space (model is ~50MB)
- Download manually from Ultralytics

### Voice Not Working
- Check system volume
- Verify pyttsx3 engine initialization
- Check logs for errors

## Performance Optimization

1. Reduce frame resolution in config
2. Increase frame skip rate
3. Lower confidence threshold
4. Use GPU acceleration with CUDA

## License

This project is licensed under the MIT License.

## Support

For issues and questions, check the logs in the `logs/` directory.
