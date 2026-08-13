"""GPS tracking and location management module"""

import json
from datetime import datetime
from pathlib import Path
from src.logger import logger


class GPSTracker:
    """GPS tracking and location management"""
    
    def __init__(self, default_lat=40.7128, default_lon=-74.0060, location_name="New York"):
        """
        Initialize GPS tracker
        
        Args:
            default_lat: Default latitude (NYC by default)
            default_lon: Default longitude (NYC by default)
            location_name: Current location name
        """
        self.latitude = default_lat
        self.longitude = default_lon
        self.location_name = location_name
        self.altitude = 0
        self.speed = 0
        self.accuracy = None
        
        self.location_history = []
        self.max_history = 100
        self.last_update = None
        
        self.traffic_hotspots = {}  # Track high-traffic areas
        self.location_data_file = Path("location_data.json")
        
        self.load_saved_location()
    
    def update_location(self, latitude, longitude, location_name=None, altitude=0, speed=0, accuracy=None):
        """
        Update current GPS location
        
        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            location_name: Human-readable location name
            altitude: GPS altitude in meters
            speed: GPS speed in km/h
            accuracy: GPS accuracy radius in meters
        """
        self.latitude = latitude
        self.longitude = longitude
        if location_name:
            self.location_name = location_name
        self.altitude = altitude
        self.speed = speed
        self.accuracy = accuracy
        self.last_update = datetime.now()
        
        # Add to history
        location_entry = {
            "lat": latitude,
            "lon": longitude,
            "name": self.location_name,
            "altitude": altitude,
            "speed": speed,
            "timestamp": str(datetime.now()),
            "high_traffic": False
        }
        
        self.location_history.append(location_entry)
        if len(self.location_history) > self.max_history:
            self.location_history.pop(0)
        
        logger.info(f"GPS Location Updated: {self.location_name} ({latitude:.4f}, {longitude:.4f})")
    
    def mark_high_traffic_zone(self, traffic_level="HIGH"):
        """Mark current location as high traffic zone"""
        if self.location_history:
            self.location_history[-1]["high_traffic"] = traffic_level
            
            # Add to hotspots tracking
            location_key = f"{self.latitude:.4f},{self.longitude:.4f}"
            if location_key not in self.traffic_hotspots:
                self.traffic_hotspots[location_key] = {
                    "count": 0,
                    "lat": self.latitude,
                    "lon": self.longitude,
                    "name": self.location_name,
                    "first_detected": str(datetime.now())
                }
            
            self.traffic_hotspots[location_key]["count"] += 1
            self.traffic_hotspots[location_key]["last_detected"] = str(datetime.now())
    
    def get_current_location(self):
        """Get current GPS location"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "location_name": self.location_name,
            "altitude": self.altitude,
            "speed": self.speed,
            "accuracy": self.accuracy,
            "timestamp": str(self.last_update) if self.last_update else "Unknown"
        }
    
    def get_location_history(self):
        """Get location history"""
        return self.location_history
    
    def get_traffic_hotspots(self):
        """Get identified high-traffic zones"""
        # Sort by frequency
        sorted_hotspots = sorted(
            self.traffic_hotspots.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        return [spot[1] for spot in sorted_hotspots[:10]]  # Top 10 hotspots
    
    def save_location_data(self):
        """Save location and traffic data to file"""
        try:
            data = {
                "current_location": self.get_current_location(),
                "location_history": self.location_history[-20:],  # Last 20 locations
                "traffic_hotspots": self.get_traffic_hotspots(),
                "saved_at": str(datetime.now())
            }
            
            with open(self.location_data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Location data saved to {self.location_data_file}")
        except Exception as e:
            logger.error(f"Failed to save location data: {e}")
    
    def load_saved_location(self):
        """Load previously saved location"""
        try:
            if self.location_data_file.exists():
                with open(self.location_data_file, 'r') as f:
                    data = json.load(f)
                    current = data.get("current_location", {})
                    
                    if current:
                        self.update_location(
                            current.get("latitude", self.latitude),
                            current.get("longitude", self.longitude),
                            current.get("location_name", self.location_name),
                            current.get("altitude", 0),
                            current.get("speed", 0)
                        )
                        logger.info("Previous location loaded from file")
        except Exception as e:
            logger.debug(f"Could not load saved location: {e}")
    
    def get_location_string(self):
        """Get formatted location string"""
        return f"{self.location_name} ({self.latitude:.4f}°N, {self.longitude:.4f}°E)"
    
    def get_map_url(self):
        """Get OpenStreetMap URL for current location"""
        return f"https://www.openstreetmap.org/#map=15/{self.latitude}/{self.longitude}"
    
    def get_google_maps_url(self):
        """Get Google Maps URL for current location"""
        return f"https://www.google.com/maps/@{self.latitude},{self.longitude},15z"
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two GPS coordinates using Haversine formula
        Returns distance in kilometers
        """
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        return km
    
    def get_distance_from_previous(self):
        """Get distance from previous location"""
        if len(self.location_history) < 2:
            return 0
        
        prev = self.location_history[-2]
        current = self.location_history[-1]
        
        distance = self.calculate_distance(
            prev["lat"], prev["lon"],
            current["lat"], current["lon"]
        )
        
        return distance
