"""
Risk Attribution for Meridian v2.1.2

Attribute PnL to risk management decisions.
"""

import pandas as pd
from typing import Dict


def attribute_to_risk_factors(
    daily_pnl: pd.Series,
    position_sizes: Dict[str, pd.Series],
    volatility: pd.Series
) -> Dict[str, float]:
    """
    Attribute PnL to risk management factors.
    
    Analyzes:
    - Position sizing decisions
    - Volatility targeting effects
    - Risk contribution by asset
    
    Args:
        daily_pnl: Daily PnL
        position_sizes: Position sizes per asset
        volatility: Portfolio volatility
    
    Returns:
        Dict[str, float]: Risk-attributed PnL
    """
    attribution = {
        'total_pnl': daily_pnl.sum()
    }
    
    # Simple risk attribution
    # Full implementation would decompose by:
    # - Vol targeting contribution
    # - Regime sizing contribution
    # - Cycle sizing contribution
    
    # Placeholder: categorize by volatility regime
    if len(volatility) > 0:
        median_vol = volatility.median()
        
        high_vol_mask = volatility > median_vol
        low_vol_mask = ~high_vol_mask
        
        attribution['high_vol_periods'] = daily_pnl[high_vol_mask].sum()
        attribution['low_vol_periods'] = daily_pnl[low_vol_mask].sum()
    
    return attribution


