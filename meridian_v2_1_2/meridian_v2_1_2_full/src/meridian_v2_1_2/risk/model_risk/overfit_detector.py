"""
Overfit Detector for Meridian v2.1.2

Detects overfitting using walk-forward analysis results.
"""

import numpy as np
from typing import Dict, List, Any


def compute_overfit_ratio(
    train_performance: float,
    oos_performance: float
) -> float:
    """
    Compute overfit ratio.
    
    Args:
        train_performance: In-sample performance metric
        oos_performance: Out-of-sample performance metric
    
    Returns:
        Overfit ratio (train / OOS)
    """
    if oos_performance <= 0:
        return np.inf
    
    return train_performance / oos_performance


def detect_overfit(
    wfa_results: List[Dict[str, Any]],
    max_overfit_ratio: float = 2.0
) -> Dict[str, Any]:
    """
    Detect overfitting from WFA results.
    
    Args:
        wfa_results: Walk-forward analysis results
        max_overfit_ratio: Maximum acceptable overfit ratio
    
    Returns:
        Dict with overfit detection results
    """
    if not wfa_results:
        return {
            'overfit_detected': False,
            'overfit_ratio': 1.0,
            'is_safe': True,
            'message': 'No WFA results to analyze'
        }
    
    # Compute average overfit ratio
    ratios = []
    
    for result in wfa_results:
        train_perf = result.get('train_sharpe', 1.0)
        oos_perf = result.get('oos_sharpe', 0.5)
        
        if train_perf > 0 and oos_perf > 0:
            ratio = train_perf / oos_perf
            ratios.append(ratio)
    
    if not ratios:
        avg_ratio = 1.0
    else:
        avg_ratio = np.mean(ratios)
    
    overfit_detected = avg_ratio > max_overfit_ratio
    
    # Compute OOS consistency
    oos_sharpes = [r.get('oos_sharpe', 0) for r in wfa_results if 'oos_sharpe' in r]
    
    if oos_sharpes:
        oos_consistency = np.std(oos_sharpes) / (abs(np.mean(oos_sharpes)) + 0.001)
    else:
        oos_consistency = 0.0
    
    return {
        'overfit_detected': overfit_detected,
        'overfit_ratio': avg_ratio,
        'is_safe': not overfit_detected,
        'oos_consistency': oos_consistency,
        'num_windows': len(wfa_results),
        'message': f"Average overfit ratio: {avg_ratio:.2f} (threshold: {max_overfit_ratio:.2f})"
    }


def compute_oos_variance(wfa_results: List[Dict[str, Any]]) -> float:
    """
    Compute variance in OOS performance.
    
    High variance indicates instability.
    
    Args:
        wfa_results: WFA results
    
    Returns:
        OOS variance
    """
    oos_returns = [r.get('oos_return', 0) for r in wfa_results if 'oos_return' in r]
    
    if not oos_returns:
        return 0.0
    
    return np.var(oos_returns)

