# 🎯 TOP 3 PRIORITIES - Ready-to-Use Code

You asked "what should I add next?" - here's the answer with **working code you can copy-paste today**.

---

## Priority 1: VIDEO RECORDING 🎥

### Why: Save evidence of accidents & violations

**File: `src/incident_recorder.py`**

```python
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
    
    def start_recording(self, incident_type='accident', details=None):
        """
        Start recording incident
        
        Args:
            incident_type: 'accident', 'speeding', 'other'
            details: Dict with incident information
        """
        if self.is_recording:
            logger.warning("Already recording, stop first")
            return
        
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
                raise Exception("Failed to open video writer")
            
            self.is_recording = True
            self.frame_count = 0
            
            # Save metadata
            metadata = {
                'incident_type': incident_type,
                'start_time': datetime.now().isoformat(),
                'details': details or {},
                'frame_width': self.frame_width,
                'frame_height': self.frame_height,
                'fps': self.fps
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
            return
        
        try:
            self.current_video.release()
            self.is_recording = False
            
            logger.info(f"Stopped recording: {self.frame_count} frames saved")
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
            search_dirs = list(self.output_dir.glob('*'))
        else:
            search_dirs = [self.output_dir / incident_type]
        
        for d in search_dirs:
            if d.is_dir():
                for json_file in d.glob('*.json'):
                    with open(json_file, 'r') as f:
                        metadata = json.load(f)
                        video_file = json_file.with_suffix('.mp4')
                        if video_file.exists():
                            incidents.append({
                                'type': d.name,
                                'name': json_file.stem,
                                'video': str(video_file),
                                'metadata': metadata,
                                'file_size': video_file.stat().st_size
                            })
        
        return sorted(incidents, key=lambda x: x['metadata']['start_time'], reverse=True)
    
    def cleanup_old_incidents(self, days=30):
        """Delete incidents older than N days"""
        from datetime import timedelta
        import os
        
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for incident_file in self.output_dir.rglob('*.mp4'):
            file_time = datetime.fromtimestamp(incident_file.stat().st_mtime)
            if file_time < cutoff_date:
                incident_file.unlink()
                incident_file.with_suffix('.json').unlink(missing_ok=True)
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old incident files")
        return deleted_count
```

**Usage in main.py:**

```python
from src.incident_recorder import IncidentRecorder

# Initialize
recorder = IncidentRecorder(output_dir='incidents', frame_width=1280, frame_height=720)

# When accident detected
def handle_accident(accident_vehicles):
    recorder.start_recording(
        incident_type='accident',
        details={
            'vehicles': accident_vehicles,
            'location': 'NH-1 KM 25',
            'time': datetime.now().isoformat()
        }
    )

# In main loop
def process_frame(frame, detections):
    # ... detection code ...
    
    if is_accident:
        handle_accident(accident_vehicles)
    
    if recorder.is_recording:
        recorder.write_frame(frame)
    
    return frame

# When accident resolved
def accident_resolved():
    recorder.stop_recording()
    incidents = recorder.get_incident_list()
    print(f"Total recorded incidents: {len(incidents)}")

# Cleanup old incidents (run daily)
recorder.cleanup_old_incidents(days=30)
```

---

## Priority 2: DATABASE 💾

### Why: Store everything for dashboards, analysis, reports

**File: `src/traffic_database.py`**

```python
"""SQLite database for traffic events and statistics"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from src.logger import logger
import json


class TrafficDatabase:
    """
    SQLite database for storing all traffic events
    Includes vehicles, violations, accidents, and statistics
    """
    
    def __init__(self, db_path='traffic_data.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Vehicles table - log every detection
        c.execute('''CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            speed_kmh REAL,
            class_name TEXT,
            confidence REAL,
            position_x INTEGER,
            position_y INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Violations table - speeding, wrong-way, etc
        c.execute('''CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER,
            violation_type TEXT,
            speed_kmh REAL,
            speed_limit REAL,
            excess_speed REAL,
            location TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Accidents table - collision events
        c.execute('''CREATE TABLE IF NOT EXISTS accidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_ids TEXT,  -- JSON array
            accident_type TEXT,
            details TEXT,  -- JSON
            location TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Emergency calls table
        c.execute('''CREATE TABLE IF NOT EXISTS emergency_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_type TEXT,
            incident_type TEXT,
            details TEXT,  -- JSON
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # System statistics
        c.execute('''CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stat_date DATE UNIQUE,
            vehicles_detected INTEGER,
            avg_speed REAL,
            max_speed REAL,
            speeding_violations INTEGER,
            accidents INTEGER,
            emergency_calls INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def log_vehicle(self, track_id, speed_kmh, class_name, confidence, position=None):
        """Log detected vehicle"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            pos_x, pos_y = position if position else (0, 0)
            
            c.execute('''INSERT INTO vehicles 
                        (track_id, speed_kmh, class_name, confidence, position_x, position_y)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (track_id, speed_kmh, class_name, confidence, pos_x, pos_y))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging vehicle: {e}")
            return False
    
    def log_violation(self, vehicle_id, violation_type, speed_kmh, speed_limit=60, location='Unknown'):
        """Log speeding or other violation"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            excess = speed_kmh - speed_limit
            
            c.execute('''INSERT INTO violations 
                        (vehicle_id, violation_type, speed_kmh, speed_limit, excess_speed, location)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (vehicle_id, violation_type, speed_kmh, speed_limit, excess, location))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging violation: {e}")
            return False
    
    def log_accident(self, vehicle_ids, accident_type, details, location='Unknown'):
        """Log accident"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO accidents 
                        (vehicle_ids, accident_type, details, location)
                        VALUES (?, ?, ?, ?)''',
                     (json.dumps(vehicle_ids), accident_type, json.dumps(details), location))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging accident: {e}")
            return False
    
    def log_emergency_call(self, service_type, incident_type, details):
        """Log emergency service call"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO emergency_calls 
                        (service_type, incident_type, details)
                        VALUES (?, ?, ?)''',
                     (service_type, incident_type, json.dumps(details)))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging emergency call: {e}")
            return False
    
    def get_todays_statistics(self):
        """Get statistics for today"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            today = datetime.now().date()
            
            # Vehicles detected
            vehicles = c.execute(
                'SELECT COUNT(DISTINCT track_id) FROM vehicles WHERE DATE(timestamp) = ?',
                (today,)
            ).fetchone()[0]
            
            # Violations
            violations = c.execute(
                'SELECT COUNT(*) FROM violations WHERE DATE(timestamp) = ?',
                (today,)
            ).fetchone()[0]
            
            # Accidents
            accidents = c.execute(
                'SELECT COUNT(*) FROM accidents WHERE DATE(timestamp) = ?',
                (today,)
            ).fetchone()[0]
            
            # Emergency calls
            calls = c.execute(
                'SELECT COUNT(*) FROM emergency_calls WHERE DATE(timestamp) = ?',
                (today,)
            ).fetchone()[0]
            
            # Average speed
            avg_speed_row = c.execute(
                'SELECT AVG(speed_kmh) FROM vehicles WHERE DATE(timestamp) = ?',
                (today,)
            ).fetchone()
            avg_speed = avg_speed_row[0] if avg_speed_row[0] else 0
            
            # Max speed
            max_speed_row = c.execute(
                'SELECT MAX(speed_kmh) FROM vehicles WHERE DATE(timestamp) = ?',
                (today,)
            ).fetchone()
            max_speed = max_speed_row[0] if max_speed_row[0] else 0
            
            conn.close()
            
            return {
                'date': today.isoformat(),
                'vehicles_detected': vehicles,
                'avg_speed_kmh': round(avg_speed, 1),
                'max_speed_kmh': round(max_speed, 1),
                'speeding_violations': violations,
                'accidents': accidents,
                'emergency_calls': calls
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def get_violations_today(self):
        """Get today's violations"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            today = datetime.now().date()
            
            c.execute('''SELECT * FROM violations 
                        WHERE DATE(timestamp) = ? 
                        ORDER BY timestamp DESC
                        LIMIT 50''', (today,))
            
            violations = [dict(row) for row in c.fetchall()]
            conn.close()
            return violations
        except Exception as e:
            logger.error(f"Error getting violations: {e}")
            return []
    
    def get_top_violators(self, days=1):
        """Get vehicles with most violations"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            cutoff_date = (datetime.now() - timedelta(days=days)).date()
            
            c.execute('''SELECT vehicle_id, COUNT(*) as count, AVG(excess_speed) as avg_excess
                        FROM violations 
                        WHERE DATE(timestamp) >= ?
                        GROUP BY vehicle_id
                        ORDER BY count DESC
                        LIMIT 10''', (cutoff_date,))
            
            violators = [{'vehicle_id': row[0], 'violations': row[1], 'avg_excess': row[2]}
                        for row in c.fetchall()]
            conn.close()
            return violators
        except Exception as e:
            logger.error(f"Error getting top violators: {e}")
            return []
    
    def get_vehicle_history(self, vehicle_id, limit=100):
        """Get history for specific vehicle"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('''SELECT * FROM vehicles WHERE track_id = ? ORDER BY timestamp DESC LIMIT ?''',
                     (vehicle_id, limit))
            
            history = [dict(row) for row in c.fetchall()]
            conn.close()
            return history
        except Exception as e:
            logger.error(f"Error getting vehicle history: {e}")
            return []
    
    def export_daily_report(self, export_path='daily_report.json'):
        """Export daily statistics to JSON"""
        try:
            stats = self.get_todays_statistics()
            violations = self.get_violations_today()
            top_violators = self.get_top_violators()
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'statistics': stats,
                'recent_violations': violations[:20],
                'top_violators': top_violators
            }
            
            with open(export_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Report exported to {export_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            return False
```

**Usage in main.py:**

```python
from src.traffic_database import TrafficDatabase

# Initialize
db = TrafficDatabase('traffic_data.db')

# In frame processing loop
def process_detections(detections):
    for det in detections:
        vehicle_id = det['track_id']
        speed = det['speed_kmh']
        class_name = det['class_name']
        
        # Log every vehicle
        db.log_vehicle(vehicle_id, speed, class_name, det['confidence'], det['center'])
        
        # Log violations
        if speed > 80:  # Speeding threshold
            db.log_violation(vehicle_id, 'SPEEDING', speed, speed_limit=60)

# Get statistics
stats = db.get_todays_statistics()
print(f"Today: {stats['vehicles_detected']} vehicles, "
      f"{stats['speeding_violations']} violations")

# Get top violators
violators = db.get_top_violators(days=1)
print(f"Top violators: {violators}")

# Export report
db.export_daily_report('traffic_report_today.json')
```

---

## Priority 3: WEB DASHBOARD 📊

### Why: Monitor from any device (phone, tablet, PC)

**File: `dashboard_app.py`** (Flask web server)

```python
"""
Web Dashboard - Monitor system from browser
Access at: http://localhost:5000
"""

from flask import Flask, render_template, jsonify
from src.traffic_database import TrafficDatabase
import threading
import json

app = Flask(__name__)
db = TrafficDatabase()

# Store latest detections for live feed
latest_detections = []
latest_frame = None

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get today's statistics"""
    return jsonify(db.get_todays_statistics())

@app.route('/api/violations')
def get_violations():
    """Get today's violations"""
    return jsonify(db.get_violations_today())

@app.route('/api/top-violators')
def get_top_violators():
    """Get top violators"""
    return jsonify(db.get_top_violators(days=7))

@app.route('/api/vehicle/<int:vehicle_id>')
def get_vehicle_info(vehicle_id):
    """Get specific vehicle history"""
    return jsonify(db.get_vehicle_history(vehicle_id))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**File: `templates/dashboard.html`**

```html
<!DOCTYPE html>
<html>
<head>
    <title>Traffic Management Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1a1a1a; color: #fff; }
        .container { padding: 20px; max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-box {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ff6b6b;
        }
        .stat-box h3 { margin-bottom: 10px; }
        .stat-value { font-size: 28px; font-weight: bold; color: #4ecdc4; }
        .stat-label { font-size: 14px; color: #aaa; }
        .violations-list {
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            max-height: 400px;
            overflow-y: auto;
        }
        .violation-item {
            background: #1a1a1a;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            border-left: 3px solid #ff6b6b;
        }
        .critical { background-color: rgba(255, 107, 107, 0.1); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Traffic Management System</h1>
            <p id="update-time">Loading...</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-box">
                <h3>🚗 Vehicles Detected</h3>
                <div class="stat-value" id="vehicles-count">0</div>
                <div class="stat-label">Today</div>
            </div>
            
            <div class="stat-box">
                <h3>📊 Avg Speed</h3>
                <div class="stat-value" id="avg-speed">0</div>
                <div class="stat-label">km/h</div>
            </div>
            
            <div class="stat-box">
                <h3>⬆️ Max Speed</h3>
                <div class="stat-value" id="max-speed">0</div>
                <div class="stat-label">km/h</div>
            </div>
            
            <div class="stat-box" style="border-left-color: #ff6b6b;">
                <h3>⚠️ Speeding Violations</h3>
                <div class="stat-value" id="violations-count">0</div>
                <div class="stat-label">Today</div>
            </div>
            
            <div class="stat-box" style="border-left-color: #feca57;">
                <h3>🚨 Accidents</h3>
                <div class="stat-value" id="accidents-count">0</div>
                <div class="stat-label">Today</div>
            </div>
            
            <div class="stat-box" style="border-left-color: #48dbfb;">
                <h3>📞 Emergency Calls</h3>
                <div class="stat-value" id="calls-count">0</div>
                <div class="stat-label">Today</div>
            </div>
        </div>
        
        <div class="violations-list">
            <h2>Recent Violations (Last 24h)</h2>
            <div id="violations-container"></div>
        </div>
    </div>
    
    <script>
        // Update dashboard every 5 seconds
        setInterval(updateDashboard, 5000);
        updateDashboard();
        
        async function updateDashboard() {
            try {
                // Get statistics
                const statsRes = await fetch('/api/stats');
                const stats = await statsRes.json();
                
                document.getElementById('vehicles-count').textContent = stats.vehicles_detected || '0';
                document.getElementById('avg-speed').textContent = stats.avg_speed_kmh || '0';
                document.getElementById('max-speed').textContent = stats.max_speed_kmh || '0';
                document.getElementById('violations-count').textContent = stats.speeding_violations || '0';
                document.getElementById('accidents-count').textContent = stats.accidents || '0';
                document.getElementById('calls-count').textContent = stats.emergency_calls || '0';
                
                // Get violations
                const violRes = await fetch('/api/violations');
                const violations = await violRes.json();
                
                const container = document.getElementById('violations-container');
                container.innerHTML = '';
                
                violations.slice(0, 20).forEach(v => {
                    const item = document.createElement('div');
                    item.className = `violation-item ${v.excess_speed > 20 ? 'critical' : ''}`;
                    item.innerHTML = `
                        <strong>Vehicle ${v.vehicle_id}</strong> - ${v.speed_kmh.toFixed(1)} km/h 
                        (Excess: +${v.excess_speed.toFixed(1)} km/h)
                        <small>${v.timestamp}</small>
                    `;
                    container.appendChild(item);
                });
                
                document.getElementById('update-time').textContent = new Date().toLocaleString();
            } catch (e) {
                console.error('Update error:', e);
            }
        }
    </script>
</body>
</html>
```

**To use:**

1. Save as `dashboard_app.py` in project root
2. Create `templates/` directory
3. Save HTML as `templates/dashboard.html`
4. Run: `python dashboard_app.py`
5. Open browser: `http://localhost:5000`

---

## 🚀 Next Steps (Pick One)

```bash
# 1. Add Recording
cp src/incident_recorder.py to your src/

# 2. Add Database  
cp src/traffic_database.py to your src/

# 3. Add Dashboard
cp dashboard_app.py to your root/
mkdir templates/
# Save HTML to templates/dashboard.html
```

Then integrate into `main.py`:

```python
# Add at top
from src.incident_recorder import IncidentRecorder
from src.traffic_database import TrafficDatabase

# Initialize
recorder = IncidentRecorder()
db = TrafficDatabase()

# In frame loop
db.log_vehicle(...)
recorder.write_frame(...)
```

**Start with whichever matters most to you!**
