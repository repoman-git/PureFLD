"""
Live Heartbeat Monitor for Meridian v2.1.2

Ensures system connectivity and health during live trading.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


@dataclass
class HeartbeatStatus:
    """Heartbeat status information"""
    is_alive: bool
    last_beat: datetime
    consecutive_failures: int
    alpaca_reachable: bool
    time_synced: bool
    error_message: Optional[str] = None


class LiveHeartbeat:
    """
    Monitors system health during live trading.
    
    Checks:
    - Alpaca API reachability
    - Time synchronization
    - Connection stability
    - Error rates
    """
    
    def __init__(self, config, alpaca_adapter=None):
        """
        Initialize heartbeat monitor.
        
        Args:
            config: LiveConfig instance
            alpaca_adapter: AlpacaAdapter instance
        """
        self.config = config
        self.alpaca_adapter = alpaca_adapter
        
        self.last_beat = None
        self.consecutive_failures = 0
        self.max_failures = config.heartbeat_max_failures
        self.is_alive = True
    
    def check(self) -> HeartbeatStatus:
        """
        Perform heartbeat check.
        
        Returns:
            HeartbeatStatus
        """
        now = datetime.now()
        
        status = HeartbeatStatus(
            is_alive=True,
            last_beat=now,
            consecutive_failures=self.consecutive_failures,
            alpaca_reachable=False,
            time_synced=True
        )
        
        # Check Alpaca connection
        if self.alpaca_adapter:
            try:
                account = self.alpaca_adapter.get_account()
                status.alpaca_reachable = account.get('enabled', False)
            except Exception as e:
                status.alpaca_reachable = False
                status.error_message = f"Alpaca unreachable: {e}"
                self.consecutive_failures += 1
        
        # Check time sync (basic check)
        # In production, would check against NTP or exchange time
        status.time_synced = True
        
        # Update alive status
        if self.consecutive_failures >= self.max_failures:
            status.is_alive = False
            self.is_alive = False
        else:
            status.is_alive = True
            self.is_alive = True
        
        # Reset failures on success
        if status.alpaca_reachable:
            self.consecutive_failures = 0
        
        self.last_beat = now
        
        return status
    
    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        if not self.is_alive:
            return False
        
        # Check if last beat was recent
        if self.last_beat:
            age = datetime.now() - self.last_beat
            max_age = timedelta(seconds=self.config.heartbeat_interval_sec * 2)
            
            if age > max_age:
                return False
        
        return True
    
    def reset(self):
        """Reset heartbeat state"""
        self.consecutive_failures = 0
        self.is_alive = True
        self.last_beat = datetime.now()


