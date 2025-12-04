"""
Regime-Based Position Sizing for Meridian v2.1.2

Apply regime-dependent multipliers to position sizes.
"""

import pandas as pd
from typing import Dict

from .risk_config import RiskConfig


def apply_regime_multipliers(
    base_size: pd.Series,
    vol_regime: pd.Series,
    trend_regime: pd.Series,
    cycle_regime: pd.Series,
    config: RiskConfig
) -> pd.Series:
    """
    Apply regime-based multipliers to position sizes.
    
    Multipliers stack multiplicatively:
    - Vol regime effect
    - Trend regime effect  
    - Cycle regime effect
    
    Args:
        base_size: Base position sizes
        vol_regime: Volatility regime (0/1/2)
        trend_regime: Trend regime (-1/0/+1)
        cycle_regime: Cycle regime (-1/0/+1)
        config: Risk configuration
    
    Returns:
        pd.Series: Adjusted position sizes
    """
    adjusted = base_size.copy()
    multipliers = config.regime_multipliers
    
    # Apply vol regime multipliers
    vol_map = {0: 'low_vol', 1: 'mid_vol', 2: 'high_vol'}
    for code, regime_name in vol_map.items():
        mask = (vol_regime == code)
        adjusted[mask] *= multipliers.get(regime_name, 1.0)
    
    # Apply trend regime multipliers
    trend_map = {1: 'uptrend', -1: 'downtrend'}
    for code, regime_name in trend_map.items():
        mask = (trend_regime == code)
        adjusted[mask] *= multipliers.get(regime_name, 1.0)
    
    # Apply cycle regime multipliers
    cycle_map = {1: 'cycle_rising', -1: 'cycle_falling'}
    for code, regime_name in cycle_map.items():
        mask = (cycle_regime == code)
        adjusted[mask] *= multipliers.get(regime_name, 1.0)
    
    adjusted.name = 'regime_adjusted_size'
    return adjusted


