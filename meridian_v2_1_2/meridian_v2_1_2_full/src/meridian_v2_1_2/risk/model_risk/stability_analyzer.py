"""
Stability Analyzer for Meridian v2.1.2

Analyzes parameter and performance stability.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any


def compute_stability_score(
    oos_returns: List[float]
) -> float:
    """
    Compute stability score from OOS returns.
    
    stability = mean / std
    
    Args:
        oos_returns: List of OOS returns
    
    Returns:
        Stability score
    """
    if not oos_returns or len(oos_returns) < 2:
        return 0.0
    
    mean_return = np.mean(oos_returns)
    std_return = np.std(oos_returns)
    
    if std_return == 0:
        return np.inf if mean_return > 0 else 0.0
    
    return mean_return / std_return


def analyze_stability(
    wfa_results: List[Dict[str, Any]],
    strategy_weights_history: List[Dict[str, float]] = None,
    min_stability_score: float = 0.6
) -> Dict[str, Any]:
    """
    Analyze system stability.
    
    Args:
        wfa_results: WFA results
        strategy_weights_history: Historical strategy weights
        min_stability_score: Minimum acceptable stability
    
    Returns:
        Stability analysis results
    """
    # OOS return stability
    oos_returns = [r.get('oos_return', 0) for r in wfa_results if 'oos_return' in r]
    
    if oos_returns:
        stability_score = compute_stability_score(oos_returns)
    else:
        stability_score = 0.0
    
    is_stable = stability_score >= min_stability_score
    
    # Strategy weight stability
    weight_volatility = 0.0
    if strategy_weights_history and len(strategy_weights_history) > 1:
        weight_volatility = _compute_weight_volatility(strategy_weights_history)
    
    # Parameter consistency
    param_consistency = _compute_parameter_consistency(wfa_results)
    
    return {
        'is_stable': is_stable,
        'stability_score': stability_score,
        'weight_volatility': weight_volatility,
        'param_consistency': param_consistency,
        'num_oos_periods': len(oos_returns),
        'message': f"Stability score: {stability_score:.2f} (threshold: {min_stability_score:.2f})"
    }


def _compute_weight_volatility(
    weights_history: List[Dict[str, float]]
) -> float:
    """Compute volatility of strategy weights"""
    if len(weights_history) < 2:
        return 0.0
    
    # Track each strategy's weight over time
    all_strategies = set()
    for weights in weights_history:
        all_strategies.update(weights.keys())
    
    total_volatility = 0.0
    
    for strategy in all_strategies:
        weight_series = [w.get(strategy, 0.0) for w in weights_history]
        if len(weight_series) > 1:
            total_volatility += np.std(weight_series)
    
    return total_volatility / len(all_strategies) if all_strategies else 0.0


def _compute_parameter_consistency(
    wfa_results: List[Dict[str, Any]]
) -> float:
    """Compute parameter consistency across windows"""
    if len(wfa_results) < 2:
        return 1.0
    
    # Check if similar parameters lead to similar results
    # Simplified: just check if OOS performance is consistent
    oos_sharpes = [r.get('oos_sharpe', 0) for r in wfa_results if 'oos_sharpe' in r]
    
    if not oos_sharpes:
        return 0.0
    
    # Consistency = 1 - coefficient of variation
    mean_sharpe = np.mean(oos_sharpes)
    std_sharpe = np.std(oos_sharpes)
    
    if abs(mean_sharpe) < 0.001:
        return 0.0
    
    cv = std_sharpe / abs(mean_sharpe)
    consistency = max(0, 1 - cv)
    
    return consistency

