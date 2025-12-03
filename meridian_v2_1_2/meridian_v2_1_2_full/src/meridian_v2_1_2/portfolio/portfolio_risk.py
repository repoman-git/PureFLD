"""
Portfolio Risk Management for Meridian v2.1.2

Portfolio-level volatility targeting and risk controls.
"""

import pandas as pd
import numpy as np
from typing import Dict

from ..config import PortfolioConfig


def compute_portfolio_volatility(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series],
    lookback: int = 20
) -> pd.Series:
    """
    Compute rolling portfolio volatility.
    
    Args:
        positions: Position sizes per symbol
        prices: Prices per symbol
        lookback: Rolling window
    
    Returns:
        pd.Series: Portfolio volatility over time
    """
    # Calculate portfolio value changes
    portfolio_values = _compute_portfolio_value(positions, prices)
    
    # Portfolio returns
    port_returns = portfolio_values.pct_change().fillna(0)
    
    # Rolling volatility
    port_vol = port_returns.rolling(window=lookback, min_periods=max(1, lookback//2)).std()
    
    # Annualize (assuming daily data, 252 trading days)
    port_vol_annual = port_vol * np.sqrt(252)
    
    return port_vol_annual


def target_portfolio_volatility(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Scale portfolio positions to target volatility.
    
    Args:
        positions: Current positions
        prices: Prices
        config: Portfolio configuration
    
    Returns:
        Dict[str, pd.Series]: Vol-targeted positions
    """
    # Compute current portfolio vol
    current_vol = compute_portfolio_volatility(positions, prices, config.vol_lookback)
    
    # Calculate scaling factor
    target = config.target_volatility
    
    scale_factor = pd.Series(1.0, index=current_vol.index)
    valid_vol = current_vol > 0
    scale_factor[valid_vol] = target / current_vol[valid_vol]
    
    # Clip scaling to reasonable range
    scale_factor = scale_factor.clip(0.1, 3.0)
    
    # Apply to all positions
    scaled_positions = {}
    for symbol, pos in positions.items():
        scaled_positions[symbol] = pos * scale_factor
    
    return scaled_positions


def _compute_portfolio_value(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> pd.Series:
    """
    Compute total portfolio value over time.
    
    Returns:
        pd.Series: Portfolio value
    """
    values = {}
    for symbol, pos in positions.items():
        if symbol in prices:
            values[symbol] = pos * prices[symbol]
    
    values_df = pd.DataFrame(values)
    portfolio_value = values_df.sum(axis=1)
    
    return portfolio_value

