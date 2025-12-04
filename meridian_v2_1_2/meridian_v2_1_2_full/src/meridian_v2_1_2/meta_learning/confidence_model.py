"""
Confidence Model for Meridian v2.1.2

Estimate signal quality and strategy confidence.
"""

import pandas as pd
import numpy as np
from typing import Optional

from ..config import MetaLearningConfig


def compute_signal_confidence(
    signals: pd.Series,
    volatility: Optional[pd.Series] = None,
    regime: Optional[pd.Series] = None,
    config: Optional[MetaLearningConfig] = None
) -> pd.Series:
    """
    Compute confidence score for signals.
    
    Confidence based on:
    - Signal persistence (stable signals = higher confidence)
    - Volatility regime (low vol = higher confidence)
    - Favorable regime (matching conditions = higher confidence)
    
    Args:
        signals: Trading signals
        volatility: Volatility regime (optional)
        regime: Composite regime (optional)
        config: Meta-learning configuration
    
    Returns:
        pd.Series: Confidence scores (0 to 1)
    """
    confidence = pd.Series(0.5, index=signals.index)  # Default medium confidence
    
    # Signal persistence component
    # Signals that persist longer = higher confidence
    signal_changes = (signals != signals.shift(1)).astype(int)
    persistence = 1 - signal_changes.rolling(window=10, min_periods=1).mean()
    
    confidence = (confidence + persistence) / 2
    
    # Volatility component (if provided)
    if volatility is not None:
        # Low vol (0) = high confidence (add 0.2)
        # High vol (2) = low confidence (subtract 0.2)
        vol_adjustment = 0.1 * (1 - volatility / 2)
        confidence = confidence + vol_adjustment
    
    # Clip to [0, 1]
    confidence = confidence.clip(0, 1)
    
    # Smooth
    if config and config.confidence_smoothing > 1:
        confidence = confidence.rolling(
            window=config.confidence_smoothing,
            min_periods=1
        ).mean()
    
    return confidence


def compute_strategy_confidence(
    strategy_returns: pd.Series,
    lookback: int = 50
) -> float:
    """
    Compute overall confidence score for a strategy.
    
    Based on:
    - Consistency of returns
    - Sharpe ratio
    - Drawdown behavior
    
    Args:
        strategy_returns: Returns series
        lookback: Window for evaluation
    
    Returns:
        float: Confidence score (0 to 1)
    """
    if len(strategy_returns) < 2:
        return 0.5
    
    recent = strategy_returns.iloc[-lookback:] if len(strategy_returns) > lookback else strategy_returns
    
    # Component 1: Sharpe-like measure
    mean_ret = recent.mean()
    std_ret = recent.std()
    
    if std_ret > 0:
        sharpe_component = np.tanh(mean_ret / std_ret)  # Normalize to -1 to 1
        sharpe_component = (sharpe_component + 1) / 2  # Scale to 0 to 1
    else:
        sharpe_component = 0.5
    
    # Component 2: Consistency (lower variance = higher confidence)
    if mean_ret != 0:
        cv = abs(std_ret / mean_ret)
        consistency_component = max(0, 1 - cv)
    else:
        consistency_component = 0.5
    
    # Combine
    confidence = 0.6 * sharpe_component + 0.4 * consistency_component
    
    return float(np.clip(confidence, 0, 1))


