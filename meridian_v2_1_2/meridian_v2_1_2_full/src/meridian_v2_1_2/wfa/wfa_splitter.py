"""
WFA Splitter for Meridian v2.1.2

Creates rolling train/test windows for walk-forward analysis.
"""

import pandas as pd
from typing import List, Tuple
from datetime import datetime


def parse_period(period_str: str) -> pd.DateOffset:
    """
    Parse period string to DateOffset.
    
    Args:
        period_str: e.g., "3Y", "6M", "1M"
    
    Returns:
        pd.DateOffset
    """
    if period_str.endswith('Y'):
        years = int(period_str[:-1])
        return pd.DateOffset(years=years)
    elif period_str.endswith('M'):
        months = int(period_str[:-1])
        return pd.DateOffset(months=months)
    elif period_str.endswith('D'):
        days = int(period_str[:-1])
        return pd.DateOffset(days=days)
    else:
        raise ValueError(f"Unknown period format: {period_str}")


def split_walkforward_windows(
    dates: pd.DatetimeIndex,
    training_window: str = "3Y",
    testing_window: str = "6M",
    step_size: str = "1M"
) -> List[Tuple[pd.DatetimeIndex, pd.DatetimeIndex]]:
    """
    Split time series into rolling train/test windows.
    
    Args:
        dates: Full date range
        training_window: Training period (e.g., "3Y")
        testing_window: Testing period (e.g., "6M")
        step_size: Step between windows (e.g., "1M")
    
    Returns:
        List of (train_dates, test_dates) tuples
    """
    train_offset = parse_period(training_window)
    test_offset = parse_period(testing_window)
    step_offset = parse_period(step_size)
    
    windows = []
    start_date = dates[0]
    
    while True:
        # Training window
        train_end = start_date + train_offset
        
        # Testing window
        test_start = train_end
        test_end = test_start + test_offset
        
        # Check if we have enough data
        if test_end > dates[-1]:
            break
        
        # Extract dates
        train_mask = (dates >= start_date) & (dates < train_end)
        test_mask = (dates >= test_start) & (dates < test_end)
        
        train_dates = dates[train_mask]
        test_dates = dates[test_mask]
        
        if len(train_dates) > 0 and len(test_dates) > 0:
            windows.append((train_dates, test_dates))
        
        # Move forward
        start_date += step_offset
    
    return windows

