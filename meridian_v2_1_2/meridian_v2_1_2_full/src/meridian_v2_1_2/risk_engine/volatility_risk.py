"""
Volatility-Based Position Sizing for Meridian v2.1.2

Scale position size inversely with volatility to maintain consistent risk.
"""

import pandas as pd
import numpy as np

from .risk_config import RiskConfig


def compute_volatility_sizing(
    prices: pd.Series,
    config: RiskConfig
) -> pd.Series:
    """
    Compute position sizing based on volatility targeting.
    
    Method:
    - Position size = target_vol / rolling_vol
    - High vol → smaller position
    - Low vol → larger position
    
    Args:
        prices: Price series
        config: Risk configuration
    
    Returns:
        pd.Series: Position size multipliers (before caps)
    
    Notes:
        - Inverse volatility scaling
        - Maintains consistent risk exposure
        - Clipped to max_position
    """
    if len(prices) < 2:
        return pd.Series(1.0, index=prices.index)
    
    # Compute log returns
    returns = np.log(prices / prices.shift(1)).fillna(0)
    
    # Rolling volatility
    rolling_vol = returns.rolling(
        window=config.vol_lookback,
        min_periods=max(1, config.vol_lookback // 2)
    ).std()
    
    # Position sizing: target_vol / actual_vol
    # When vol is high, size is small; when vol is low, size is large
    vol_sizes = pd.Series(1.0, index=prices.index)
    
    valid_vol = rolling_vol > 0
    vol_sizes[valid_vol] = config.target_vol / rolling_vol[valid_vol]
    
    # Clip to reasonable range
    vol_sizes = vol_sizes.clip(lower=0.1, upper=config.max_position)
    
    vol_sizes.name = 'vol_size'
    return vol_sizes

