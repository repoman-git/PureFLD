"""
Signal Blending for Meridian v2.1.2

Combine signals from multiple strategies using various blend modes.
"""

import pandas as pd
import numpy as np
from typing import Dict

from ..config import MetaStrategyConfig


def blend_signals(
    strategy_signals: Dict[str, pd.Series],
    config: MetaStrategyConfig
) -> pd.Series:
    """
    Blend signals from multiple strategies.
    
    Supports multiple blend modes:
    - weighted: Weighted average of signals
    - voting: Democratic voting
    - override: Priority-based override
    - gating: Strict AND-logic (all must agree)
    
    Args:
        strategy_signals: Dict of {strategy_name: signal_series}
        config: Meta-strategy configuration
    
    Returns:
        pd.Series: Blended signal (+1/0/-1)
    """
    if len(strategy_signals) == 0:
        raise ValueError("No strategy signals provided")
    
    blend_mode = config.blend_mode
    
    if blend_mode == "weighted":
        return _weighted_blend(strategy_signals, config)
    elif blend_mode == "voting":
        return _voting_blend(strategy_signals, config)
    elif blend_mode == "override":
        return _override_blend(strategy_signals, config)
    elif blend_mode == "gating":
        return _gating_blend(strategy_signals, config)
    else:
        raise ValueError(f"Unknown blend mode: {blend_mode}")


def _weighted_blend(
    strategy_signals: Dict[str, pd.Series],
    config: MetaStrategyConfig
) -> pd.Series:
    """
    Weighted blending: final_signal = Σ(weight_i × signal_i)
    
    Returns:
        pd.Series: Weighted average signal (then sign converted)
    """
    # Get index from first strategy
    index = list(strategy_signals.values())[0].index
    
    # Initialize weighted sum
    weighted_sum = pd.Series(0.0, index=index)
    total_weight = 0.0
    
    for strategy_name, signals in strategy_signals.items():
        weight = config.strategy_weights.get(strategy_name, 1.0)
        weighted_sum += signals * weight
        total_weight += weight
    
    # Normalize
    if total_weight > 0:
        blended = weighted_sum / total_weight
    else:
        blended = weighted_sum
    
    # Convert to discrete signals (+1/0/-1)
    discrete_signals = pd.Series(0, index=index)
    discrete_signals[blended > 0.1] = 1
    discrete_signals[blended < -0.1] = -1
    
    return discrete_signals


def _voting_blend(
    strategy_signals: Dict[str, pd.Series],
    config: MetaStrategyConfig
) -> pd.Series:
    """
    Voting: Democratic voting across strategies
    
    Returns:
        pd.Series: Voted signal based on threshold
    """
    index = list(strategy_signals.values())[0].index
    
    # Count votes
    long_votes = pd.Series(0, index=index)
    short_votes = pd.Series(0, index=index)
    total_strategies = len(strategy_signals)
    
    for signals in strategy_signals.values():
        long_votes += (signals == 1).astype(int)
        short_votes += (signals == -1).astype(int)
    
    # Determine final signal based on threshold
    final_signal = pd.Series(0, index=index)
    
    long_pct = long_votes / total_strategies
    short_pct = short_votes / total_strategies
    
    final_signal[long_pct >= config.voting_threshold] = 1
    final_signal[short_pct >= config.voting_threshold] = -1
    
    return final_signal


def _override_blend(
    strategy_signals: Dict[str, pd.Series],
    config: MetaStrategyConfig
) -> pd.Series:
    """
    Override: Priority-based signal selection
    
    Strategies are ordered by config.strategies_enabled list.
    First non-zero signal wins.
    
    Returns:
        pd.Series: Override-selected signal
    """
    index = list(strategy_signals.values())[0].index
    final_signal = pd.Series(0, index=index)
    
    # Priority order from config
    priority_order = config.strategies_enabled if config.strategies_enabled else list(strategy_signals.keys())
    
    for strategy_name in priority_order:
        if strategy_name in strategy_signals:
            signals = strategy_signals[strategy_name]
            
            # Where final_signal is still 0 and this strategy has signal, use it
            still_zero = (final_signal == 0)
            has_signal = (signals != 0)
            final_signal[still_zero & has_signal] = signals[still_zero & has_signal]
    
    return final_signal


def _gating_blend(
    strategy_signals: Dict[str, pd.Series],
    config: MetaStrategyConfig
) -> pd.Series:
    """
    Gating: Strict AND-logic - all strategies must agree
    
    Returns:
        pd.Series: Signal only where all strategies agree
    """
    index = list(strategy_signals.values())[0].index
    
    # Start with first strategy
    signals_list = list(strategy_signals.values())
    final_signal = signals_list[0].copy()
    
    # Apply AND-logic with each subsequent strategy
    for signals in signals_list[1:]:
        # Signal only persists if both agree
        # Long requires both long
        final_signal[(final_signal == 1) & (signals != 1)] = 0
        
        # Short requires both short
        final_signal[(final_signal == -1) & (signals != -1)] = 0
        
        # If either is opposite, cancel
        final_signal[(final_signal == 1) & (signals == -1)] = 0
        final_signal[(final_signal == -1) & (signals == 1)] = 0
    
    return final_signal


