# 🚗 Multiple Vehicle Tracking, Speeding Detection & Accident Prediction Guide

## 1️⃣ MULTIPLE VEHICLES & SPEEDING DETECTION AT ONCE

### ✅ What to Use

**Best Approach: Batch Processing + Spatial Indexing**

```
Current System (ByteTrack) + Enhancements:
├── Real-time Detection (YOLO)
├── Multi-object Tracking (ByteTrack) ✓ Already handling multiple vehicles
├── Batch Speeding Alerts (NEW)
├── Spatial Zone Analysis (NEW)
└── Heatmap Generation (NEW)
```

### 🔧 Implementation - Batch Speed Alerts

```python
class MultiVehicleSpeedAnalyzer:
    """Analyze multiple vehicles and speeding in one go"""
    
    def __init__(self):
        self.vehicle_zones = {}  # Zone-based vehicle grouping
        self.speeding_vehicles_frame = []
        self.collision_risk_pairs = []
    
    def batch_analyze_speeds(self, detections, speed_limit_kmh=60):
        """
        Analyze ALL vehicles at once for speeding
        
        Input: detections from YOLOv8 (multiple vehicles)
        Output: List of speeding vehicles + batch alerts
        """
        speeding_batch = []
        safe_vehicles = []
        
        for detection in detections:
            vehicle_id = detection.get('track_id')
            speed = detection.get('speed_kmh', 0)
            
            if speed > speed_limit_kmh:
                speeding_batch.append({
                    'vehicle_id': vehicle_id,
                    'speed': speed,
                    'excess': speed - speed_limit_kmh,
                    'position': detection.get('center'),
                    'confidence': detection.get('confidence')
                })
            else:
                safe_vehicles.append(vehicle_id)
        
        return speeding_batch, safe_vehicles
    
    def batch_alert_speeding(self, speeding_vehicles):
        """
        Send BATCH alerts instead of individual alerts
        Much more efficient for multiple violators
        """
        if not speeding_vehicles:
            return None
        
        # Group by severity
        critical = [v for v in speeding_vehicles if v['excess'] >= 20]  # >80 km/h
        warning = [v for v in speeding_vehicles if 10 <= v['excess'] < 20]  # 70-80
        minor = [v for v in speeding_vehicles if v['excess'] < 10]  # 60-70
        
        alert_summary = {
            'critical_speeders': len(critical),    # Call police
            'warning_speeders': len(warning),      # Log only
            'minor_speeders': len(minor),          # Monitor
            'total_violators': len(speeding_vehicles),
            'avg_excess_speed': sum(v['excess'] for v in speeding_vehicles) / len(speeding_vehicles),
            'max_excess_speed': max(v['excess'] for v in speeding_vehicles),
            'timestamp': datetime.now()
        }
        
        return alert_summary
```

### 📊 Implementation - Spatial Zone Analysis

```python
class SpatialZoneAnalyzer:
    """Divide frame into zones and analyze each zone"""
    
    def __init__(self, frame_width=1280, frame_height=720, zones_x=4, zones_y=3):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.zones_x = zones_x
        self.zones_y = zones_y
        self.zone_data = {}
        
        # Create zones grid
        self.zone_width = frame_width // zones_x
        self.zone_height = frame_height // zones_y
        self.initialize_zones()
    
    def initialize_zones(self):
        """Initialize empty zones"""
        for y in range(self.zones_y):
            for x in range(self.zones_x):
                zone_id = f"zone_{x}_{y}"
                self.zone_data[zone_id] = {
                    'vehicles': [],
                    'speeding_count': 0,
                    'avg_speed': 0,
                    'collision_risk': False
                }
    
    def assign_vehicle_to_zone(self, vehicle):
        """Assign vehicle to zone based on position"""
        x, y = vehicle['center']
        zone_x = int(x // self.zone_width)
        zone_y = int(y // self.zone_height)
        
        # Clamp to valid range
        zone_x = min(zone_x, self.zones_x - 1)
        zone_y = min(zone_y, self.zones_y - 1)
        
        zone_id = f"zone_{zone_x}_{zone_y}"
        return zone_id
    
    def analyze_all_zones(self, detections):
        """Analyze all vehicles in all zones at once"""
        # Reset zones
        self.initialize_zones()
        
        # Assign vehicles to zones
        for vehicle in detections:
            zone_id = self.assign_vehicle_to_zone(vehicle)
            self.zone_data[zone_id]['vehicles'].append(vehicle)
        
        # Analyze each zone
        zone_alerts = []
        
        for zone_id, zone_info in self.zone_data.items():
            vehicles = zone_info['vehicles']
            
            if len(vehicles) == 0:
                continue
            
            # Calculate zone statistics
            speeds = [v.get('speed_kmh', 0) for v in vehicles]
            avg_speed = np.mean(speeds)
            speeding_count = sum(1 for s in speeds if s > 60)
            
            zone_info['avg_speed'] = avg_speed
            zone_info['speeding_count'] = speeding_count
            
            # Alert if too many speeders in zone
            if speeding_count >= 2:
                zone_alerts.append({
                    'zone': zone_id,
                    'vehicle_count': len(vehicles),
                    'speeding_count': speeding_count,
                    'avg_speed': avg_speed,
                    'severity': 'HIGH' if speeding_count >= 3 else 'MEDIUM'
                })
        
        return zone_alerts, self.zone_data
```

### 🎨 Heatmap Visualization

```python
def generate_speeding_heatmap(frame, zone_data, frame_width=1280, frame_height=720):
    """
    Generate heatmap showing speeding density
    Red = High speeding, Yellow = Medium, Green = Safe
    """
    heatmap = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    zones_x = 4
    zones_y = 3
    zone_width = frame_width // zones_x
    zone_height = frame_height // zones_y
    
    for zone_id, zone_info in zone_data.items():
        # Parse zone coordinates
        _, x, y = zone_id.split('_')
        x, y = int(x), int(y)
        
        # Calculate color based on speeding count
        speeding_count = zone_info['speeding_count']
        total_vehicles = len(zone_info['vehicles'])
        
        if total_vehicles == 0:
            color = (0, 255, 0)  # Green - no vehicles
        else:
            ratio = speeding_count / total_vehicles
            if ratio > 0.5:  # >50% speeding
                color = (0, 0, 255)  # Red - high risk
            elif ratio > 0.25:  # 25-50% speeding
                color = (0, 165, 255)  # Orange - medium risk
            else:
                color = (0, 255, 0)  # Green - safe
        
        # Draw zone rectangle
        x1 = x * zone_width
        y1 = y * zone_height
        x2 = x1 + zone_width
        y2 = y1 + zone_height
        
        cv2.rectangle(heatmap, (x1, y1), (x2, y2), color, -1)
        
        # Add zone stats
        text = f"{speeding_count}/{total_vehicles}"
        cv2.putText(heatmap, text, (x1 + 10, y1 + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Blend with original frame
    result = cv2.addWeighted(frame, 0.7, heatmap, 0.3, 0)
    return result
```

---

## 2️⃣ ACCIDENT PREDICTION (Detect Before It Happens)

### ✅ What to Use

**Best Approach: Trajectory Analysis + Collision Probability**

```
Accident Prevention Pipeline:
├── Track Vehicle Trajectories (ByteTrack) ✓
├── Calculate Velocity Vectors (NEW)
├── Estimate Collision Risk (NEW)
├── Predict Accident 1-2 seconds BEFORE (NEW)
└── Alert for preventive measures (NEW)
```

### 🔧 Implementation - Collision Risk Prediction

```python
import numpy as np
from scipy.spatial.distance import euclidean

class AccidentPredictor:
    """Predict accidents before they happen"""
    
    def __init__(self, prediction_horizon_frames=30):  # 1 second ahead at 30 FPS
        """
        Initialize predictor
        
        Args:
            prediction_horizon_frames: How many frames ahead to predict
        """
        self.vehicle_trajectories = {}  # Store position history
        self.vehicle_velocities = {}    # Store velocity vectors
        self.collision_risks = {}
        self.prediction_horizon = prediction_horizon_frames
        self.position_history_length = 10  # Keep last 10 frames of history
    
    def update_vehicle_position(self, vehicle_id, position, speed_kmh):
        """Update vehicle position and calculate velocity"""
        if vehicle_id not in self.vehicle_trajectories:
            self.vehicle_trajectories[vehicle_id] = []
        
        # Add current position to history
        self.vehicle_trajectories[vehicle_id].append({
            'position': position,
            'speed_kmh': speed_kmh,
            'timestamp': time.time()
        })
        
        # Keep only recent history
        if len(self.vehicle_trajectories[vehicle_id]) > self.position_history_length:
            self.vehicle_trajectories[vehicle_id].pop(0)
        
        # Calculate velocity if we have history
        if len(self.vehicle_trajectories[vehicle_id]) >= 2:
            prev = self.vehicle_trajectories[vehicle_id][-2]
            curr = self.vehicle_trajectories[vehicle_id][-1]
            
            dx = curr['position'][0] - prev['position'][0]
            dy = curr['position'][1] - prev['position'][1]
            
            self.vehicle_velocities[vehicle_id] = {
                'velocity_x': dx,
                'velocity_y': dy,
                'magnitude': np.sqrt(dx**2 + dy**2)
            }
    
    def predict_future_position(self, vehicle_id, frames_ahead):
        """
        Predict where vehicle will be N frames ahead
        
        Using linear extrapolation from recent trajectory
        """
        if vehicle_id not in self.vehicle_velocities:
            return None
        
        trajectory = self.vehicle_trajectories[vehicle_id]
        velocity = self.vehicle_velocities[vehicle_id]
        
        if len(trajectory) == 0:
            return None
        
        current_pos = trajectory[-1]['position']
        
        # Predict position
        predicted_x = current_pos[0] + (velocity['velocity_x'] * frames_ahead)
        predicted_y = current_pos[1] + (velocity['velocity_y'] * frames_ahead)
        
        return (predicted_x, predicted_y)
    
    def calculate_collision_risk(self, vehicle1_id, vehicle2_id, frame_width=1280, frame_height=720):
        """
        Calculate collision risk between two vehicles
        Returns risk score 0-1 (0=safe, 1=imminent collision)
        """
        # Get predicted positions
        pos1_predicted = self.predict_future_position(vehicle1_id, self.prediction_horizon)
        pos2_predicted = self.predict_future_position(vehicle2_id, self.prediction_horizon)
        
        if pos1_predicted is None or pos2_predicted is None:
            return 0.0
        
        # Calculate distance between predicted positions
        distance = euclidean(pos1_predicted, pos2_predicted)
        
        # Define collision distance (typical vehicle width ~2 meters = ~40 pixels at PPM=20)
        collision_distance = 50  # pixels
        
        # Calculate risk (higher distance = lower risk)
        if distance < collision_distance:
            risk_score = 1.0 - (distance / collision_distance)
            return min(risk_score, 1.0)
        else:
            # Check if distance is decreasing (vehicles approaching)
            trajectory1 = self.vehicle_trajectories[vehicle1_id]
            trajectory2 = self.vehicle_trajectories[vehicle2_id]
            
            if len(trajectory1) >= 2 and len(trajectory2) >= 2:
                prev_dist = euclidean(
                    trajectory1[-2]['position'],
                    trajectory2[-2]['position']
                )
                curr_dist = distance  # Already calculated above
                
                # If distance decreased, increase risk
                if curr_dist < prev_dist:
                    approach_speed = prev_dist - curr_dist
                    risk_score = min(approach_speed / 100, 0.5)  # Max 0.5 for approaching
                    return risk_score
        
        return 0.0
    
    def predict_accidents(self, detections):
        """
        Check all vehicle pairs for collision risk
        
        Returns list of high-risk pairs
        """
        high_risk_pairs = []
        detections_list = list(detections)
        
        # Update positions
        for det in detections_list:
            vehicle_id = det.get('track_id')
            position = det.get('center')
            speed = det.get('speed_kmh', 0)
            self.update_vehicle_position(vehicle_id, position, speed)
        
        # Check all pairs
        for i in range(len(detections_list)):
            for j in range(i + 1, len(detections_list)):
                v1_id = detections_list[i].get('track_id')
                v2_id = detections_list[j].get('track_id')
                
                risk = self.calculate_collision_risk(v1_id, v2_id)
                
                if risk > 0.3:  # Risk threshold (>30% risk)
                    high_risk_pairs.append({
                        'vehicle1_id': v1_id,
                        'vehicle2_id': v2_id,
                        'collision_risk': risk,
                        'severity': 'CRITICAL' if risk > 0.7 else 'HIGH' if risk > 0.5 else 'MEDIUM'
                    })
        
        return sorted(high_risk_pairs, key=lambda x: x['collision_risk'], reverse=True)
```

### 🚨 Sudden Deceleration Detection

```python
class SuddenDeceleration:
    """Detect sudden braking/deceleration"""
    
    def __init__(self):
        self.speed_history = {}
        self.deceleration_threshold = 5  # km/h per frame
    
    def check_sudden_stop(self, vehicle_id, current_speed_kmh):
        """Detect sudden braking"""
        if vehicle_id not in self.speed_history:
            self.speed_history[vehicle_id] = []
        
        self.speed_history[vehicle_id].append(current_speed_kmh)
        
        if len(self.speed_history[vehicle_id]) >= 2:
            speed_change = self.speed_history[vehicle_id][-2] - current_speed_kmh
            
            if speed_change > self.deceleration_threshold:
                return {
                    'vehicle_id': vehicle_id,
                    'is_emergency_braking': True,
                    'speed_drop': speed_change,
                    'current_speed': current_speed_kmh,
                    'reason': 'Sudden braking detected - possible obstacle or emergency'
                }
        
        return None
```

---

## 3️⃣ QUICK ACCIDENT ANALYSIS & FORENSICS

### ✅ What to Use

**Best Approach: Post-Incident Data Extraction + Rule-Based Analysis**

### 🔧 Implementation - Accident Analysis Engine

```python
class AccidentAnalyzer:
    """
    Analyze accident quickly after it happens
    Extract key data for investigation
    """
    
    def __init__(self):
        self.incident_buffer = []
        self.buffer_size = 300  # Store 10 seconds at 30 FPS
    
    def store_frame_data(self, frame_data):
        """Store frame data for analysis"""
        self.incident_buffer.append({
            'timestamp': datetime.now(),
            'detections': frame_data,
            'vehicles_present': len(frame_data)
        })
        
        # Keep buffer size limited
        if len(self.incident_buffer) > self.buffer_size:
            self.incident_buffer.pop(0)
    
    def analyze_accident(self, accident_vehicle_ids):
        """
        Quickly analyze accident
        
        Returns:
            - What happened
            - Who was involved
            - Speed of vehicles
            - Position when accident occurred
            - Timeline of events
        """
        analysis = {
            'timestamp': datetime.now(),
            'vehicles_involved': accident_vehicle_ids,
            'detailed_analysis': [],
            'summary': ""
        }
        
        # Find frames containing all involved vehicles
        critical_frames = []
        for i, frame_data in enumerate(self.incident_buffer):
            frame_vehicles = [v.get('track_id') for v in frame_data['detections']]
            if all(vid in frame_vehicles for vid in accident_vehicle_ids):
                critical_frames.append(i)
        
        if not critical_frames:
            return analysis
        
        # Find frame just before accident (first collision frame)
        accident_frame_idx = critical_frames[0]
        
        # Get pre-accident data
        if accident_frame_idx > 0:
            pre_accident = self.incident_buffer[accident_frame_idx - 1]
            analysis['pre_accident_state'] = self._extract_vehicle_states(
                pre_accident['detections'],
                accident_vehicle_ids
            )
        
        # Get accident frame data
        accident_frame = self.incident_buffer[accident_frame_idx]
        analysis['accident_state'] = self._extract_vehicle_states(
            accident_frame['detections'],
            accident_vehicle_ids
        )
        
        # Get post-accident data
        if accident_frame_idx + 5 < len(self.incident_buffer):
            post_accident = self.incident_buffer[accident_frame_idx + 5]
            analysis['post_accident_state'] = self._extract_vehicle_states(
                post_accident['detections'],
                accident_vehicle_ids
            )
        
        # Generate summary
        analysis['summary'] = self._generate_summary(analysis)
        
        return analysis
    
    def _extract_vehicle_states(self, detections, vehicle_ids):
        """Extract state of specific vehicles"""
        states = {}
        for det in detections:
            if det.get('track_id') in vehicle_ids:
                states[det.get('track_id')] = {
                    'speed_kmh': det.get('speed_kmh', 0),
                    'position': det.get('center'),
                    'confidence': det.get('confidence'),
                    'class': det.get('class_name')
                }
        return states
    
    def _generate_summary(self, analysis):
        """Generate human-readable summary"""
        summary = "Accident Analysis Report\n"
        summary += "=" * 50 + "\n"
        
        if 'vehicles_involved' in analysis:
            summary += f"Vehicles Involved: {analysis['vehicles_involved']}\n"
        
        if 'accident_state' in analysis:
            summary += "\nAt Time of Accident:\n"
            for v_id, state in analysis['accident_state'].items():
                summary += f"  Vehicle {v_id}: {state['speed_kmh']:.1f} km/h at {state['position']}\n"
        
        return summary
    
    def generate_accident_report(self, accident_vehicle_ids):
        """Generate full accident report"""
        analysis = self.analyze_accident(accident_vehicle_ids)
        
        report = {
            'incident_id': f"INC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'recommendations': self._generate_recommendations(analysis)
        }
        
        return report
    
    def _generate_recommendations(self, analysis):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        if 'accident_state' in analysis:
            speeds = [s.get('speed_kmh', 0) for s in analysis['accident_state'].values()]
            if any(speed > 80 for speed in speeds):
                recommendations.append("Speeding was a factor")
        
        if len(analysis['vehicles_involved']) > 1:
            recommendations.append("Multi-vehicle collision")
        
        return recommendations
    
    def export_forensics(self, report, filepath='accident_report.json'):
        """Export forensic report"""
        import json
        with open(filepath, 'w') as f:
            # Convert datetime to string for JSON serialization
            json.dump(str(report), f, indent=2)
        return True
```

---

## 📊 COMPLETE INTEGRATION EXAMPLE

```python
class TrafficManagementSystem:
    """Complete system with all features"""
    
    def __init__(self):
        self.speed_analyzer = MultiVehicleSpeedAnalyzer()
        self.zone_analyzer = SpatialZoneAnalyzer()
        self.accident_predictor = AccidentPredictor()
        self.accident_analyzer = AccidentAnalyzer()
        self.emergency_manager = EmergencyServiceManager()
    
    def process_frame(self, frame, detections):
        """Process single frame with all analytics"""
        
        # 1. BATCH SPEED ANALYSIS
        speeding_batch, safe_vehicles = self.speed_analyzer.batch_analyze_speeds(detections)
        if speeding_batch:
            speed_alert = self.speed_analyzer.batch_alert_speeding(speeding_batch)
            logger.warning(f"Speeding Alert: {speed_alert}")
        
        # 2. ZONE ANALYSIS
        zone_alerts, zone_data = self.zone_analyzer.analyze_all_zones(detections)
        if zone_alerts:
            for alert in zone_alerts:
                logger.warning(f"Zone {alert['zone']}: {alert['speeding_count']} speeders")
        
        # 3. HEATMAP GENERATION
        heatmap_frame = generate_speeding_heatmap(frame, zone_data)
        
        # 4. ACCIDENT PREDICTION
        high_risk_pairs = self.accident_predictor.predict_accidents(detections)
        if high_risk_pairs:
            for pair in high_risk_pairs[:3]:  # Top 3 risks
                if pair['severity'] == 'CRITICAL':
                    logger.critical(f"COLLISION RISK: Vehicles {pair['vehicle1_id']} "
                                  f"and {pair['vehicle2_id']} - Risk: {pair['collision_risk']:.1%}")
                    self.emergency_manager.call_ambulance('COLLISION_RISK', details=pair)
        
        # 5. STORE FOR ANALYSIS
        self.accident_analyzer.store_frame_data(detections)
        
        return heatmap_frame
    
    def handle_accident(self, accident_vehicle_ids):
        """Handle actual accident"""
        # Call emergency services
        self.emergency_manager.handle_accident({
            'type': 'Multi-vehicle collision',
            'vehicle1_id': accident_vehicle_ids[0],
            'vehicle2_id': accident_vehicle_ids[1] if len(accident_vehicle_ids) > 1 else None,
            'center': (640, 360)
        })
        
        # Quick analysis
        report = self.accident_analyzer.generate_accident_report(accident_vehicle_ids)
        self.accident_analyzer.export_forensics(report)
        
        logger.critical(f"Accident Report: {report}")
```

---

## 🎯 SUMMARY TABLE

| Feature | Method | Purpose |
|---------|--------|---------|
| **Multiple Vehicles** | ByteTrack | Track many vehicles simultaneously |
| **Batch Alerts** | Zone Analysis | Alert on multiple speeders at once |
| **Heatmap** | Spatial Zones | Visualize speeding density |
| **Collision Risk** | Trajectory Prediction | Detect high-risk pairs |
| **Accident Prevention** | Velocity Analysis | Alert 1-2 seconds before collision |
| **Quick Analysis** | Post-Incident Buffer | Extract data quickly after accident |
| **Forensics** | Data Export | Generate investigation reports |

---

## 🚀 Quick Implementation

```bash
# Add to main.py
from accident_predictor import AccidentPredictor
from accident_analyzer import AccidentAnalyzer
from multi_vehicle_analyzer import MultiVehicleSpeedAnalyzer, SpatialZoneAnalyzer

# Create instances
accident_predictor = AccidentPredictor()
accident_analyzer = AccidentAnalyzer()
speed_analyzer = MultiVehicleSpeedAnalyzer()
zone_analyzer = SpatialZoneAnalyzer()

# In frame processing loop
predictions = accident_predictor.predict_accidents(detections)
zone_alerts, zone_data = zone_analyzer.analyze_all_zones(detections)
accident_analyzer.store_frame_data(detections)
```

**All systems work together to prevent and analyze accidents!** ✅
