"""Emergency service notification system"""

import threading
import time
from datetime import datetime, timedelta
from src.logger import logger
import subprocess
import sys
import os

class EmergencyServiceManager:
    """Manages emergency service calls"""
    
    # Emergency service phone numbers (can be configured)
    EMERGENCY_NUMBERS = {
        'police': '100',      # India police emergency
        'ambulance': '102',   # India ambulance emergency
        'fire': '101',        # India fire emergency
        'unified': '112'      # Unified emergency number
    }
    
    def __init__(self, enable_calls=False):
        """
        Initialize emergency service manager
        
        Args:
            enable_calls: Enable actual emergency calls (use with caution!)
        """
        self.enable_calls = enable_calls
        self.call_history = []
        self.ongoing_calls = {}
        self.cooldown_period = 30  # seconds - prevent duplicate calls
        self.call_lock = threading.Lock()
    
    def log_emergency_call(self, service_type, incident_type, location=None, details=None):
        """Log an emergency call"""
        call_info = {
            'timestamp': datetime.now(),
            'service_type': service_type,
            'incident_type': incident_type,
            'location': location or 'Unknown',
            'details': details or {},
            'phone_number': self.EMERGENCY_NUMBERS.get(service_type, 'Unknown')
        }
        self.call_history.append(call_info)
        return call_info
    
    def is_duplicate_call(self, service_type, incident_type):
        """Check if same type of call was made recently"""
        with self.call_lock:
            key = f"{service_type}_{incident_type}"
            
            if key in self.ongoing_calls:
                last_call_time = self.ongoing_calls[key]
                if datetime.now() - last_call_time < timedelta(seconds=self.cooldown_period):
                    return True
            
            return False
    
    def ring_alarm(self, duration=5, frequency=1000):
        """
        Ring alarm sound
        
        Args:
            duration: Duration in seconds
            frequency: Frequency in Hz (1000 Hz for warning beep)
        """
        logger.warning(f"[ALARM] RINGING - Duration: {duration}s, Frequency: {frequency}Hz")
        
        try:
            if sys.platform == 'win32':
                # Windows beep
                import winsound
                winsound.Beep(frequency, duration * 1000)
            elif sys.platform == 'darwin':
                # macOS
                os.system(f'afplay /System/Library/Sounds/Alarm.aiff')
            else:
                # Linux - try beep or speaker-test
                os.system(f'beep -f {frequency} -l {duration * 1000}')
        except Exception as e:
            logger.error(f"Error ringing alarm: {e}")
    
    def ring_alarm_threaded(self, duration=5, frequency=1000, num_rings=3):
        """Ring alarm in a separate thread"""
        def _ring():
            for i in range(num_rings):
                self.ring_alarm(duration, frequency)
                if i < num_rings - 1:
                    time.sleep(0.5)
        
        thread = threading.Thread(target=_ring, daemon=True)
        thread.start()
    
    def call_emergency_service(self, service_type, incident_type, location=None, details=None):
        """
        Call emergency service
        
        Args:
            service_type: 'police', 'ambulance', 'fire', or 'unified'
            incident_type: Type of incident
            location: Location of incident
            details: Additional details dict
        """
        # Check for duplicate calls
        if self.is_duplicate_call(service_type, incident_type):
            logger.warning(f"Duplicate {service_type} call suppressed (cooldown active)")
            return None
        
        # Log the call
        call_info = self.log_emergency_call(service_type, incident_type, location, details)
        
        # Ring alarm
        if incident_type in ['COLLISION', 'FIRE', 'ACCIDENT', 'SUDDEN_STOP', 'SPEEDING']:
            self.ring_alarm_threaded(duration=2, frequency=800, num_rings=3)
        
        # Record ongoing call
        with self.call_lock:
            key = f"{service_type}_{incident_type}"
            self.ongoing_calls[key] = datetime.now()
        
        # Log emergency call
        phone = call_info['phone_number']
        logger.critical(
            f"[EMERGENCY_CALL] Service: {service_type.upper()} (Phone: {phone}) - "
            f"Incident: {incident_type} | Location: {location} | Time: {call_info['timestamp']}"
        )
        
        # Additional info logging
        if details:
            logger.critical(f"[EMERGENCY_CALL_DETAILS] {details}")
        
        # In a real system, you would initiate the actual call here
        # For demonstration, we log it
        
        return call_info
    
    def call_police(self, incident_type, location=None, details=None):
        """Call police"""
        return self.call_emergency_service('police', incident_type, location, details)
    
    def call_ambulance(self, incident_type, location=None, details=None):
        """Call ambulance"""
        return self.call_emergency_service('ambulance', incident_type, location, details)
    
    def call_fire_brigade(self, incident_type, location=None, details=None):
        """Call fire brigade"""
        return self.call_emergency_service('fire', incident_type, location, details)
    
    def handle_speeding_vehicle(self, vehicle_info, excess_speed):
        """Handle speeding vehicle - alert and log"""
        details = {
            'vehicle_id': vehicle_info.get('track_id'),
            'vehicle_class': vehicle_info.get('class_name'),
            'current_speed': vehicle_info.get('speed', 0),
            'excess_speed': excess_speed,
            'location': (vehicle_info.get('center')[0], vehicle_info.get('center')[1])
        }
        
        logger.warning(
            f"[SPEEDING_ALERT] {vehicle_info.get('class_name')} "
            f"at {vehicle_info.get('speed', 0):.1f} km/h "
            f"(excess: {excess_speed:.1f} km/h)"
        )
        
        # Call police if significantly over speed
        if excess_speed >= 20:  # 80+ km/h when limit is 60
            self.call_police(
                incident_type='SPEEDING_VIOLATION',
                location='Traffic Monitoring Zone',
                details=details
            )
    
    def handle_accident(self, incident_info):
        """Handle accident - call police, ambulance, and fire brigade"""
        location = 'Traffic Monitoring Zone'
        details = {
            'incident_type': incident_info.get('type'),
            'vehicle_ids': [incident_info.get('vehicle1_id'), incident_info.get('vehicle2_id')],
            'location': incident_info.get('center')
        }
        
        logger.critical(f"[ACCIDENT_DETECTED] Type: {incident_info.get('type')}")
        
        # Call all emergency services for accident/crash
        self.call_police('ACCIDENT', location, details)
        self.call_ambulance('ACCIDENT', location, details)
        self.call_fire_brigade('ACCIDENT', location, details)
    
    def handle_fire_incident(self, fire_info):
        """Handle fire incident - call police, ambulance, and fire brigade"""
        location = 'Traffic Monitoring Zone'
        details = {
            'fire_class': fire_info.get('class_name'),
            'confidence': fire_info.get('confidence'),
            'location': fire_info.get('center')
        }
        
        logger.critical(f"[FIRE_DETECTED] Class: {fire_info.get('class_name')}")
        
        # Call all emergency services
        self.call_police('FIRE_INCIDENT', location, details)
        self.call_ambulance('FIRE_INCIDENT', location, details)
        self.call_fire_brigade('FIRE_INCIDENT', location, details)
    
    def get_call_history(self, limit=50):
        """Get emergency call history"""
        return self.call_history[-limit:]
    
    def get_call_statistics(self):
        """Get statistics of emergency calls"""
        stats = {
            'total_calls': len(self.call_history),
            'by_service': {},
            'by_incident_type': {},
            'today_calls': 0
        }
        
        today = datetime.now().date()
        
        for call in self.call_history:
            service = call['service_type']
            incident = call['incident_type']
            
            stats['by_service'][service] = stats['by_service'].get(service, 0) + 1
            stats['by_incident_type'][incident] = stats['by_incident_type'].get(incident, 0) + 1
            
            if call['timestamp'].date() == today:
                stats['today_calls'] += 1
        
        return stats
