"""Record incidents for later analysis"""

import cv2
from pathlib import Path
from datetime import datetime
import json
from src.logger import logger


class IncidentRecorder:
    """
    Record video footage of accidents, violations, and incidents
    Automatically organizes by incident type and timestamp
    """
    
    def __init__(self, output_dir='incidents', frame_width=1280, frame_height=720, fps=30):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        
        self.current_video = None
        self.current_filename = None
        self.frame_count = 0
        self.is_recording = False
        
        # Create subdirectories for organized storage
        (self.output_dir / 'accidents').mkdir(exist_ok=True)
        (self.output_dir / 'speeding').mkdir(exist_ok=True)
        (self.output_dir / 'other').mkdir(exist_ok=True)
        
        logger.info(f"IncidentRecorder initialized: {self.output_dir}")
    
    def start_recording(self, incident_type='accident', details=None):
        """
        Start recording incident
        
        Args:
            incident_type: 'accident', 'speeding', 'other'
            details: Dict with incident information
        """
        if self.is_recording:
            logger.warning("Already recording, stop first")
            return False
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.current_filename = f"{incident_type}_{timestamp}"
        
        # Choose directory
        incident_dir = self.output_dir / incident_type
        filepath = incident_dir / f"{self.current_filename}.mp4"
        
        try:
            # Create video writer with proper codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.current_video = cv2.VideoWriter(
                str(filepath),
                fourcc,
                self.fps,
                (self.frame_width, self.frame_height)
            )
            
            if not self.current_video.isOpened():
                logger.error("Failed to open video writer")
                return False
            
            self.is_recording = True
            self.frame_count = 0
            
            # Save metadata
            metadata = {
                'incident_type': incident_type,
                'start_time': datetime.now().isoformat(),
                'details': details or {},
                'frame_width': self.frame_width,
                'frame_height': self.frame_height,
                'fps': self.fps,
                'filepath': str(filepath)
            }
            
            metadata_path = incident_dir / f"{self.current_filename}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Started recording: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    def write_frame(self, frame):
        """
        Write frame to recording
        
        Args:
            frame: OpenCV frame (BGR format)
        """
        if not self.is_recording or self.current_video is None:
            return False
        
        try:
            # Resize if needed
            frame_resized = cv2.resize(frame, (self.frame_width, self.frame_height))
            self.current_video.write(frame_resized)
            self.frame_count += 1
            return True
        except Exception as e:
            logger.error(f"Error writing frame: {e}")
            return False
    
    def stop_recording(self):
        """Stop recording and finalize video"""
        if not self.is_recording or self.current_video is None:
            return False
        
        try:
            self.current_video.release()
            self.is_recording = False
            
            logger.info(f"Stopped recording: {self.frame_count} frames saved ({self.current_filename})")
            return True
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return False
    
    def get_recording_status(self):
        """Get current recording status"""
        return {
            'is_recording': self.is_recording,
            'current_file': self.current_filename,
            'frames_recorded': self.frame_count
        }
    
    def get_incident_list(self, incident_type='all'):
        """Get list of recorded incidents"""
        incidents = []
        
        if incident_type == 'all':
            search_dirs = [d for d in self.output_dir.glob('*') if d.is_dir()]
        else:
            search_dirs = [self.output_dir / incident_type]
        
        for d in search_dirs:
            if d.is_dir():
                for json_file in d.glob('*.json'):
                    try:
                        with open(json_file, 'r') as f:
                            metadata = json.load(f)
                            video_file = json_file.with_suffix('.mp4')
                            if video_file.exists():
                                incidents.append({
                                    'type': d.name,
                                    'name': json_file.stem,
                                    'video': str(video_file),
                                    'metadata': metadata,
                                    'file_size_mb': round(video_file.stat().st_size / (1024*1024), 2)
                                })
                    except Exception as e:
                        logger.error(f"Error reading incident metadata: {e}")
        
        return sorted(incidents, key=lambda x: x['metadata']['start_time'], reverse=True)
    
    def cleanup_old_incidents(self, days=30):
        """Delete incidents older than N days"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        total_freed_mb = 0
        
        try:
            for incident_file in self.output_dir.rglob('*.mp4'):
                file_time = datetime.fromtimestamp(incident_file.stat().st_mtime)
                if file_time < cutoff_date:
                    file_size = incident_file.stat().st_size / (1024*1024)
                    incident_file.unlink()
                    incident_file.with_suffix('.json').unlink(missing_ok=True)
                    deleted_count += 1
                    total_freed_mb += file_size
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old incident files ({total_freed_mb:.1f} MB freed)")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up incidents: {e}")
            return 0
    
    def get_storage_stats(self):
        """Get storage statistics"""
        try:
            total_size = 0
            total_files = 0
            type_stats = {}
            
            for incident_dir in self.output_dir.glob('*'):
                if incident_dir.is_dir():
                    type_stats[incident_dir.name] = {
                        'count': 0,
                        'size_mb': 0
                    }
                    
                    for video_file in incident_dir.glob('*.mp4'):
                        size = video_file.stat().st_size
                        total_size += size
                        total_files += 1
                        type_stats[incident_dir.name]['count'] += 1
                        type_stats[incident_dir.name]['size_mb'] += size / (1024*1024)
            
            return {
                'total_files': total_files,
                'total_size_mb': round(total_size / (1024*1024), 2),
                'by_type': type_stats
            }
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
