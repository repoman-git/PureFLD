"""
Meta-Strategy Manager for Meridian v2.1.2

Orchestrates adaptive strategy weighting and learning.
"""

import pandas as pd
from typing import Dict, Optional

from ..config import MetaLearningConfig
from .reward_tracker import compute_strategy_rewards
from .weight_adapter import adapt_weights, apply_weight_constraints
from .confidence_model import compute_strategy_confidence
from .regime_responder import adapt_weights_by_regime


class MetaStrategyManager:
    """
    Manages adaptive strategy weighting and meta-learning.
    
    Combines:
    - Reward-based adaptation
    - Regime responsiveness
    - Confidence modeling
    - Weight constraints
    """
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.weight_history = []
        self.reward_history = []
    
    def update_strategy_weights(
        self,
        strategy_returns: Dict[str, pd.Series],
        current_weights: Dict[str, float],
        vol_regime: Optional[int] = None,
        trend_regime: Optional[int] = None,
        cycle_regime: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Update strategy weights using all adaptive mechanisms.
        
        Pipeline:
        1. Compute rewards
        2. Apply weight adaptation
        3. Adjust for regimes (if enabled)
        4. Apply confidence scaling (if enabled)
        5. Apply constraints
        6. Return final weights
        
        Args:
            strategy_returns: Returns per strategy
            current_weights: Current weights
            vol_regime: Current volatility regime
            trend_regime: Current trend regime
            cycle_regime: Current cycle regime
        
        Returns:
            Dict[str, float]: Updated weights
        """
        # 1. Compute rewards
        rewards = compute_strategy_rewards(strategy_returns, self.config)
        
        # 2. Adapt weights based on rewards
        new_weights = adapt_weights(current_weights, rewards, self.config)
        
        # 3. Regime adaptation (if enabled)
        if (self.config.enable_regime_adaptation and 
            vol_regime is not None and 
            trend_regime is not None and 
            cycle_regime is not None):
            
            new_weights = adapt_weights_by_regime(
                new_weights,
                vol_regime,
                trend_regime,
                cycle_regime,
                self.config
            )
        
        # 4. Apply final constraints
        new_weights = apply_weight_constraints(new_weights, self.config)
        
        # 5. Store history
        self.weight_history.append(new_weights.copy())
        self.reward_history.append(rewards.copy())
        
        return new_weights
    
    def get_weight_history(self) -> list:
        """Get historical weight evolution"""
        return self.weight_history
    
    def get_reward_history(self) -> list:
        """Get historical rewards"""
        return self.reward_history

