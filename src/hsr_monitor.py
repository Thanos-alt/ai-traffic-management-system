"""HSR (Human Shoulder Responsibility) Status Monitor"""

import time
from datetime import datetime
from config.config import HSR_STATUS_CHECK_INTERVAL, HSR_CLOSING_THRESHOLD
from src.logger import logger

class HSRMonitor:
    """Monitors HSR (Human Shoulder Responsibility) status"""
    
    def __init__(self):
        self.status = "OPEN"  # OPEN, CLOSING, CLOSED
        self.consecutive_close_frames = 0
        self.last_status_change = datetime.now()
        self.status_history = []
        self.is_monitoring = False
    
    def update_status(self, detected_incident: bool):
        """Update HSR status based on detected incidents"""
        
        if detected_incident:
            self.consecutive_close_frames += 1
        else:
            self.consecutive_close_frames = 0
        
        # Check if should change status
        if self.consecutive_close_frames >= HSR_CLOSING_THRESHOLD:
            if self.status != "CLOSED":
                self._change_status("CLOSED")
        elif self.status == "CLOSED" and self.consecutive_close_frames == 0:
            self._change_status("OPEN")
    
    def _change_status(self, new_status: str):
        """Change HSR status and log it"""
        if self.status != new_status:
            old_status = self.status
            self.status = new_status
            self.last_status_change = datetime.now()
            
            self.status_history.append({
                "timestamp": self.last_status_change,
                "previous_status": old_status,
                "new_status": new_status
            })
            
            logger.info(f"HSR Status changed: {old_status} -> {new_status}")
            
            if new_status == "CLOSED":
                logger.warning("HSR status is CLOSED - occupancy at 0%")
            else:
                logger.info("HSR status is OPEN - normal operations")
    
    def get_status(self) -> dict:
        """Get current HSR status"""
        return {
            "status": self.status,
            "consecutive_frames": self.consecutive_close_frames,
            "last_change": self.last_status_change,
            "threshold": HSR_CLOSING_THRESHOLD
        }
    
    def get_status_history(self, limit: int = 10) -> list:
        """Get recent status changes"""
        return self.status_history[-limit:]
    
    def reset_monitoring(self):
        """Reset monitoring"""
        self.consecutive_close_frames = 0
        self.status = "OPEN"
        logger.info("HSR monitoring reset")
