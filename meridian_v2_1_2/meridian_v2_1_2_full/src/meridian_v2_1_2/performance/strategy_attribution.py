"""
Strategy Attribution for Meridian v2.1.2

Attribute PnL to individual strategies.
"""

import pandas as pd
from typing import Dict


def attribute_to_strategies(
    strategy_signals: Dict[str, Dict[str, pd.Series]],
    strategy_weights: Dict[str, float],
    positions: Dict[str, pd.Series],
    prices: Dict[str, pd.Series]
) -> Dict[str, float]:
    """
    Attribute PnL to individual strategies.
    
    For each strategy:
    - Get its signal contribution
    - Weight by strategy weight
    - Multiply by asset returns
    - Compute PnL contribution
    
    Args:
        strategy_signals: Nested dict {strategy: {symbol: signals}}
        strategy_weights: Weight per strategy
        positions: Actual positions
        prices: Prices
    
    Returns:
        Dict[str, float]: PnL contribution per strategy
    """
    attribution = {}
    
    for strategy_name, signals_by_symbol in strategy_signals.items():
        strategy_pnl = 0.0
        weight = strategy_weights.get(strategy_name, 0.0)
        
        for symbol, signals in signals_by_symbol.items():
            if symbol in positions and symbol in prices:
                # Compute return contribution
                price_returns = prices[symbol].pct_change()
                
                # Strategy contribution = weight × signal × return
                # Simplified: assume signal drove position
                contribution = (signals * price_returns * weight).sum()
                strategy_pnl += contribution
        
        attribution[strategy_name] = strategy_pnl
    
    return attribution

