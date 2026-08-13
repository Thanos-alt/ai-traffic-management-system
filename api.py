"""REST API for Traffic Management System (Optional)"""

from flask import Flask, jsonify, render_template
from datetime import datetime
import json
from pathlib import Path

app = Flask(__name__)

# Global state (in production, use a database)
traffic_state = {
    "current_vehicles": 0,
    "traffic_level": "LOW",
    "density": 0.0,
    "hsr_status": "OPEN",
    "last_update": datetime.now().isoformat(),
    "cameras": {}
}

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current traffic status"""
    return jsonify(traffic_state)

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get traffic history"""
    history_file = Path("logs") / "traffic_history.json"
    if history_file.exists():
        with open(history_file, 'r') as f:
            history = json.load(f)
        return jsonify(history)
    return jsonify([])

@app.route('/api/hsr', methods=['GET'])
def get_hsr_status():
    """Get HSR status"""
    return jsonify({
        "status": traffic_state["hsr_status"],
        "last_change": traffic_state["last_update"]
    })

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    """Get camera information"""
    return jsonify(traffic_state["cameras"])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Serve dashboard HTML"""
    return render_template('dashboard.html')

if __name__ == '__main__':
    print("Starting Traffic Management API...")
    print("API available at http://localhost:5000")
    print("Dashboard at http://localhost:5000/dashboard")
    app.run(debug=True, host='0.0.0.0', port=5000)
