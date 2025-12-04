"""
Volatility Regime Classification for Meridian v2.1.2

Classify market volatility into low/medium/high regimes.
"""

import pandas as pd
import numpy as np

from ..config import RegimeConfig


def classify_volatility(
    prices: pd.Series,
    config: RegimeConfig
) -> pd.Series:
    """
    Classify volatility regime.
    
    Method:
    1. Compute log returns
    2. Rolling standard deviation over vol_lookback
    3. Classify into regimes based on thresholds
    
    Args:
        prices: Price series
        config: Regime configuration
    
    Returns:
        pd.Series: Volatility regime codes
            0 = low volatility
            1 = medium volatility
            2 = high volatility
    
    Notes:
        - Based on rolling standard deviation of returns
        - Deterministic classification
        - Useful for risk management and strategy adaptation
    """
    if len(prices) < 2:
        return pd.Series(1, index=prices.index)  # Default to medium
    
    # Compute log returns
    log_returns = np.log(prices / prices.shift(1)).fillna(0)
    
    # Rolling volatility
    volatility = log_returns.rolling(
        window=config.vol_lookback,
        min_periods=max(1, config.vol_lookback // 2)
    ).std()
    
    # Classify into regimes
    regime = pd.Series(1, index=prices.index)  # Default medium
    
    # Low volatility
    regime[volatility < config.vol_threshold_low] = 0
    
    # High volatility
    regime[volatility > config.vol_threshold_high] = 2
    
    regime.name = 'vol_regime'
    return regime


def get_volatility_label(regime_code: int) -> str:
    """
    Get human-readable label for volatility regime.
    
    Args:
        regime_code: Volatility code (0/1/2)
    
    Returns:
        str: Regime label
    """
    labels = {
        0: "Low Volatility",
        1: "Medium Volatility",
        2: "High Volatility"
    }
    return labels.get(regime_code, f"Unknown ({regime_code})")


