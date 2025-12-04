"""
Composite Regime Scoring for Meridian v2.1.2

Combine multiple regime dimensions into single composite score.
"""

import pandas as pd
import numpy as np

from ..config import RegimeConfig
from .regime_utils import normalize_regime, smooth_regime


def compute_composite_regime(
    vol_regime: pd.Series,
    trend_regime: pd.Series,
    cycle_regime: pd.Series,
    config: RegimeConfig
) -> pd.Series:
    """
    Compute composite regime score from multiple dimensions.
    
    Combines volatility, trend, and cycle regimes using weighted average:
    
    score = w_vol × normalize(vol) + w_trend × normalize(trend) + w_cycle × normalize(cycle)
    
    Then applies smoothing for stability.
    
    Args:
        vol_regime: Volatility regime (0/1/2)
        trend_regime: Trend regime (-1/0/+1)
        cycle_regime: Cycle regime (-1/0/+1)
        config: Regime configuration
    
    Returns:
        pd.Series: Composite regime score (-1 to +1)
        
    Interpretation:
        +1.0: Strong bullish regime
        +0.5: Mild bullish
         0.0: Neutral
        -0.5: Mild bearish
        -1.0: Strong bearish regime
    
    Notes:
        - Deterministic calculation
        - Smoothed for stability
        - Each dimension contributes based on weights
    """
    # Validate indices
    if not (vol_regime.index.equals(trend_regime.index) and 
            trend_regime.index.equals(cycle_regime.index)):
        raise ValueError("All regime series must have matching indices")
    
    # Normalize each regime to -1 to +1 scale
    vol_normalized = normalize_regime(vol_regime, regime_type='volatility')
    trend_normalized = normalize_regime(trend_regime, regime_type='trend')
    cycle_normalized = normalize_regime(cycle_regime, regime_type='cycle')
    
    # Get weights
    w_vol = config.composite_weights.get('vol', 0.33)
    w_trend = config.composite_weights.get('trend', 0.33)
    w_cycle = config.composite_weights.get('cycle', 0.34)
    
    # Weighted combination
    composite = (
        w_vol * vol_normalized +
        w_trend * trend_normalized +
        w_cycle * cycle_normalized
    )
    
    # Apply smoothing
    if config.smoothing_window > 1:
        composite = smooth_regime(composite, config.smoothing_window)
    
    composite.name = 'composite_regime'
    return composite


def get_composite_regime_label(score: float) -> str:
    """
    Get human-readable label for composite regime score.
    
    Args:
        score: Composite score (-1 to +1)
    
    Returns:
        str: Regime label
    """
    if score >= 0.5:
        return "Strong Bullish"
    elif score >= 0.1:
        return "Mild Bullish"
    elif score >= -0.1:
        return "Neutral"
    elif score >= -0.5:
        return "Mild Bearish"
    else:
        return "Strong Bearish"


