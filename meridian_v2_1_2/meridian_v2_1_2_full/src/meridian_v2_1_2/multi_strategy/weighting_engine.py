"""
Weighting Engine for Meridian v2.1.2

Compute strategy weights for signal blending.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def compute_strategy_weights(
    strategy_names: list,
    config_weights: Optional[Dict[str, float]] = None,
    risk_budgets: Optional[Dict[str, float]] = None,
    performance_weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """
    Compute normalized strategy weights.
    
    Combines:
    1. Config weights (user-specified)
    2. Risk budgets (risk allocation)
    3. Performance weights (past performance) - optional
    
    Args:
        strategy_names: List of strategy names
        config_weights: User-specified weights
        risk_budgets: Risk budget per strategy
        performance_weights: Performance-based weights (optional)
    
    Returns:
        Dict[str, float]: Normalized weights (sum to 1.0)
    """
    weights = {}
    
    for name in strategy_names:
        # Start with config weight or equal
        base_weight = config_weights.get(name, 1.0) if config_weights else 1.0
        
        # Apply risk budget if provided
        risk_factor = risk_budgets.get(name, 1.0) if risk_budgets else 1.0
        
        # Apply performance weight if provided
        perf_factor = performance_weights.get(name, 1.0) if performance_weights else 1.0
        
        # Combine multiplicatively
        weights[name] = base_weight * risk_factor * perf_factor
    
    # Normalize to sum to 1.0
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: v / total_weight for k, v in weights.items()}
    
    return weights


