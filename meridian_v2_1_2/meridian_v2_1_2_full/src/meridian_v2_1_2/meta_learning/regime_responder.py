"""
Regime-Responsive Weight Adaptation for Meridian v2.1.2

Adjust strategy weights based on current market regime.
"""

import pandas as pd
from typing import Dict

from ..config import MetaLearningConfig


def adapt_weights_by_regime(
    current_weights: Dict[str, float],
    vol_regime: int,
    trend_regime: int,
    cycle_regime: int,
    config: MetaLearningConfig
) -> Dict[str, float]:
    """
    Adapt strategy weights based on current regime.
    
    Regime-based adjustments:
    - High vol → reduce trend, increase mean-reversion
    - Uptrend → increase trend strategies
    - Cycle rising → increase cycle strategies
    
    Args:
        current_weights: Current strategy weights
        vol_regime: Volatility regime (0/1/2)
        trend_regime: Trend regime (-1/0/+1)
        cycle_regime: Cycle regime (-1/0/+1)
        config: Meta-learning configuration
    
    Returns:
        Dict[str, float]: Regime-adjusted weights
    """
    adjusted_weights = current_weights.copy()
    sensitivity = config.regime_transition_sensitivity
    
    # Apply regime-specific adjustments
    for strategy_name in adjusted_weights.keys():
        adjustment_factor = 1.0
        
        # Volatility regime effects
        if vol_regime == 2:  # High vol
            if 'trend' in strategy_name.lower():
                adjustment_factor *= (1 - sensitivity * 0.2)  # Reduce trend
            if 'meanrev' in strategy_name.lower():
                adjustment_factor *= (1 + sensitivity * 0.3)  # Increase mean-reversion
        
        # Trend regime effects
        if trend_regime == 1:  # Uptrend
            if 'trend' in strategy_name.lower():
                adjustment_factor *= (1 + sensitivity * 0.3)  # Boost trend
        elif trend_regime == -1:  # Downtrend
            if 'trend' in strategy_name.lower():
                adjustment_factor *= (1 - sensitivity * 0.2)  # Reduce trend
        
        # Cycle regime effects
        if cycle_regime == 1:  # Cycle rising
            if 'cycle' in strategy_name.lower():
                adjustment_factor *= (1 + sensitivity * 0.3)  # Boost cycle
        elif cycle_regime == -1:  # Cycle falling
            if 'cycle' in strategy_name.lower():
                adjustment_factor *= (1 - sensitivity * 0.2)  # Reduce cycle
        
        adjusted_weights[strategy_name] *= adjustment_factor
    
    # Normalize
    total = sum(adjusted_weights.values())
    if total > 0:
        adjusted_weights = {k: v / total for k, v in adjusted_weights.items()}
    
    return adjusted_weights


