"""
EOD Signal Runner for Meridian v2.1.2

Run all strategies and generate signals at end of day.
"""

import pandas as pd
from typing import Dict

from ..config import MeridianConfig


def run_eod_signals(
    eod_data: Dict[str, pd.DataFrame],
    config: MeridianConfig
) -> Dict[str, pd.Series]:
    """
    Run signal generation for all symbols at EOD.
    
    For each symbol:
    1. Extract close prices
    2. Run strategy stack
    3. Apply multi-strategy blending
    4. Apply risk sizing
    5. Apply portfolio allocation
    
    Args:
        eod_data: EOD bar data per symbol
        config: Meridian configuration
    
    Returns:
        Dict[str, pd.Series]: Final signals per symbol
    
    Notes:
        - Operates on daily closes only
        - Generates T+1 signals from T data
        - Deterministic given same EOD data
    """
    signals = {}
    
    for symbol, df in eod_data.items():
        # Extract close prices
        prices = df['close']
        
        # Run strategy (simplified - use main orchestrator)
        # In full implementation, would use multi-strategy engine
        from ..orchestrator import run_backtest
        
        # For EOD, we just need the latest signal
        # Full implementation would maintain state and generate next-day signal
        
        # Placeholder: return neutral signal
        signals[symbol] = pd.Series(0, index=[prices.index[-1]])
    
    return signals


def get_latest_signals(
    full_signals: Dict[str, pd.Series]
) -> Dict[str, int]:
    """
    Extract latest signal for each symbol (for next trading day).
    
    Args:
        full_signals: Complete signal series per symbol
    
    Returns:
        Dict[str, int]: Latest signal per symbol (+1/0/-1)
    """
    latest = {}
    
    for symbol, signals in full_signals.items():
        if len(signals) > 0:
            latest[symbol] = int(signals.iloc[-1])
        else:
            latest[symbol] = 0
    
    return latest


