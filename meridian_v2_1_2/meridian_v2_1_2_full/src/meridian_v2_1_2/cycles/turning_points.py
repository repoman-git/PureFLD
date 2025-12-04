"""
Turning Point Detection for Meridian v2.1.2

Detect local peaks and troughs in price series.
"""

import pandas as pd
import numpy as np


def detect_turning_points(
    prices: pd.Series,
    window: int = 3
) -> pd.Series:
    """
    Detect turning points (local peaks and troughs).
    
    Uses sliding window to identify local extrema:
    - Peak: Value higher than all neighbors in window
    - Trough: Value lower than all neighbors in window
    
    Args:
        prices: Price series
        window: Window size for local comparison (must be odd)
    
    Returns:
        pd.Series: +1 for peaks, -1 for troughs, 0 otherwise
    
    Notes:
        - Window should be odd (e.g., 3, 5, 7)
        - Larger windows = fewer turning points (less noise)
        - Deterministic algorithm
    """
    if window % 2 == 0:
        window += 1  # Force odd window
    
    turning_points = pd.Series(0, index=prices.index)
    
    half_window = window // 2
    
    for i in range(half_window, len(prices) - half_window):
        # Get window around current bar
        window_data = prices.iloc[i - half_window:i + half_window + 1]
        center_value = prices.iloc[i]
        
        # Check if peak (highest in window)
        if center_value == window_data.max() and center_value > window_data.drop(prices.index[i]).max():
            turning_points.iloc[i] = 1
        
        # Check if trough (lowest in window)
        elif center_value == window_data.min() and center_value < window_data.drop(prices.index[i]).min():
            turning_points.iloc[i] = -1
    
    return turning_points


def smooth_turning_points(
    turning_points: pd.Series,
    smooth_window: int = 5
) -> pd.Series:
    """
    Smooth turning points to eliminate noise.
    
    Args:
        turning_points: Raw turning points series
        smooth_window: Smoothing window
    
    Returns:
        pd.Series: Smoothed turning points
    """
    # Take rolling max of absolute values to preserve signals
    smoothed = turning_points.rolling(window=smooth_window, min_periods=1, center=True).apply(
        lambda x: x[abs(x).idxmax()] if len(x[x != 0]) > 0 else 0,
        raw=False
    )
    
    return smoothed.fillna(0)


