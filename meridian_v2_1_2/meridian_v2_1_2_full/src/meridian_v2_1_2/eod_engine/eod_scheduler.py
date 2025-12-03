"""
EOD Scheduler for Meridian v2.1.2

Handles daily trigger logic and market calendar awareness.
"""

from datetime import datetime, time
from typing import Optional


class EODScheduler:
    """
    End-of-day scheduler for trading cycle triggers.
    
    Determines when to run the daily trading cycle.
    """
    
    def __init__(
        self,
        run_time: time = time(16, 30),  # 4:30 PM ET (after US market close)
        trading_days_only: bool = True
    ):
        """
        Initialize EOD scheduler.
        
        Args:
            run_time: Time of day to run (default: 4:30 PM)
            trading_days_only: Only run on trading days
        """
        self.run_time = run_time
        self.trading_days_only = trading_days_only
    
    def should_run_now(self, current_time: Optional[datetime] = None) -> bool:
        """
        Check if trading cycle should run now.
        
        Args:
            current_time: Current datetime (uses now() if None)
        
        Returns:
            bool: True if should run
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Check if it's the right time
        if current_time.time() >= self.run_time:
            # Check if it's a trading day
            if self.trading_days_only:
                # Skip weekends
                if current_time.weekday() >= 5:  # Saturday=5, Sunday=6
                    return False
            
            return True
        
        return False


def should_run_today(
    current_date: Optional[datetime] = None,
    skip_weekends: bool = True
) -> bool:
    """
    Simple check if trading should run today.
    
    Args:
        current_date: Date to check (uses today if None)
        skip_weekends: Skip Saturday/Sunday
    
    Returns:
        bool: True if should run
    """
    if current_date is None:
        current_date = datetime.now()
    
    if skip_weekends and current_date.weekday() >= 5:
        return False
    
    return True

