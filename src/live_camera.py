"""Live camera streaming and display"""

import cv2
import time
from pathlib import Path
from datetime import datetime
from threading import Thread, Lock
from queue import Queue
from config.config import (
    FRAME_WIDTH, FRAME_HEIGHT, FPS, 
    CAMERA_SOURCES
)
from src.logger import logger

class LiveCameraStream:
    """Handles live camera streaming"""
    
    def __init__(self, camera_id: str = "camera_0", source=None):
        self.camera_id = camera_id
        self.source = source if source is not None else CAMERA_SOURCES.get(camera_id, 0)
        self.cap = None
        self.is_running = False
        self.frame_buffer = Queue(maxsize=2)
        self.fps_counter = 0
        self.fps = 0
        self.frame_lock = Lock()
        self.current_frame = None
        self.stream_thread = None
        self.recording = False
        self.video_writer = None
        self.frames_captured = 0
        
        self.open_stream()
    
    def open_stream(self):
        """Open camera stream"""
        try:
            logger.info(f"Opening camera stream: {self.camera_id} ({self.source})")
            self.cap = cv2.VideoCapture(self.source)
            
            if not self.cap.isOpened():
                raise ValueError(f"Cannot open camera: {self.source}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            logger.info(f"Camera stream opened successfully: {self.camera_id}")
        
        except Exception as e:
            logger.error(f"Failed to open camera stream: {e}")
            raise
    
    def start_stream(self):
        """Start streaming in background thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.stream_thread = Thread(target=self._stream_loop, daemon=True)
        self.stream_thread.start()
        logger.info(f"Live stream started: {self.camera_id}")
    
    def _stream_loop(self):
        """Background streaming loop"""
        fps_time = time.time()
        frame_count = 0
        
        while self.is_running:
            ret, frame = self.cap.read()
            
            if ret:
                # Update current frame
                with self.frame_lock:
                    self.current_frame = frame
                    self.frames_captured += 1
                
                # Add to buffer
                try:
                    self.frame_buffer.put_nowait(frame)
                except:
                    pass  # Buffer full, skip frame
                
                # Calculate FPS
                frame_count += 1
                current_time = time.time()
                if current_time - fps_time >= 1.0:
                    self.fps = frame_count
                    frame_count = 0
                    fps_time = current_time
                
                # Record if enabled
                if self.recording and self.video_writer:
                    self.video_writer.write(frame)
            
            else:
                logger.warning(f"Failed to read frame from {self.camera_id}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Get current frame"""
        with self.frame_lock:
            return self.current_frame
    
    def get_buffered_frame(self, timeout=1):
        """Get frame from buffer (non-blocking)"""
        try:
            return self.frame_buffer.get(timeout=timeout)
        except:
            return None
    
    def start_recording(self, output_dir: str = "recordings"):
        """Start recording frames to video file"""
        try:
            Path(output_dir).mkdir(exist_ok=True)
            
            filename = f"{output_dir}/{self.camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            
            self.video_writer = cv2.VideoWriter(
                filename, fourcc, self.fps, 
                (FRAME_WIDTH, FRAME_HEIGHT)
            )
            
            self.recording = True
            logger.info(f"Recording started: {filename}")
            return filename
        
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            return None
    
    def stop_recording(self):
        """Stop recording"""
        if self.recording and self.video_writer:
            self.video_writer.release()
            self.recording = False
            logger.info("Recording stopped")
    
    def take_snapshot(self, output_dir: str = "snapshots") -> str:
        """Take a snapshot"""
        try:
            Path(output_dir).mkdir(exist_ok=True)
            frame = self.get_frame()
            
            if frame is not None:
                filename = f"{output_dir}/{self.camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(filename, frame)
                logger.info(f"Snapshot saved: {filename}")
                return filename
        
        except Exception as e:
            logger.error(f"Failed to take snapshot: {e}")
        
        return None
    
    def get_stream_info(self) -> dict:
        """Get stream information"""
        return {
            "camera_id": self.camera_id,
            "source": str(self.source),
            "running": self.is_running,
            "fps": self.fps,
            "frames_captured": self.frames_captured,
            "recording": self.recording,
            "width": FRAME_WIDTH,
            "height": FRAME_HEIGHT
        }
    
    def stop_stream(self):
        """Stop streaming"""
        self.is_running = False
        self.stop_recording()
        
        if self.stream_thread:
            self.stream_thread.join(timeout=2)
        
        if self.cap:
            self.cap.release()
        
        logger.info(f"Camera stream stopped: {self.camera_id}")
    
    def __del__(self):
        """Cleanup"""
        self.stop_stream()


class MultiCameraManager:
    """Manages multiple camera streams"""
    
    def __init__(self):
        self.cameras = {}
        self.active_camera = None
    
    def add_camera(self, camera_id: str, source=None):
        """Add camera stream"""
        try:
            camera = LiveCameraStream(camera_id, source)
            camera.start_stream()
            self.cameras[camera_id] = camera
            
            if not self.active_camera:
                self.active_camera = camera_id
            
            logger.info(f"Camera added: {camera_id}")
            return camera
        
        except Exception as e:
            logger.error(f"Failed to add camera: {e}")
            return None
    
    def switch_camera(self, camera_id: str):
        """Switch to different camera"""
        if camera_id in self.cameras:
            self.active_camera = camera_id
            logger.info(f"Switched to camera: {camera_id}")
            return True
        return False
    
    def get_active_frame(self):
        """Get frame from active camera"""
        if self.active_camera and self.active_camera in self.cameras:
            return self.cameras[self.active_camera].get_frame()
        return None
    
    def get_all_frames(self) -> dict:
        """Get frames from all cameras"""
        frames = {}
        for camera_id, camera in self.cameras.items():
            frames[camera_id] = camera.get_frame()
        return frames
    
    def start_all_streams(self):
        """Start all camera streams"""
        for camera in self.cameras.values():
            if not camera.is_running:
                camera.start_stream()
        logger.info("All camera streams started")
    
    def stop_all_streams(self):
        """Stop all camera streams"""
        for camera in self.cameras.values():
            camera.stop_stream()
        logger.info("All camera streams stopped")
    
    def get_streams_info(self) -> dict:
        """Get info about all streams"""
        return {
            camera_id: camera.get_stream_info()
            for camera_id, camera in self.cameras.items()
        }
    
    def __del__(self):
        """Cleanup"""
        self.stop_all_streams()
