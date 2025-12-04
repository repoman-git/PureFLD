"""
Portfolio Capital Allocation for Meridian v2.1.2

Allocate capital across multiple assets using various methods.
"""

import pandas as pd
import numpy as np
from typing import Dict

from ..config import PortfolioConfig


def allocate_capital(
    signals: Dict[str, pd.Series],
    position_sizes: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Allocate capital across multiple assets.
    
    Args:
        signals: Dictionary of {symbol: signal_series}
        position_sizes: Dictionary of {symbol: size_series}
        config: Portfolio configuration
    
    Returns:
        Dict[str, pd.Series]: Allocated position sizes per symbol
    """
    method = config.allocation_method
    
    if method == "equal_weight":
        return _equal_weight_allocation(signals, position_sizes, config)
    elif method == "vol_parity":
        return _vol_parity_allocation(signals, position_sizes, config)
    elif method == "risk_parity":
        return _risk_parity_allocation(signals, position_sizes, config)
    else:
        raise ValueError(f"Unknown allocation method: {method}")


def _equal_weight_allocation(
    signals: Dict[str, pd.Series],
    position_sizes: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Equal weight allocation - each asset gets equal share.
    
    Returns:
        Dict[str, pd.Series]: Equal-weighted positions
    """
    num_assets = len(signals)
    if num_assets == 0:
        return {}
    
    weight_per_asset = 1.0 / num_assets
    
    allocated = {}
    for symbol, sizes in position_sizes.items():
        allocated[symbol] = sizes * weight_per_asset
    
    return allocated


def _vol_parity_allocation(
    signals: Dict[str, pd.Series],
    position_sizes: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Volatility parity allocation - inverse volatility weighting.
    
    Returns:
        Dict[str, pd.Series]: Vol-parity weighted positions
    """
    # Placeholder: Equal weight for now
    # Full implementation would compute inverse vol weights
    return _equal_weight_allocation(signals, position_sizes, config)


def _risk_parity_allocation(
    signals: Dict[str, pd.Series],
    position_sizes: Dict[str, pd.Series],
    config: PortfolioConfig
) -> Dict[str, pd.Series]:
    """
    Risk parity allocation - equal risk contribution.
    
    Returns:
        Dict[str, pd.Series]: Risk-parity weighted positions
    """
    # Placeholder: Equal weight for now
    # Full implementation would use covariance matrix
    return _equal_weight_allocation(signals, position_sizes, config)


def compute_portfolio_weights(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> pd.DataFrame:
    """
    Compute portfolio weights over time.
    
    Args:
        positions: Position sizes per symbol
        prices: Prices per symbol
    
    Returns:
        pd.DataFrame: Weights per symbol over time
    """
    # Calculate position values
    values = {}
    for symbol, pos in positions.items():
        if symbol in prices:
            values[symbol] = pos * prices[symbol]
    
    # Convert to DataFrame
    values_df = pd.DataFrame(values)
    
    # Calculate weights (proportion of total abs value)
    total_abs_value = values_df.abs().sum(axis=1)
    
    weights_df = values_df.div(total_abs_value, axis=0).fillna(0)
    
    return weights_df


