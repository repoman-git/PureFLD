"""
WFA Metrics for Meridian v2.1.2

Compute out-of-sample metrics and stability measures.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any


def compute_overfit_index(
    train_perf: float,
    oos_perf: float
) -> float:
    """
    Compute overfit index.
    
    Ratio of training performance to OOS performance.
    
    Args:
        train_perf: Training Sharpe/MAR
        oos_perf: OOS Sharpe/MAR
    
    Returns:
        float: Overfit index (>2 indicates overfitting)
    """
    if oos_perf <= 0:
        return np.inf
    
    return train_perf / oos_perf


def compute_stability_score(
    oos_returns: List[float]
) -> float:
    """
    Compute stability score across WFA windows.
    
    Stability = mean(OOS returns) / std(OOS returns)
    
    Args:
        oos_returns: List of OOS returns from each window
    
    Returns:
        float: Stability score
    """
    if len(oos_returns) == 0:
        return 0.0
    
    returns_array = np.array(oos_returns)
    
    if returns_array.std() == 0:
        return 0.0
    
    return returns_array.mean() / returns_array.std()


def compute_wfa_metrics(
    wfa_results: List[Dict[str, Any]]
) -> Dict[str, float]:
    """
    Compute comprehensive WFA metrics.
    
    Args:
        wfa_results: List of window results
    
    Returns:
        Dict with aggregated metrics
    """
    if len(wfa_results) == 0:
        return {}
    
    # Extract OOS metrics
    oos_sharpes = [r['oos_sharpe'] for r in wfa_results]
    oos_returns = [r['oos_return'] for r in wfa_results]
    
    # Extract training metrics
    train_sharpes = [r['train_sharpe'] for r in wfa_results]
    
    # Compute aggregate metrics
    metrics = {
        'mean_oos_sharpe': np.mean(oos_sharpes),
        'median_oos_sharpe': np.median(oos_sharpes),
        'std_oos_sharpe': np.std(oos_sharpes),
        'mean_oos_return': np.mean(oos_returns),
        'total_oos_return': np.sum(oos_returns),
        'stability_score': compute_stability_score(oos_returns),
        'num_windows': len(wfa_results),
        'positive_windows': sum(1 for r in oos_returns if r > 0),
        'negative_windows': sum(1 for r in oos_returns if r < 0),
        'win_rate': sum(1 for r in oos_returns if r > 0) / len(oos_returns) if len(oos_returns) > 0 else 0.0
    }
    
    # Overfit index
    if len(train_sharpes) > 0 and len(oos_sharpes) > 0:
        metrics['overfit_index'] = compute_overfit_index(
            np.mean(train_sharpes),
            np.mean(oos_sharpes)
        )
    
    return metrics


