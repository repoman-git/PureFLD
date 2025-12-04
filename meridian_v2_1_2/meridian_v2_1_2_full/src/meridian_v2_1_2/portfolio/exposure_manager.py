"""
Exposure Management for Meridian v2.1.2

Monitor and enforce portfolio-level exposure limits.
"""

import pandas as pd
import numpy as np
from typing import Dict

from ..config import PortfolioConfig


def compute_exposures(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> pd.DataFrame:
    """
    Compute portfolio exposures.
    
    Args:
        positions: Position sizes per symbol
        prices: Prices per symbol
    
    Returns:
        pd.DataFrame with columns:
            - gross_exposure: Sum of absolute position values
            - net_exposure: Sum of signed position values
            - long_exposure: Sum of positive positions
            - short_exposure: Sum of negative positions
    """
    # Calculate position values
    values = {}
    for symbol, pos in positions.items():
        if symbol in prices:
            values[symbol] = pos * prices[symbol]
    
    values_df = pd.DataFrame(values)
    
    # Compute exposures
    exposures = pd.DataFrame(index=values_df.index)
    
    exposures['gross_exposure'] = values_df.abs().sum(axis=1)
    exposures['net_exposure'] = values_df.sum(axis=1)
    exposures['long_exposure'] = values_df[values_df > 0].sum(axis=1).fillna(0)
    exposures['short_exposure'] = values_df[values_df < 0].sum(axis=1).fillna(0).abs()
    
    return exposures


def enforce_exposure_limits(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Enforce portfolio exposure limits by scaling positions.
    
    If limits are violated, scales down all positions proportionally.
    
    Args:
        positions: Position sizes per symbol
        prices: Prices per symbol
        config: Portfolio configuration
    
    Returns:
        Dict[str, pd.Series]: Exposure-limited positions
    """
    # Compute current exposures
    exposures = compute_exposures(positions, prices)
    
    # Get capital (use starting_capital as reference)
    capital = config.starting_capital
    
    # Calculate scaling factors needed
    gross_scale = pd.Series(1.0, index=exposures.index)
    net_scale = pd.Series(1.0, index=exposures.index)
    
    # Check gross exposure limit
    gross_violation = exposures['gross_exposure'] > (capital * config.max_gross_exposure)
    gross_scale[gross_violation] = (capital * config.max_gross_exposure) / exposures['gross_exposure'][gross_violation]
    
    # Check net exposure limit
    net_violation = exposures['net_exposure'].abs() > (capital * config.max_net_exposure)
    net_scale[net_violation] = (capital * config.max_net_exposure) / exposures['net_exposure'][net_violation].abs()
    
    # Take minimum scale factor (most restrictive)
    scale_factor = pd.concat([gross_scale, net_scale], axis=1).min(axis=1)
    
    # Apply scaling
    limited_positions = {}
    for symbol, pos in positions.items():
        limited_positions[symbol] = pos * scale_factor
    
    return limited_positions


