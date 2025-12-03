"""
Asset Attribution for Meridian v2.1.2

Attribute PnL to individual assets.
"""

import pandas as pd
from typing import Dict


def attribute_to_assets(
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> Dict[str, float]:
    """
    Attribute total PnL to individual assets.
    
    Classic attribution:
        PnL_asset = position × price_change
    
    Args:
        positions: Position series per symbol
        prices: Price series per symbol
    
    Returns:
        Dict[str, float]: Total PnL per asset
    """
    attribution = {}
    
    for symbol in positions.keys():
        if symbol in prices:
            pos = positions[symbol]
            price = prices[symbol]
            price_change = price.diff()
            
            # PnL = previous position × price change
            asset_pnl = (pos.shift(1) * price_change).sum()
            attribution[symbol] = asset_pnl
    
    return attribution

