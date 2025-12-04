"""
Kelly Criterion Position Sizing for Meridian v2.1.2

Optimal position sizing based on edge and variance.
"""

import pandas as pd
import numpy as np
from typing import Optional

from .risk_config import RiskConfig


def compute_kelly_size(
    expectancy: float,
    variance: float,
    config: RiskConfig
) -> float:
    """
    Compute Kelly fraction for position sizing.
    
    Kelly Formula:
        K = expectancy / variance
    
    Args:
        expectancy: Expected value per trade
        variance: Variance of trade outcomes
        config: Risk configuration
    
    Returns:
        float: Kelly-based size multiplier
    
    Notes:
        - Full Kelly can be aggressive
        - config.kelly_fraction scales it down (e.g., 0.25 = quarter Kelly)
        - Returns 1.0 if insufficient data or invalid inputs
    """
    if variance <= 0 or expectancy <= 0:
        return 1.0  # No edge or invalid, use base size
    
    # Kelly fraction
    kelly = expectancy / variance
    
    # Scale by fraction (fractional Kelly)
    kelly_size = kelly * config.kelly_fraction
    
    # Reasonable bounds
    kelly_size = max(0.1, min(kelly_size, 5.0))
    
    return kelly_size


def apply_kelly_sizing(
    base_size: pd.Series,
    trade_stats: Optional[dict],
    config: RiskConfig
) -> pd.Series:
    """
    Apply Kelly-based sizing to position series.
    
    Args:
        base_size: Base position sizes
        trade_stats: Dictionary with trade statistics (expectancy, variance)
        config: Risk configuration
    
    Returns:
        pd.Series: Kelly-adjusted position sizes
    """
    if trade_stats is None:
        return base_size
    
    # Check if we have enough trades
    num_trades = trade_stats.get('number_of_trades', 0)
    if num_trades < config.min_trades_for_kelly:
        return base_size  # Not enough data
    
    # Get statistics
    expectancy = trade_stats.get('expectancy', 0)
    
    # Estimate variance from win/loss stats
    avg_win = trade_stats.get('average_win', 0)
    avg_loss = trade_stats.get('average_loss', 0)
    win_rate = trade_stats.get('win_rate', 0.5)
    
    # Variance approximation
    variance = (win_rate * avg_win ** 2 + (1 - win_rate) * avg_loss ** 2) - expectancy ** 2
    
    if variance <= 0:
        return base_size
    
    # Compute Kelly multiplier
    kelly_multiplier = compute_kelly_size(expectancy, variance, config)
    
    # Apply to all positions
    kelly_adjusted = base_size * kelly_multiplier
    
    kelly_adjusted.name = 'kelly_adjusted_size'
    return kelly_adjusted


