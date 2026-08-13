"""Alert system for traffic incidents"""

from datetime import datetime
from config.config import (
    HIGH_TRAFFIC_MESSAGE, INCIDENT_MESSAGE, NORMAL_TRAFFIC_MESSAGE
)
from src.logger import logger

class AlertManager:
    """Manages and triggers alerts"""
    
    def __init__(self):
        self.active_alerts = {}
        self.alert_history = []
        self.alert_cooldown = {}
    
    def create_alert(self, alert_type: str, severity: str, message: str, 
                    data: dict = None) -> dict:
        """Create and log an alert"""
        alert = {
            "id": len(self.alert_history) + 1,
            "timestamp": datetime.now(),
            "type": alert_type,
            "severity": severity,  # LOW, MEDIUM, HIGH, CRITICAL
            "message": message,
            "data": data or {},
            "status": "ACTIVE"
        }
        
        self.alert_history.append(alert)
        self.active_alerts[alert["id"]] = alert
        
        # Log alert
        log_level = "warning" if severity in ["HIGH", "CRITICAL"] else "info"
        getattr(logger, log_level)(f"[ALERT] {alert_type}: {message} (Severity: {severity})")
        
        return alert
    
    def high_traffic_alert(self, location: str, vehicle_count: int, density: float):
        """Create high traffic alert"""
        message = f"High traffic detected at {location}: {vehicle_count} vehicles, {density:.1%} density"
        return self.create_alert(
            alert_type="HIGH_TRAFFIC",
            severity="HIGH",
            message=message,
            data={"location": location, "vehicles": vehicle_count, "density": density}
        )
    
    def incident_alert(self, incident_type: str, location: str, description: str = ""):
        """Create incident alert"""
        message = f"{incident_type} at {location}"
        if description:
            message += f": {description}"
        return self.create_alert(
            alert_type="INCIDENT",
            severity="CRITICAL",
            message=message,
            data={"incident_type": incident_type, "location": location, "description": description}
        )
    
    def lane_closure_alert(self, lane: str, reason: str = ""):
        """Create lane closure alert"""
        message = f"Lane {lane} is closing"
        if reason:
            message += f" - {reason}"
        return self.create_alert(
            alert_type="LANE_CLOSURE",
            severity="HIGH",
            message=message,
            data={"lane": lane, "reason": reason}
        )
    
    def hsr_status_alert(self, status: str, occupancy: float):
        """Create HSR status alert"""
        message = f"HSR Status: {status} (Occupancy: {occupancy:.1%})"
        severity = "CRITICAL" if status == "CLOSED" else "HIGH"
        return self.create_alert(
            alert_type="HSR_STATUS",
            severity=severity,
            message=message,
            data={"status": status, "occupancy": occupancy}
        )
    
    def normal_traffic_alert(self, location: str):
        """Create normal traffic alert"""
        message = f"Traffic flow normalized at {location}"
        return self.create_alert(
            alert_type="NORMAL_TRAFFIC",
            severity="LOW",
            message=message,
            data={"location": location}
        )
    
    def accident_alert(self, location: str, severity_level: str = "MODERATE"):
        """Create accident alert"""
        message = f"Traffic accident detected at {location} - Severity: {severity_level}"
        return self.create_alert(
            alert_type="ACCIDENT",
            severity="CRITICAL",
            message=message,
            data={"location": location, "severity": severity_level}
        )
    
    def congestion_building_alert(self, location: str, trend: str):
        """Create congestion building alert"""
        message = f"Traffic congestion building at {location} - Trend: {trend}"
        severity = "HIGH" if trend == "INCREASING" else "MEDIUM"
        return self.create_alert(
            alert_type="CONGESTION_BUILDING",
            severity=severity,
            message=message,
            data={"location": location, "trend": trend}
        )
    
    def resolve_alert(self, alert_id: int):
        """Mark alert as resolved"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert["status"] = "RESOLVED"
            alert["resolved_at"] = datetime.now()
            del self.active_alerts[alert_id]
            logger.info(f"Alert #{alert_id} resolved: {alert['message']}")
            return True
        return False
    
    def get_active_alerts(self) -> list:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_critical_alerts(self) -> list:
        """Get only critical alerts"""
        return [a for a in self.get_active_alerts() if a["severity"] == "CRITICAL"]
    
    def get_alert_history(self, limit: int = 50) -> list:
        """Get alert history"""
        return self.alert_history[-limit:]
    
    def clear_resolved_alerts(self):
        """Clear resolved alerts from history"""
        self.alert_history = [a for a in self.alert_history if a.get("status") != "RESOLVED"]
    
    def get_alert_stats(self) -> dict:
        """Get alert statistics"""
        total = len(self.alert_history)
        by_type = {}
        by_severity = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        for alert in self.alert_history:
            alert_type = alert["type"]
            severity = alert["severity"]
            
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            by_severity[severity] += 1
        
        return {
            "total_alerts": total,
            "active_alerts": len(self.active_alerts),
            "by_type": by_type,
            "by_severity": by_severity
        }
