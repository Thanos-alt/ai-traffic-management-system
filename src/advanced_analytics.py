"""
Accident Prediction & Multi-Vehicle Analysis System
Ready-to-use module for detecting accidents before they happen
"""

import numpy as np
import cv2
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
from src.logger import logger


class AccidentPredictionEngine:
    """
    Real-time accident prediction system
    Predicts collisions 1-2 seconds before they happen
    """
    
    def __init__(self, prediction_horizon_frames=30, collision_distance_pixels=50):
        """
        Initialize prediction engine
        
        Args:
            prediction_horizon_frames: Predict this many frames ahead (~1 second at 30 FPS)
            collision_distance_pixels: Distance threshold for collision detection
        """
        self.prediction_horizon = prediction_horizon_frames
        self.collision_distance = collision_distance_pixels
        
        # Vehicle tracking
        self.vehicle_trajectories = {}
        self.vehicle_velocities = {}
        self.vehicle_accelerations = {}
        self.trajectory_history_length = 15  # Keep 15 frames history
        
        # Collision data
        self.collision_warnings = {}
        self.predicted_collisions = []
        
    def update_vehicle(self, vehicle_id: int, position: Tuple[float, float], 
                       speed_kmh: float, frame_time: float = None):
        """
        Update vehicle position and calculate dynamics
        
        Args:
            vehicle_id: Unique vehicle identifier
            position: (x, y) position in frame
            speed_kmh: Speed in km/h
            frame_time: Timestamp (auto if None)
        """
        if frame_time is None:
            frame_time = time.time()
        
        # Initialize trajectory if needed
        if vehicle_id not in self.vehicle_trajectories:
            self.vehicle_trajectories[vehicle_id] = []
            self.vehicle_velocities[vehicle_id] = (0, 0)
            self.vehicle_accelerations[vehicle_id] = (0, 0)
        
        # Add to trajectory
        trajectory_point = {
            'position': position,
            'speed_kmh': speed_kmh,
            'time': frame_time
        }
        self.vehicle_trajectories[vehicle_id].append(trajectory_point)
        
        # Keep trajectory limited
        if len(self.vehicle_trajectories[vehicle_id]) > self.trajectory_history_length:
            self.vehicle_trajectories[vehicle_id].pop(0)
        
        # Calculate velocity if we have enough history
        if len(self.vehicle_trajectories[vehicle_id]) >= 3:
            self._calculate_velocity(vehicle_id)
            self._calculate_acceleration(vehicle_id)
    
    def _calculate_velocity(self, vehicle_id: int):
        """Calculate velocity vector"""
        traj = self.vehicle_trajectories[vehicle_id]
        
        if len(traj) >= 2:
            prev = traj[-2]
            curr = traj[-1]
            
            dx = curr['position'][0] - prev['position'][0]
            dy = curr['position'][1] - prev['position'][1]
            
            self.vehicle_velocities[vehicle_id] = (dx, dy)
    
    def _calculate_acceleration(self, vehicle_id: int):
        """Calculate acceleration vector"""
        if vehicle_id not in self.vehicle_velocities:
            return
        
        traj = self.vehicle_trajectories[vehicle_id]
        
        if len(traj) >= 3:
            # Get velocity at t-1 and t
            prev_pos = traj[-2]['position']
            prev_prev_pos = traj[-3]['position']
            curr_pos = traj[-1]['position']
            
            # Velocity at t-1
            vx1 = prev_pos[0] - prev_prev_pos[0]
            vy1 = prev_pos[1] - prev_prev_pos[1]
            
            # Velocity at t
            vx2 = curr_pos[0] - prev_pos[0]
            vy2 = curr_pos[1] - prev_pos[1]
            
            # Acceleration
            ax = vx2 - vx1
            ay = vy2 - vy1
            
            self.vehicle_accelerations[vehicle_id] = (ax, ay)
    
    def predict_future_position(self, vehicle_id: int, frames_ahead: int) -> Optional[Tuple[float, float]]:
        """
        Predict vehicle position N frames ahead using constant acceleration model
        """
        if vehicle_id not in self.vehicle_trajectories:
            return None
        
        traj = self.vehicle_trajectories[vehicle_id]
        if len(traj) == 0:
            return None
        
        current_pos = traj[-1]['position']
        velocity = self.vehicle_velocities.get(vehicle_id, (0, 0))
        acceleration = self.vehicle_accelerations.get(vehicle_id, (0, 0))
        
        # Physics: x = x0 + v*t + 0.5*a*t^2
        predicted_x = current_pos[0] + velocity[0] * frames_ahead + 0.5 * acceleration[0] * (frames_ahead ** 2)
        predicted_y = current_pos[1] + velocity[1] * frames_ahead + 0.5 * acceleration[1] * (frames_ahead ** 2)
        
        return (predicted_x, predicted_y)
    
    def calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
    
    def predict_collision_risk(self, vehicle_id1: int, vehicle_id2: int) -> Dict:
        """
        Calculate collision risk between two vehicles
        
        Returns:
            risk_info: {
                'vehicle1_id': id1,
                'vehicle2_id': id2,
                'current_distance': float,
                'predicted_distance': float,
                'risk_score': 0-1,
                'time_to_collision_frames': int or None,
                'severity': 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'SAFE'
            }
        """
        # Get current positions
        if vehicle_id1 not in self.vehicle_trajectories or vehicle_id2 not in self.vehicle_trajectories:
            return None
        
        traj1 = self.vehicle_trajectories[vehicle_id1]
        traj2 = self.vehicle_trajectories[vehicle_id2]
        
        if len(traj1) == 0 or len(traj2) == 0:
            return None
        
        pos1_current = traj1[-1]['position']
        pos2_current = traj2[-1]['position']
        
        # Get predicted positions
        pos1_predicted = self.predict_future_position(vehicle_id1, self.prediction_horizon)
        pos2_predicted = self.predict_future_position(vehicle_id2, self.prediction_horizon)
        
        if pos1_predicted is None or pos2_predicted is None:
            return None
        
        # Calculate distances
        current_distance = self.calculate_distance(pos1_current, pos2_current)
        predicted_distance = self.calculate_distance(pos1_predicted, pos2_predicted)
        
        # Determine if vehicles are approaching
        is_approaching = predicted_distance < current_distance
        
        # Calculate risk score
        if predicted_distance < self.collision_distance:
            risk_score = max(0, 1.0 - (predicted_distance / self.collision_distance))
            time_to_collision = self.prediction_horizon
        else:
            if is_approaching:
                distance_reduction = current_distance - predicted_distance
                risk_score = min(0.5, distance_reduction / 100)
                time_to_collision = self.prediction_horizon
            else:
                risk_score = 0.0
                time_to_collision = None
        
        # Determine severity
        if risk_score > 0.7:
            severity = 'CRITICAL'
        elif risk_score > 0.5:
            severity = 'HIGH'
        elif risk_score > 0.25:
            severity = 'MEDIUM'
        elif is_approaching:
            severity = 'LOW'
        else:
            severity = 'SAFE'
        
        return {
            'vehicle1_id': vehicle_id1,
            'vehicle2_id': vehicle_id2,
            'current_distance': current_distance,
            'predicted_distance': predicted_distance,
            'distance_reduction': current_distance - predicted_distance if is_approaching else 0,
            'risk_score': risk_score,
            'time_to_collision_frames': time_to_collision,
            'severity': severity,
            'is_approaching': is_approaching
        }
    
    def predict_all_collisions(self, detections: List[Dict]) -> List[Dict]:
        """
        Check all vehicle pairs for collision risk
        
        Args:
            detections: List of vehicle detections with positions
            
        Returns:
            List of high-risk pairs sorted by risk
        """
        # Update all vehicles
        for det in detections:
            vehicle_id = det.get('track_id')
            position = det.get('center')
            speed = det.get('speed_kmh', 0)
            
            if vehicle_id is not None and position is not None:
                self.update_vehicle(vehicle_id, position, speed)
        
        # Check all pairs
        high_risk_pairs = []
        vehicle_ids = [det.get('track_id') for det in detections if det.get('track_id') is not None]
        
        for i in range(len(vehicle_ids)):
            for j in range(i + 1, len(vehicle_ids)):
                v1_id = vehicle_ids[i]
                v2_id = vehicle_ids[j]
                
                risk_info = self.predict_collision_risk(v1_id, v2_id)
                
                if risk_info and risk_info['risk_score'] > 0.2:  # 20% threshold
                    high_risk_pairs.append(risk_info)
        
        # Sort by risk
        return sorted(high_risk_pairs, key=lambda x: x['risk_score'], reverse=True)
    
    def draw_collision_predictions(self, frame: np.ndarray, high_risk_pairs: List[Dict]) -> np.ndarray:
        """
        Draw collision predictions on frame (lines between vehicles, risk indicators)
        """
        for risk_info in high_risk_pairs[:5]:  # Show top 5 risks
            v1_id = risk_info['vehicle1_id']
            v2_id = risk_info['vehicle2_id']
            risk_score = risk_info['risk_score']
            severity = risk_info['severity']
            
            # Get vehicle positions
            if v1_id in self.vehicle_trajectories and v2_id in self.vehicle_trajectories:
                pos1 = self.vehicle_trajectories[v1_id][-1]['position']
                pos2 = self.vehicle_trajectories[v2_id][-1]['position']
                
                # Color based on severity
                if severity == 'CRITICAL':
                    color = (0, 0, 255)      # Red
                    thickness = 3
                elif severity == 'HIGH':
                    color = (0, 165, 255)    # Orange
                    thickness = 2
                else:
                    color = (0, 255, 255)    # Yellow
                    thickness = 1
                
                # Draw line between vehicles
                cv2.line(frame, tuple(map(int, pos1)), tuple(map(int, pos2)), color, thickness)
                
                # Draw warning circle
                cv2.circle(frame, tuple(map(int, pos1)), 15, color, 2)
                cv2.circle(frame, tuple(map(int, pos2)), 15, color, 2)
                
                # Draw risk text
                mid_point = ((pos1[0] + pos2[0]) / 2, (pos1[1] + pos2[1]) / 2)
                risk_text = f"{severity} {risk_score:.0%}"
                cv2.putText(frame, risk_text, tuple(map(int, mid_point)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        return frame


class BatchSpeedAnalyzer:
    """
    Batch process multiple speeding vehicles
    More efficient than individual alerts
    """
    
    def __init__(self, speed_limit_kmh: int = 60):
        self.speed_limit = speed_limit_kmh
        self.speeding_history = defaultdict(list)
        self.zone_stats = {}
    
    def analyze_batch(self, detections: List[Dict]) -> Dict:
        """
        Analyze all vehicles in one go
        
        Returns speeding statistics and violations
        """
        speeding_vehicles = []
        safe_vehicles = []
        critical_speeders = []
        
        for det in detections:
            vehicle_id = det.get('track_id')
            speed = det.get('speed_kmh', 0)
            
            if speed > self.speed_limit:
                excess = speed - self.speed_limit
                speeding_vehicles.append({
                    'vehicle_id': vehicle_id,
                    'speed': speed,
                    'excess': excess,
                    'position': det.get('center'),
                    'confidence': det.get('confidence'),
                    'class': det.get('class_name')
                })
                
                # Track critical speeders (30+ over limit)
                if excess >= 30:
                    critical_speeders.append(vehicle_id)
                else:
                    self.speeding_history[vehicle_id].append(speed)
            else:
                safe_vehicles.append(vehicle_id)
        
        # Calculate batch statistics
        stats = {
            'total_vehicles': len(detections),
            'speeding_count': len(speeding_vehicles),
            'safe_count': len(safe_vehicles),
            'critical_count': len(critical_speeders),
            'avg_speeding': np.mean([v['speed'] for v in speeding_vehicles]) if speeding_vehicles else 0,
            'max_speed': max([v['speed'] for v in speeding_vehicles]) if speeding_vehicles else 0,
            'min_speed_speeding': min([v['speed'] for v in speeding_vehicles]) if speeding_vehicles else 0,
            'speeding_percentage': (len(speeding_vehicles) / len(detections) * 100) if detections else 0,
            'violations': speeding_vehicles,
            'critical_violators': critical_speeders
        }
        
        return stats
    
    def get_summary_alert(self, stats: Dict) -> Optional[str]:
        """Generate single batch alert instead of multiple individual alerts"""
        if stats['speeding_count'] == 0:
            return None
        
        if stats['critical_count'] > 0:
            return (f"🚨 CRITICAL: {stats['critical_count']} vehicles exceeding limit by 30+ km/h. "
                   f"Call police immediately!")
        elif stats['speeding_percentage'] > 50:
            return (f"⚠️ WARNING: {stats['speeding_count']}/{stats['total_vehicles']} vehicles speeding. "
                   f"Max speed: {stats['max_speed']:.1f} km/h")
        else:
            return (f"📊 {stats['speeding_count']} speeding violations detected. "
                   f"Average excess: {stats['avg_speeding'] - self.speed_limit:.1f} km/h")


class PostIncidentAnalyzer:
    """
    Quick analysis of accidents after they occur
    Extract key information for investigation
    """
    
    def __init__(self, buffer_frames: int = 300):  # 10 seconds at 30 FPS
        self.frame_buffer = []
        self.buffer_frames = buffer_frames
    
    def store_frame(self, frame_data: Dict):
        """Store frame data"""
        self.frame_buffer.append({
            'timestamp': datetime.now(),
            'data': frame_data
        })
        
        # Keep buffer limited
        if len(self.frame_buffer) > self.buffer_frames:
            self.frame_buffer.pop(0)
    
    def analyze_incident(self, incident_vehicle_ids: List[int]) -> Dict:
        """
        Analyze incident involving specific vehicles
        Look at what happened before, during, and after
        """
        analysis = {
            'incident_time': datetime.now(),
            'vehicles_involved': incident_vehicle_ids,
            'timeline': {
                'pre_incident': None,
                'at_incident': None,
                'post_incident': None
            },
            'findings': [],
            'recommendations': []
        }
        
        # Find frames when all vehicles were visible
        incident_frames = []
        for i, frame_data in enumerate(self.frame_buffer):
            vehicles_in_frame = [v.get('track_id') for v in frame_data['data']]
            if all(vid in vehicles_in_frame for vid in incident_vehicle_ids):
                incident_frames.append(i)
        
        if not incident_frames:
            analysis['findings'].append("Incomplete data - not all vehicles visible in buffer")
            return analysis
        
        # Analyze frames
        first_incident_frame = incident_frames[0]
        
        # Pre-incident (5 frames before)
        if first_incident_frame >= 5:
            pre_frame = self.frame_buffer[first_incident_frame - 5]
            analysis['timeline']['pre_incident'] = self._extract_vehicle_info(
                pre_frame['data'], incident_vehicle_ids
            )
        
        # At incident
        incident_frame = self.frame_buffer[first_incident_frame]
        analysis['timeline']['at_incident'] = self._extract_vehicle_info(
            incident_frame['data'], incident_vehicle_ids
        )
        
        # Post-incident (5 frames after)
        if first_incident_frame + 5 < len(self.frame_buffer):
            post_frame = self.frame_buffer[first_incident_frame + 5]
            analysis['timeline']['post_incident'] = self._extract_vehicle_info(
                post_frame['data'], incident_vehicle_ids
            )
        
        # Generate findings
        analysis['findings'] = self._generate_findings(analysis)
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _extract_vehicle_info(self, detections: List[Dict], vehicle_ids: List[int]) -> Dict:
        """Extract info for specific vehicles"""
        info = {}
        for det in detections:
            if det.get('track_id') in vehicle_ids:
                info[det.get('track_id')] = {
                    'speed_kmh': det.get('speed_kmh', 0),
                    'position': det.get('center'),
                    'class': det.get('class_name'),
                    'confidence': det.get('confidence')
                }
        return info
    
    def _generate_findings(self, analysis: Dict) -> List[str]:
        """Generate findings from analysis"""
        findings = []
        
        if analysis['timeline']['at_incident']:
            speeds = [v['speed_kmh'] for v in analysis['timeline']['at_incident'].values()]
            if any(s > 80 for s in speeds):
                findings.append(f"Speeding detected at incident: {max(speeds):.1f} km/h")
            if min(speeds) < 5:
                findings.append("Vehicle braking hard - possible emergency stop")
        
        return findings
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        if len(analysis['vehicles_involved']) > 1:
            recommendations.append("Multi-vehicle collision - investigate all vehicles")
        
        if analysis['findings']:
            recommendations.append("Focus investigation on vehicles showing abnormal behavior")
        
        recommendations.append("Review video footage frame-by-frame")
        
        return recommendations
    
    def export_analysis(self, analysis: Dict, filepath: str = 'incident_analysis.json') -> bool:
        """Export analysis to file"""
        import json
        try:
            # Convert non-serializable objects
            analysis_copy = analysis.copy()
            analysis_copy['incident_time'] = analysis_copy['incident_time'].isoformat()
            
            with open(filepath, 'w') as f:
                json.dump(analysis_copy, f, indent=2)
            
            logger.info(f"Incident analysis exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export analysis: {e}")
            return False


# Convenience functions
def create_accident_prediction_system():
    """Create and return all analysis systems"""
    return {
        'prediction': AccidentPredictionEngine(),
        'speed_batch': BatchSpeedAnalyzer(),
        'post_incident': PostIncidentAnalyzer()
    }
