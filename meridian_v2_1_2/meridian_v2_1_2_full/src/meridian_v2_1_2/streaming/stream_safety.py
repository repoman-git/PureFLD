"""
Stream Safety for Meridian v2.1.2

Monitoring and protection for streaming layer.
"""

from typing import Dict, Any
from datetime import datetime, timedelta


class StreamSafety:
    """
    Safety monitoring for streaming layer.
    
    Prevents streaming failures from affecting EOD execution.
    """
    
    def __init__(self, config):
        """
        Initialize stream safety.
        
        Args:
            config: StreamerConfig instance
        """
        self.config = config
        self.failure_count = {
            'openbb': 0,
            'alpaca': 0
        }
        self.last_success = {}
        self.paused = False
    
    def check_openbb_health(self, success: bool):
        """
        Check OpenBB health.
        
        Args:
            success: Whether last poll succeeded
        """
        if success:
            self.failure_count['openbb'] = 0
            self.last_success['openbb'] = datetime.now()
        else:
            self.failure_count['openbb'] += 1
        
        # Auto-pause if too many failures
        if self.failure_count['openbb'] >= self.config.max_consecutive_failures:
            self.paused = True
    
    def check_alpaca_health(self, success: bool):
        """
        Check Alpaca health.
        
        Args:
            success: Whether last poll succeeded
        """
        if success:
            self.failure_count['alpaca'] = 0
            self.last_success['alpaca'] = datetime.now()
        else:
            self.failure_count['alpaca'] += 1
        
        # Auto-pause if too many failures
        if self.failure_count['alpaca'] >= self.config.max_consecutive_failures:
            self.paused = True
    
    def is_healthy(self) -> bool:
        """
        Check if streaming is healthy.
        
        Returns:
            True if healthy
        """
        if self.paused:
            return False
        
        # Check failure counts
        if self.failure_count['openbb'] >= self.config.max_consecutive_failures:
            return False
        
        if self.failure_count['alpaca'] >= self.config.max_consecutive_failures:
            return False
        
        return True
    
    def is_paused(self) -> bool:
        """Check if streaming is paused"""
        return self.paused
    
    def resume(self):
        """Resume streaming after pause"""
        self.paused = False
        self.failure_count = {'openbb': 0, 'alpaca': 0}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get safety status.
        
        Returns:
            Status dict
        """
        return {
            'healthy': self.is_healthy(),
            'paused': self.paused,
            'failure_counts': self.failure_count.copy(),
            'last_success': {
                k: v.isoformat() if v else None
                for k, v in self.last_success.items()
            }
        }

