"""Camera and video source handler"""

import cv2
import time
import threading
import numpy as np
from queue import Queue
from config.config import (
    FPS, FRAME_WIDTH, FRAME_HEIGHT, CAMERA_SOURCES,
    CAMERA_BRIGHTNESS, CAMERA_CONTRAST, CAMERA_SATURATION,
    CAMERA_GAIN, CAMERA_EXPOSURE, CAMERA_AUTO_EXPOSURE,
    CAMERA_WHITE_BALANCE, CAMERA_BUFFER_SIZE, CAMERA_ENHANCE_CONTRAST
)
from src.logger import logger

class CameraHandler:
    """Handles video capture from multiple sources"""
    
    def __init__(self, source=0):
        self.source = source
        self.cap = None
        self.is_running = False
        self.frame_queue = Queue(maxsize=2)
        self.frame_count = 0
        self.fps = FPS
        self.frame_width = FRAME_WIDTH
        self.frame_height = FRAME_HEIGHT
        self.open_camera()
    
    def open_camera(self):
        """Open video capture device"""
        try:
            if isinstance(self.source, str):
                logger.info(f"Opening camera from URL: {self.source}")
                self.cap = cv2.VideoCapture(self.source)
            else:
                logger.info(f"Opening camera device: {self.source}")
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)  # Use DirectShow backend on Windows
            
            # Add timeout check
            for _ in range(5):
                if self.cap.isOpened():
                    break
                time.sleep(0.5)
                self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW) if not isinstance(self.source, str) else cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                raise ValueError(f"Cannot open camera source: {self.source}")
            
            # Set resolution and FPS for quality video capture
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH or 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT or 720)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, CAMERA_BUFFER_SIZE)  # Reduce buffer for lower latency
            
            # Configure camera image properties for natural, clear video
            try:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
                logger.info("Autofocus enabled")
            except:
                pass
            
            # Exposure control - lower values = darker, more detail in bright conditions
            if CAMERA_AUTO_EXPOSURE:
                # Windows: 0 = manual, 1 = auto. Linux: 1 = manual, 3 = auto
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # Auto exposure
                logger.info("Auto-exposure enabled")
            else:
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # Manual exposure
                self.cap.set(cv2.CAP_PROP_EXPOSURE, CAMERA_EXPOSURE)  # Negative values = darker
                logger.info(f"Manual exposure set to {CAMERA_EXPOSURE}")
            
            # White balance
            if CAMERA_WHITE_BALANCE:
                try:
                    self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)  # Auto white balance
                    logger.info("Auto white balance enabled")
                except:
                    pass
            
            # Image properties for natural appearance
            self.cap.set(cv2.CAP_PROP_BRIGHTNESS, CAMERA_BRIGHTNESS)  # -64 to 64
            self.cap.set(cv2.CAP_PROP_CONTRAST, CAMERA_CONTRAST)       # 0 to 100
            self.cap.set(cv2.CAP_PROP_SATURATION, CAMERA_SATURATION)   # 0 to 128
            self.cap.set(cv2.CAP_PROP_GAIN, CAMERA_GAIN)               # 0 to 100
            
            logger.info(f"Camera settings: Brightness={CAMERA_BRIGHTNESS}, Contrast={CAMERA_CONTRAST}, Saturation={CAMERA_SATURATION}")
            
            logger.info(f"Camera opened successfully. Source: {self.source}")
            logger.info(f"Camera resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        
        except Exception as e:
            logger.error(f"Failed to open camera: {e}")
            raise
    
    def get_frame(self):
        """Get current frame with optional contrast enhancement"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if ret:
            self.frame_count += 1
            # Ensure frame is contiguous and correct dtype
            if frame.dtype != np.uint8:
                frame = frame.astype(np.uint8)
            if not frame.flags['C_CONTIGUOUS']:
                frame = np.ascontiguousarray(frame)
            
            # Optional: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # Only if video is too dark - reduces computational load
            if CAMERA_ENHANCE_CONTRAST:
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l_channel = lab[:, :, 0]
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                l_channel = clahe.apply(l_channel)
                lab[:, :, 0] = l_channel
                frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return np.ascontiguousarray(frame)
        return None
    
    def start_capture_thread(self):
        """Start background frame capture thread"""
        if self.is_running:
            return
        
        self.is_running = True
        capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        capture_thread.start()
        logger.info("Camera capture thread started")
    
    def _capture_loop(self):
        """Background capture loop"""
        while self.is_running:
            frame = self.get_frame()
            if frame is not None:
                try:
                    self.frame_queue.put_nowait(frame)
                except:
                    pass  # Queue full, skip frame
    
    def get_queued_frame(self):
        """Get frame from queue (non-blocking)"""
        try:
            return self.frame_queue.get_nowait()
        except:
            return None
    
    def stop_capture(self):
        """Stop camera capture"""
        self.is_running = False
        if self.cap:
            self.cap.release()
        logger.info(f"Camera stopped. Total frames captured: {self.frame_count}")
    
    def get_camera_info(self) -> dict:
        """Get camera information"""
        if not self.cap or not self.cap.isOpened():
            return {"status": "CLOSED"}
        
        return {
            "source": self.source,
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "frame_count": self.frame_count,
            "status": "ACTIVE"
        }
    
    def __del__(self):
        """Cleanup"""
        self.stop_capture()
