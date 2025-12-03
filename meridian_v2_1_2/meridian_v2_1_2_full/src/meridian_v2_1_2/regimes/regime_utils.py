"""
Regime Utilities for Meridian v2.1.2

Helper functions for regime processing and normalization.
"""

import pandas as pd


def normalize_regime(
    regime: pd.Series,
    regime_type: str = 'generic'
) -> pd.Series:
    """
    Normalize regime codes to -1 to +1 scale.
    
    Args:
        regime: Regime series with integer codes
        regime_type: Type of regime ('volatility', 'trend', 'cycle', or 'generic')
    
    Returns:
        pd.Series: Normalized regime (-1 to +1)
    
    Notes:
        - Volatility (0/1/2) → map to (-1, 0, +1) where low vol = -1, high vol = +1
        - Trend (-1/0/+1) → already normalized
        - Cycle (-1/0/+1) → already normalized
    """
    normalized = regime.copy().astype(float)
    
    if regime_type == 'volatility':
        # Volatility: 0 (low) → -1, 1 (med) → 0, 2 (high) → +1
        # Note: High vol is often bearish/risky, but for bullish bias we map:
        # Low vol (-1) = risk-off, High vol (+1) = risk-on
        normalized = (regime - 1).astype(float)  # Maps 0→-1, 1→0, 2→+1
    
    elif regime_type == 'trend':
        # Trend: already -1/0/+1
        pass
    
    elif regime_type == 'cycle':
        # Cycle: already -1/0/+1
        pass
    
    else:
        # Generic: try to normalize to -1 to +1
        min_val = normalized.min()
        max_val = normalized.max()
        
        if max_val != min_val:
            normalized = 2 * (normalized - min_val) / (max_val - min_val) - 1
    
    return normalized


def smooth_regime(
    regime: pd.Series,
    window: int = 5
) -> pd.Series:
    """
    Smooth regime series to reduce whipsaws.
    
    Args:
        regime: Regime series
        window: Smoothing window
    
    Returns:
        pd.Series: Smoothed regime
    """
    return regime.rolling(window=window, min_periods=1, center=False).mean()

