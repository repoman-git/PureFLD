"""
Risk Utilities for Meridian v2.1.2

Helper functions for risk management and position sizing.
"""

import pandas as pd


def smooth_sizes(
    sizes: pd.Series,
    window: int = 3
) -> pd.Series:
    """
    Smooth position sizes to reduce whipsaws.
    
    Args:
        sizes: Position size series
        window: Smoothing window
    
    Returns:
        pd.Series: Smoothed sizes
    """
    return sizes.rolling(window=window, min_periods=1, center=False).mean()


def normalize_sizes(
    sizes: pd.Series,
    target_mean: float = 1.0
) -> pd.Series:
    """
    Normalize sizes to have specified mean.
    
    Args:
        sizes: Position size series
        target_mean: Target mean size
    
    Returns:
        pd.Series: Normalized sizes
    """
    current_mean = sizes.mean()
    
    if current_mean > 0:
        normalized = sizes * (target_mean / current_mean)
    else:
        normalized = sizes
    
    return normalized


