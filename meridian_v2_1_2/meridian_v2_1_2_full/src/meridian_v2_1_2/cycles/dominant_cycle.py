"""
Dominant Cycle Detection for Meridian v2.1.2

Simplified Hurst "half period" cycle estimator using correlation analysis.
"""

import pandas as pd
import numpy as np
from typing import Optional

from ..config import CycleConfig


def estimate_dominant_cycle(
    prices: pd.Series,
    config: CycleConfig
) -> int:
    """
    Estimate dominant cycle using half-period correlation method.
    
    This is a simplified Hurst cycle estimator that:
    1. For each candidate cycle length
    2. Computes smoothed price
    3. Computes shifted version (lag = length / 2)
    4. Computes correlation
    5. Returns cycle with highest absolute correlation
    
    Args:
        prices: Price series
        config: Cycle configuration
    
    Returns:
        int: Estimated dominant cycle length
    
    Notes:
        - Based on Hurst "half period" correlation method
        - Simple and testable
        - Deterministic (same inputs → same output)
    """
    if len(prices) < config.min_cycle:
        return config.min_cycle  # Default to minimum
    
    best_cycle = config.min_cycle
    best_correlation = 0.0
    
    # Test each candidate cycle length
    for cycle_length in range(config.min_cycle, config.max_cycle + 1, config.step):
        if cycle_length > len(prices) // 2:
            break  # Not enough data for this cycle
        
        # Smooth prices
        smoothed = prices.rolling(window=config.smoothing_window, min_periods=1).mean()
        
        # Shift by half cycle
        lag = cycle_length // 2
        shifted = smoothed.shift(lag)
        
        # Compute correlation
        # Use only valid (non-NaN) overlapping period
        valid_mask = smoothed.notna() & shifted.notna()
        if valid_mask.sum() < 10:  # Need minimum overlap
            continue
        
        corr = smoothed[valid_mask].corr(shifted[valid_mask])
        
        # Track best (highest absolute correlation)
        if not np.isnan(corr) and abs(corr) > abs(best_correlation):
            best_correlation = corr
            best_cycle = cycle_length
    
    return best_cycle


def estimate_dominant_cycle_fft(
    prices: pd.Series,
    config: CycleConfig
) -> int:
    """
    Alternative: FFT-based dominant cycle estimation.
    
    Uses Fast Fourier Transform to find dominant frequency.
    
    Args:
        prices: Price series
        config: Cycle configuration
    
    Returns:
        int: Estimated dominant cycle length
    
    Notes:
        - More sophisticated than correlation method
        - May be added in future versions
        - Placeholder for now
    """
    # Placeholder for FFT-based method
    # Would use np.fft.fft() to find dominant frequency
    return estimate_dominant_cycle(prices, config)


