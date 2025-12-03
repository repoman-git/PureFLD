"""
PnL Decomposer for Meridian v2.1.2

Core PnL calculation and decomposition.
"""

import pandas as pd
from typing import Dict


def compute_daily_pnl(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> pd.Series:
    """
    Compute daily PnL from positions and prices.
    
    Args:
        positions: Position series per symbol
        prices: Price series per symbol
    
    Returns:
        pd.Series: Daily PnL
    """
    # Align all data
    position_df = pd.DataFrame(positions)
    price_df = pd.DataFrame(prices)
    
    # Compute returns
    returns_df = price_df.pct_change()
    
    # PnL = position × price × return
    # Simplified: position × price_change
    pnl_components = {}
    
    for symbol in positions.keys():
        if symbol in prices:
            pos = position_df[symbol]
            price = price_df[symbol]
            price_change = price.diff()
            
            pnl_components[symbol] = pos.shift(1) * price_change
    
    pnl_df = pd.DataFrame(pnl_components)
    daily_pnl = pnl_df.sum(axis=1)
    
    return daily_pnl


def decompose_pnl(
    daily_pnl: pd.Series,
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> Dict[str, pd.Series]:
    """
    Decompose PnL into components.
    
    Args:
        daily_pnl: Total daily PnL
        positions: Positions per symbol
        prices: Prices per symbol
    
    Returns:
        Dict with PnL components
    """
    decomposition = {
        'total_pnl': daily_pnl
    }
    
    # Per-asset PnL
    for symbol in positions.keys():
        if symbol in prices:
            pos = positions[symbol]
            price = prices[symbol]
            price_change = price.diff()
            
            asset_pnl = pos.shift(1) * price_change
            decomposition[f'pnl_{symbol}'] = asset_pnl
    
    return decomposition

