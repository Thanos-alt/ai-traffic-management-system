"""Voice alert system for traffic incidents"""

import pyttsx3
import threading
from config.config import ENABLE_VOICE, VOICE_RATE, VOICE_VOLUME
from src.logger import logger

class VoiceAlertSystem:
    """Handles voice alerts for traffic incidents"""
    
    def __init__(self):
        self.enable_voice = ENABLE_VOICE
        if self.enable_voice:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', VOICE_RATE)
                self.engine.setProperty('volume', VOICE_VOLUME)
                logger.info("Voice engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize voice engine: {e}")
                self.enable_voice = False
    
    def speak(self, message: str):
        """Speak the given message in a separate thread"""
        if not self.enable_voice:
            return
        
        def _speak():
            try:
                self.engine.say(message)
                self.engine.runAndWait()
                logger.info(f"Voice alert: {message}")
            except Exception as e:
                logger.error(f"Error in voice alert: {e}")
        
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()
    
    def alert_high_traffic(self, lane: str):
        """Alert for high traffic condition"""
        message = f"High traffic detected on {lane}"
        self.speak(message)
    
    def alert_incident(self, incident_type: str):
        """Alert for traffic incident"""
        message = f"Traffic incident detected: {incident_type}"
        self.speak(message)
    
    def alert_normal_flow(self):
        """Alert when traffic returns to normal"""
        message = "Traffic flow is back to normal"
        self.speak(message)
    
    def alert_lane_closure(self, lane: str):
        """Alert for lane closure"""
        message = f"Lane {lane} is being closed. Please use alternate route"
        self.speak(message)
    
    def alert_speeding_vehicle(self, speed: float, speed_limit: float = 60):
        """Alert for speeding vehicle"""
        message = f"Speeding detected. Vehicle is traveling at {speed:.0f} kilometers per hour. Speed limit is {speed_limit:.0f}. Police will be notified."
        self.speak(message)
    
    def alert_collision(self):
        """Alert for collision detected"""
        message = "Collision detected! Emergency services are being contacted."
        self.speak(message)
    
    def alert_accident(self):
        """Alert for accident detected"""
        message = "Traffic accident detected! Police and ambulance are being contacted."
        self.speak(message)
    
    def alert_fire(self):
        """Alert for fire incident"""
        message = "Fire detected! Police, ambulance, and fire brigade are being contacted immediately."
        self.speak(message)
    
    def alert_sudden_stop(self):
        """Alert for sudden stop (possible accident)"""
        message = "Sudden vehicle stop detected. This may indicate an accident."
        self.speak(message)

    def shutdown(self):
        """Shutdown voice engine"""
        if self.enable_voice:
            try:
                self.engine.stop()
                logger.info("Voice engine shutdown successfully")
            except Exception as e:
                logger.error(f"Error shutting down voice engine: {e}")
