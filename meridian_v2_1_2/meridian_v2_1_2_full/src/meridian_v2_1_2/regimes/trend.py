"""
Trend Regime Classification for Meridian v2.1.2

Classify market trend into uptrend/chop/downtrend regimes.
"""

import pandas as pd
import numpy as np

from ..config import RegimeConfig


def classify_trend(
    prices: pd.Series,
    config: RegimeConfig
) -> pd.Series:
    """
    Classify trend regime using rolling linear regression.
    
    Method:
    1. Compute rolling slope via linear regression over trend_lookback
    2. Classify based on slope magnitude and direction
    
    Args:
        prices: Price series
        config: Regime configuration
    
    Returns:
        pd.Series: Trend regime codes
            +1 = uptrend
             0 = chop/neutral
            -1 = downtrend
    
    Notes:
        - Based on linear regression slope
        - Deterministic classification
        - Smoothed with rolling window
    """
    if len(prices) < config.trend_lookback:
        return pd.Series(0, index=prices.index)  # Default to chop
    
    # Compute rolling slope
    slopes = []
    
    for i in range(len(prices)):
        if i < config.trend_lookback - 1:
            slopes.append(0.0)
            continue
        
        # Get window
        window = prices.iloc[i - config.trend_lookback + 1:i + 1]
        
        # Linear regression
        x = np.arange(len(window))
        y = window.values
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            slopes.append(slope)
        else:
            slopes.append(0.0)
    
    slopes_series = pd.Series(slopes, index=prices.index)
    
    # Classify into regimes
    regime = pd.Series(0, index=prices.index)  # Default chop
    
    # Uptrend
    regime[slopes_series > config.trend_threshold] = 1
    
    # Downtrend
    regime[slopes_series < -config.trend_threshold] = -1
    
    regime.name = 'trend_regime'
    return regime


def get_trend_label(regime_code: int) -> str:
    """
    Get human-readable label for trend regime.
    
    Args:
        regime_code: Trend code (+1/0/-1)
    
    Returns:
        str: Regime label
    """
    labels = {
        1: "Uptrend",
        0: "Chop/Neutral",
        -1: "Downtrend"
    }
    return labels.get(regime_code, f"Unknown ({regime_code})")

