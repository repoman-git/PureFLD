"""
Voting Engine for Meridian v2.1.2

Democratic voting across multiple strategies.
"""

import pandas as pd
from typing import Dict


def vote_signals(
    strategy_signals: Dict[str, pd.Series],
    threshold: float = 0.5
) -> pd.Series:
    """
    Vote on signals across strategies.
    
    Implements democratic voting:
    - long_votes / total >= threshold → +1
    - short_votes / total >= threshold → -1
    - otherwise → 0
    
    Args:
        strategy_signals: Dict of {strategy_name: signal_series}
        threshold: Percentage of strategies required to agree (0.0 to 1.0)
    
    Returns:
        pd.Series: Voted signals (+1/0/-1)
    
    Examples:
        >>> signals = {
        ...     'trend': pd.Series([1, 1, -1, 0]),
        ...     'cycles': pd.Series([1, 0, -1, 1]),
        ...     'seasonal': pd.Series([1, -1, -1, 0])
        ... }
        >>> vote_signals(signals, threshold=0.5)
        # Bar 0: 3/3 long (100%) → +1
        # Bar 1: 1/3 long, 1/3 short (33% each) → 0
        # Bar 2: 0/3 long, 3/3 short (100%) → -1
        # Bar 3: 1/3 long (33%) → 0
    """
    if len(strategy_signals) == 0:
        raise ValueError("No strategy signals provided")
    
    # Get common index
    index = list(strategy_signals.values())[0].index
    
    # Count votes per bar
    long_votes = pd.Series(0, index=index)
    short_votes = pd.Series(0, index=index)
    total_strategies = len(strategy_signals)
    
    for signals in strategy_signals.values():
        long_votes += (signals == 1).astype(int)
        short_votes += (signals == -1).astype(int)
    
    # Calculate vote percentages
    long_pct = long_votes / total_strategies
    short_pct = short_votes / total_strategies
    
    # Determine final signal
    final_signal = pd.Series(0, index=index)
    final_signal[long_pct >= threshold] = 1
    final_signal[short_pct >= threshold] = -1
    
    return final_signal


