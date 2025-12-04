"""
Synthetic Trend Generator for Meridian v2.1.2

Trend component generation for stress testing.
"""

import numpy as np
import pandas as pd


def generate_trend_component(
    length: int,
    strength: float = 0.4,
    mode: str = "alternating",
    regime_sequence: pd.Series = None,
    seed: int = 42
) -> np.ndarray:
    """
    Generate trend component.
    
    Modes:
    - alternating: Bull/bear cycles
    - random: Random walk trend
    - structural: Long-term drift
    
    Args:
        length: Number of days
        strength: Trend strength (drift per day)
        mode: Trend mode
        regime_sequence: Optional regime sequence
        seed: Random seed
    
    Returns:
        np.ndarray of cumulative trend
    """
    np.random.seed(seed)
    
    if mode == "alternating":
        # Alternate between bull and bear
        trend_period = length // 4
        trend_direction = np.ones(length)
        
        for i in range(0, length, trend_period):
            if (i // trend_period) % 2 == 0:
                trend_direction[i:i+trend_period] = 1.0
            else:
                trend_direction[i:i+trend_period] = -1.0
        
        daily_trend = trend_direction * strength / 252
        return np.cumsum(daily_trend)
    
    elif mode == "random":
        # Random walk with some persistence
        daily_trend = np.random.randn(length) * strength / 252
        return np.cumsum(daily_trend)
    
    elif mode == "structural":
        # Slow upward drift
        daily_trend = strength / 252 + np.random.randn(length) * 0.1 * strength / 252
        return np.cumsum(daily_trend)
    
    elif regime_sequence is not None:
        # Use regime for trend direction
        daily_trend = np.zeros(length)
        
        for i in range(length):
            regime = regime_sequence.iloc[i]
            
            if 'bull' in regime:
                daily_trend[i] = strength / 252
            elif 'bear' in regime:
                daily_trend[i] = -strength / 252
            else:
                daily_trend[i] = 0.0
        
        return np.cumsum(daily_trend)
    
    else:
        return np.zeros(length)


