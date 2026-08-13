"""Traffic signal management system"""

import time
from src.logger import logger


class TrafficSignalManager:
    """Manages traffic signals for each lane"""
    
    # Signal states
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    
    # Signal colors in BGR
    SIGNAL_COLORS = {
        "GREEN": (0, 255, 0),
        "YELLOW": (0, 255, 255),
        "RED": (0, 0, 255),
        "EMERGENCY": (255, 0, 255)  # Magenta for emergency
    }
    
    def __init__(self, num_lanes=2, green_phase=30, yellow_phase=5):
        """
        Initialize traffic signal manager
        
        Args:
            num_lanes: Number of lanes
            green_phase: Duration of green signal in seconds
            yellow_phase: Duration of yellow signal in seconds
        """
        self.num_lanes = num_lanes
        self.green_phase = green_phase
        self.yellow_phase = yellow_phase
        
        # Initialize signal states
        self.signals = {}
        self.signal_start_time = {}
        self.emergency_active = False
        self.emergency_lane = None
        self.emergency_start_time = None
        self.emergency_duration = 60  # Emergency signal lasts 60 seconds
        
        # Set initial state
        for i in range(num_lanes):
            lane_num = f"lane_{i}"
            self.signals[lane_num] = self.GREEN if i == 0 else self.RED
            self.signal_start_time[lane_num] = time.time()
    
    def update_signals_adaptive(self, lane_data):
        """
        Update signals based on traffic density (adaptive traffic control)
        
        Args:
            lane_data: Dictionary with lane density information
        """
        if self.emergency_active:
            # Emergency mode - clear path for emergency vehicle
            self._handle_emergency_mode()
            return
        
        # Adaptive signal based on density
        for lane_num, info in lane_data.items():
            level = info["level"]
            
            # If critical traffic in a lane, give it longer green
            if level == "CRITICAL" or level == "HIGH":
                if self.signals[lane_num] == self.RED:
                    # Give green signal to high-traffic lane
                    self._activate_green_signal(lane_num, duration=self.green_phase + 10)
            elif level == "LOW":
                # Low traffic can have shorter green
                if self.signals[lane_num] == self.GREEN:
                    self._start_yellow_signal(lane_num)
    
    def activate_emergency_mode(self, emergency_lane):
        """
        Activate emergency mode - clear the road for emergency vehicle
        
        Args:
            emergency_lane: Lane with emergency vehicle (e.g. 'lane_0')
        """
        logger.warning(f"🚨 EMERGENCY MODE ACTIVATED for {emergency_lane}")
        self.emergency_active = True
        self.emergency_lane = emergency_lane
        self.emergency_start_time = time.time()
        
        # All lanes get RED except emergency lane
        for i in range(self.num_lanes):
            lane_num = f"lane_{i}"
            if lane_num == emergency_lane:
                self.signals[lane_num] = self.GREEN  # Green for emergency
            else:
                self.signals[lane_num] = self.RED     # Red for others
            
            self.signal_start_time[lane_num] = time.time()
    
    def deactivate_emergency_mode(self):
        """Deactivate emergency mode and return to normal operation"""
        if self.emergency_active:
            logger.warning("🚨 Emergency mode deactivated")
            self.emergency_active = False
            self.emergency_lane = None
            self.emergency_start_time = None
            
            # Reset to normal mode
            for i in range(self.num_lanes):
                lane_num = f"lane_{i}"
                self.signals[lane_num] = self.GREEN if i == 0 else self.RED
                self.signal_start_time[lane_num] = time.time()
    
    def _handle_emergency_mode(self):
        """Handle emergency mode timing"""
        if self.emergency_start_time is None:
            return
        
        elapsed = time.time() - self.emergency_start_time
        
        # Check if emergency duration expired
        if elapsed > self.emergency_duration:
            self.deactivate_emergency_mode()
    
    def _activate_green_signal(self, lane_num, duration=None):
        """Activate green signal for a lane"""
        self.signals[lane_num] = self.GREEN
        self.signal_start_time[lane_num] = time.time()
        logger.info(f"🟢 GREEN signal activated for {lane_num}")
    
    def _start_yellow_signal(self, lane_num):
        """Start yellow signal transition"""
        self.signals[lane_num] = self.YELLOW
        self.signal_start_time[lane_num] = time.time()
        logger.info(f"🟡 YELLOW signal activated for {lane_num}")
    
    def get_signal_target(self, lane_num):
        """
        Get the current signal status and target (BGR color)
        
        Args:
            lane_num: Lane identifier
            
        Returns:
            Tuple of (signal_state, color)
        """
        if lane_num not in self.signals:
            return (self.RED, self.SIGNAL_COLORS[self.RED])
        
        if self.emergency_active and lane_num == self.emergency_lane:
            return (self.GREEN, self.SIGNAL_COLORS["EMERGENCY"])
        
        signal = self.signals[lane_num]
        color = self.SIGNAL_COLORS[signal]
        
        return (signal, color)
    
    def get_all_signals(self):
        """Get signal state for all lanes"""
        result = {}
        for i in range(self.num_lanes):
            lane_num = f"lane_{i}"
            signal, color = self.get_signal_target(lane_num)
            result[lane_num] = {
                "signal": signal,
                "color": color
            }
        
        return result
    
    def is_emergency_active(self):
        """Check if emergency mode is active"""
        return self.emergency_active
    
    def get_emergency_info(self):
        """Get info about active emergency"""
        if self.emergency_active:
            elapsed = time.time() - self.emergency_start_time if self.emergency_start_time else 0
            return {
                "active": True,
                "lane": self.emergency_lane,
                "elapsed": elapsed,
                "duration": self.emergency_duration
            }
        else:
            return {"active": False}
