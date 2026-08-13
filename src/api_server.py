"""
Traffic Management API Integration

This module integrates the Flask API with the main traffic detection system.
"""

from flask import Flask
from threading import Thread
from datetime import datetime
from src.logger import logger

class APIServer:
    """Manages Flask API server"""
    
    def __init__(self, port=5000):
        self.port = port
        self.app = Flask(__name__)
        self.thread = None
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/api/status')
        def status():
            return {
                "status": "running",
                "timestamp": str(datetime.now())
            }
        
        @self.app.route('/api/health')
        def health():
            return {"status": "healthy"}
    
    def start(self):
        """Start API server in background thread"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self._run, daemon=True)
            self.thread.start()
            logger.info(f"API server started on port {self.port}")
    
    def _run(self):
        """Run Flask app"""
        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        except Exception as e:
            logger.error(f"API server error: {e}")
    
    def stop(self):
        """Stop API server"""
        logger.info("Stopping API server")
