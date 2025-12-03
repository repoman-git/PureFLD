"""
Regime Attribution for Meridian v2.1.2

Attribute PnL to market regimes.
"""

import pandas as pd
from typing import Dict


def attribute_to_regimes(
    daily_pnl: pd.Series,
    vol_regime: pd.Series,
    trend_regime: pd.Series,
    cycle_regime: pd.Series
) -> Dict[str, float]:
    """
    Attribute PnL to regime types.
    
    Args:
        daily_pnl: Daily PnL series
        vol_regime: Volatility regime series
        trend_regime: Trend regime series
        cycle_regime: Cycle regime series
    
    Returns:
        Dict[str, float]: PnL per regime type
    """
    attribution = {}
    
    # Volatility regime attribution
    for regime_code in [0, 1, 2]:
        mask = (vol_regime == regime_code)
        pnl_in_regime = daily_pnl[mask].sum()
        regime_name = {0: 'low_vol', 1: 'mid_vol', 2: 'high_vol'}[regime_code]
        attribution[f'vol_{regime_name}'] = pnl_in_regime
    
    # Trend regime attribution
    for regime_code in [-1, 0, 1]:
        mask = (trend_regime == regime_code)
        pnl_in_regime = daily_pnl[mask].sum()
        regime_name = {-1: 'downtrend', 0: 'chop', 1: 'uptrend'}[regime_code]
        attribution[f'trend_{regime_name}'] = pnl_in_regime
    
    # Cycle regime attribution
    for regime_code in [-1, 0, 1]:
        mask = (cycle_regime == regime_code)
        pnl_in_regime = daily_pnl[mask].sum()
        regime_name = {-1: 'falling', 0: 'neutral', 1: 'rising'}[regime_code]
        attribution[f'cycle_{regime_name}'] = pnl_in_regime
    
    return attribution

