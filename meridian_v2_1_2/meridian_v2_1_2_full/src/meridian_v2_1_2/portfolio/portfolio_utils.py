"""
Portfolio Utilities for Meridian v2.1.2

Helper functions for portfolio management.
"""

import pandas as pd
from typing import Dict


def combine_positions(
    positions_dict: Dict[str, Dict[str, pd.Series]]
) -> Dict[str, pd.Series]:
    """
    Combine positions from multiple strategies.
    
    Args:
        positions_dict: Nested dict {strategy: {symbol: positions}}
    
    Returns:
        Dict[str, pd.Series]: Combined positions per symbol
    """
    combined = {}
    
    for strategy_name, strategy_positions in positions_dict.items():
        for symbol, pos in strategy_positions.items():
            if symbol not in combined:
                combined[symbol] = pos.copy()
            else:
                combined[symbol] = combined[symbol] + pos
    
    return combined


def aggregate_pnl(
    trades_dict: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Aggregate PnL across multiple assets.
    
    Args:
        trades_dict: Dictionary of {symbol: trades_df}
    
    Returns:
        pd.DataFrame: Combined trades with symbol column
    """
    all_trades = []
    
    for symbol, trades in trades_dict.items():
        trades_copy = trades.copy()
        trades_copy['symbol'] = symbol
        all_trades.append(trades_copy)
    
    if len(all_trades) == 0:
        return pd.DataFrame()
    
    combined = pd.concat(all_trades, ignore_index=True)
    
    return combined


