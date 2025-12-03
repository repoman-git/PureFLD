"""
EOD Scheduler for Meridian v2.1.2

Business day calendar and time advancement.
"""

import pandas as pd
from typing import List
from datetime import datetime


def create_business_calendar(
    start_date: str,
    end_date: str,
    exclude_weekends: bool = True
) -> pd.DatetimeIndex:
    """
    Create business day calendar.
    
    Args:
        start_date: Start date string
        end_date: End date string
        exclude_weekends: Whether to exclude Sat/Sun
    
    Returns:
        DatetimeIndex of trading days
    """
    # Generate full date range
    dates = pd.date_range(start_date, end_date, freq='D')
    
    if exclude_weekends:
        # Remove weekends (5=Saturday, 6=Sunday)
        dates = dates[dates.dayofweek < 5]
    
    return dates


class EODScheduler:
    """
    EOD time scheduler.
    
    Manages simulated time advancement for offline testing.
    """
    
    def __init__(
        self,
        start_date: str = "2010-01-01",
        end_date: str = "2025-01-01",
        simulate_clock: bool = True
    ):
        """
        Initialize scheduler.
        
        Args:
            start_date: Start date
            end_date: End date
            simulate_clock: Whether to use simulated time
        """
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date)
        self.simulate_clock = simulate_clock
        
        # Create calendar
        self.calendar = create_business_calendar(start_date, end_date)
        self.current_idx = 0
    
    def next_trading_day(self) -> pd.Timestamp:
        """
        Get next trading day.
        
        Returns:
            Next trading day or None if at end
        """
        if self.current_idx >= len(self.calendar):
            return None
        
        date = self.calendar[self.current_idx]
        self.current_idx += 1
        
        return date
    
    def has_more_days(self) -> bool:
        """Check if more trading days remain"""
        return self.current_idx < len(self.calendar)
    
    def get_calendar(self) -> pd.DatetimeIndex:
        """Get full calendar"""
        return self.calendar
    
    def jump_to_date(self, date: str) -> bool:
        """
        Jump to specific date.
        
        Args:
            date: Target date string
        
        Returns:
            True if date found, False otherwise
        """
        target = pd.Timestamp(date)
        
        try:
            idx = self.calendar.get_loc(target)
            self.current_idx = idx
            return True
        except KeyError:
            return False
    
    def reset(self):
        """Reset to start of calendar"""
        self.current_idx = 0

