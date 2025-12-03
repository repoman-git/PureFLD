"""
Synthetic Volatility Models for Meridian v2.1.2

Volatility generation for realistic market simulation.
"""

import numpy as np
import pandas as pd


def generate_volatility_regime(
    length: int,
    vol_low: float = 0.005,
    vol_high: float = 0.02,
    regime_sequence: pd.Series = None,
    seed: int = 42
) -> np.ndarray:
    """
    Generate regime-based volatility.
    
    Args:
        length: Number of days
        vol_low: Low volatility
        vol_high: High volatility
        regime_sequence: Optional regime sequence
        seed: Random seed
    
    Returns:
        np.ndarray of daily volatilities
    """
    np.random.seed(seed)
    
    if regime_sequence is not None:
        # Use regime to determine vol
        vol = np.where(
            regime_sequence.str.contains('high_vol'),
            vol_high,
            vol_low
        )
    else:
        # Simple two-state Markov
        vol = np.ones(length) * vol_low
        
        # Periods of high vol
        switch_prob = 0.05
        high_vol_state = False
        
        for i in range(length):
            if np.random.rand() < switch_prob:
                high_vol_state = not high_vol_state
            
            if high_vol_state:
                vol[i] = vol_high
    
    return vol


def generate_stochastic_vol(
    length: int,
    base_vol: float = 0.01,
    vol_of_vol: float = 0.3,
    mean_reversion: float = 0.1,
    seed: int = 42
) -> np.ndarray:
    """
    Generate stochastic volatility (Heston-lite).
    
    Args:
        length: Number of days
        base_vol: Base volatility
        vol_of_vol: Volatility of volatility
        mean_reversion: Mean reversion speed
        seed: Random seed
    
    Returns:
        np.ndarray of daily volatilities
    """
    np.random.seed(seed)
    
    vol = np.zeros(length)
    vol[0] = base_vol
    
    for i in range(1, length):
        # Mean-reverting process
        dv = mean_reversion * (base_vol - vol[i-1]) + vol_of_vol * np.random.randn()
        vol[i] = max(vol[i-1] + dv, 0.001)  # Floor at 0.1%
    
    return vol

