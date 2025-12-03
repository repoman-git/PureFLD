"""
Weight Adaptation for Meridian v2.1.2

RL-lite adaptive weight adjustment based on strategy rewards.
"""

import pandas as pd
import numpy as np
from typing import Dict

from ..config import MetaLearningConfig


def adapt_weights(
    current_weights: Dict[str, float],
    rewards: Dict[str, float],
    config: MetaLearningConfig
) -> Dict[str, float]:
    """
    Adapt strategy weights using reinforcement learning principles.
    
    Update rule:
        new_weight = old_weight + learning_rate × reward_delta
    
    Where reward_delta = (reward - mean_reward)
    
    Args:
        current_weights: Current strategy weights
        rewards: Recent rewards per strategy
        config: Meta-learning configuration
    
    Returns:
        Dict[str, float]: Adapted weights (normalized)
    """
    if len(rewards) == 0:
        return current_weights
    
    # Normalize rewards to mean=0
    reward_values = list(rewards.values())
    mean_reward = np.mean(reward_values)
    
    # Compute weight updates
    new_weights = {}
    
    for strategy_name, current_weight in current_weights.items():
        reward = rewards.get(strategy_name, 0.0)
        
        # RL update
        reward_delta = reward - mean_reward
        update = config.learning_rate * reward_delta
        
        new_weight = current_weight + update
        new_weights[strategy_name] = new_weight
    
    # Apply constraints
    new_weights = apply_weight_constraints(new_weights, config)
    
    return new_weights


def apply_weight_constraints(
    weights: Dict[str, float],
    config: MetaLearningConfig
) -> Dict[str, float]:
    """
    Apply constraints to weights.
    
    1. Clip to [min_weight, max_weight]
    2. Ensure non-negative
    3. Normalize to sum=1.0
    4. Re-clip if normalization violated max
    
    Args:
        weights: Raw weights
        config: Configuration
    
    Returns:
        Dict[str, float]: Constrained and normalized weights
    """
    constrained = {}
    
    # First clip to range
    for name, weight in weights.items():
        clipped = np.clip(weight, config.min_weight, config.max_weight)
        constrained[name] = clipped
    
    # Normalize to sum=1.0
    total = sum(constrained.values())
    
    if total > 0:
        normalized = {k: v / total for k, v in constrained.items()}
    else:
        # If all zero, equal weight
        n = len(constrained)
        normalized = {k: 1.0 / n for k in constrained.keys()}
    
    # Re-apply max constraint after normalization (in case it violated)
    final = {}
    for name, weight in normalized.items():
        final[name] = np.clip(weight, config.min_weight, config.max_weight)
    
    # Final normalization
    final_total = sum(final.values())
    if final_total > 0:
        final = {k: v / final_total for k, v in final.items()}
    
    return final

