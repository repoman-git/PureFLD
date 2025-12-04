"""
Walk-Forward Validation Engine

Iterative train/test validation to assess strategy robustness over time.
Supports both fixed-window and expanding-window approaches.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class WalkForwardResult:
    """Results from walk-forward validation"""
    windows: List[Dict[str, Any]]  # List of window results
    train_metrics: List[Dict[str, float]]  # Training metrics per window
    test_metrics: List[Dict[str, float]]  # Test metrics per window
    stability_score: float  # How consistent is performance?
    degradation_factor: float  # How much worse is test vs train?
    stats: Dict[str, Any]  # Summary statistics


def walk_forward_validation(
    strategy_name: str,
    params: Dict[str, Any],
    windows: List[Tuple[str, str, str, str]],
    backtester_func: callable = None
) -> WalkForwardResult:
    """
    Perform walk-forward validation over multiple train/test windows.
    
    Trains strategy parameters on in-sample data, tests on out-of-sample data,
    iterating forward through time to assess stability and robustness.
    
    Args:
        strategy_name: Name of strategy to test
        params: Base parameters for strategy
        windows: List of (train_start, train_end, test_start, test_end) date tuples
        backtester_func: Function to run backtest (optional, uses default if None)
    
    Returns:
        WalkForwardResult: Complete walk-forward analysis results
    
    Example:
        >>> windows = [
        ...     ('2020-01-01', '2020-06-30', '2020-07-01', '2020-12-31'),
        ...     ('2020-07-01', '2020-12-31', '2021-01-01', '2021-06-30'),
        ... ]
        >>> result = walk_forward_validation('FLD', {'fld_offset': 10}, windows)
        >>> print(f"Stability: {result.stability_score:.2f}")
    """
    
    if backtester_func is None:
        # Use default backtester
        from meridian_v2_1_2.api import run_backtest
        backtester_func = run_backtest
    
    window_results = []
    train_metrics_list = []
    test_metrics_list = []
    
    for i, (train_start, train_end, test_start, test_end) in enumerate(windows):
        print(f"Processing window {i+1}/{len(windows)}: "
              f"Train [{train_start} to {train_end}], Test [{test_start} to {test_end}]")
        
        # Run training period
        try:
            train_result = backtester_func(
                strategy_name=strategy_name,
                params=params,
                start_date=train_start,
                end_date=train_end
            )
            train_metrics = train_result.metrics
        except Exception as e:
            print(f"Warning: Training failed for window {i+1}: {e}")
            train_metrics = {'error': str(e)}
        
        # Run test period
        try:
            test_result = backtester_func(
                strategy_name=strategy_name,
                params=params,
                start_date=test_start,
                end_date=test_end
            )
            test_metrics = test_result.metrics
        except Exception as e:
            print(f"Warning: Testing failed for window {i+1}: {e}")
            test_metrics = {'error': str(e)}
        
        # Store window results
        window_info = {
            'window_id': i + 1,
            'train_period': f"{train_start} to {train_end}",
            'test_period': f"{test_start} to {test_end}",
            'train_metrics': train_metrics,
            'test_metrics': test_metrics
        }
        
        window_results.append(window_info)
        train_metrics_list.append(train_metrics)
        test_metrics_list.append(test_metrics)
    
    # Calculate stability and degradation
    stability_score = _calculate_stability(test_metrics_list)
    degradation_factor = _calculate_degradation(train_metrics_list, test_metrics_list)
    
    # Summary statistics
    stats = {
        'n_windows': len(windows),
        'avg_train_sharpe': _safe_mean([m.get('sharpe_ratio', 0) for m in train_metrics_list]),
        'avg_test_sharpe': _safe_mean([m.get('sharpe_ratio', 0) for m in test_metrics_list]),
        'avg_train_return': _safe_mean([m.get('total_return', 0) for m in train_metrics_list]),
        'avg_test_return': _safe_mean([m.get('total_return', 0) for m in test_metrics_list]),
        'sharpe_stability': _safe_std([m.get('sharpe_ratio', 0) for m in test_metrics_list]),
        'return_stability': _safe_std([m.get('total_return', 0) for m in test_metrics_list])
    }
    
    return WalkForwardResult(
        windows=window_results,
        train_metrics=train_metrics_list,
        test_metrics=test_metrics_list,
        stability_score=stability_score,
        degradation_factor=degradation_factor,
        stats=stats
    )


def expanding_window_validation(
    strategy_name: str,
    params: Dict[str, Any],
    start_date: str,
    end_date: str,
    n_windows: int = 5,
    test_size_months: int = 6,
    backtester_func: callable = None
) -> WalkForwardResult:
    """
    Perform expanding-window validation (anchored walk-forward).
    
    Training set grows with each window while test set size stays fixed.
    This mimics real-world scenario where you continuously accumulate data.
    
    Args:
        strategy_name: Name of strategy
        params: Strategy parameters
        start_date: Overall start date (YYYY-MM-DD)
        end_date: Overall end date (YYYY-MM-DD)
        n_windows: Number of windows to create
        test_size_months: Size of each test period in months
        backtester_func: Backtest function (optional)
    
    Returns:
        WalkForwardResult: Validation results
    
    Example:
        >>> # Expanding windows: train grows, test stays same size
        >>> result = expanding_window_validation(
        ...     'FLD', {'fld_offset': 10}, 
        ...     '2020-01-01', '2023-12-31', 
        ...     n_windows=6
        ... )
    """
    
    # Parse dates
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Calculate window boundaries
    total_days = (end_dt - start_dt).days
    test_days = test_size_months * 30  # Approximate
    
    windows = []
    
    for i in range(n_windows):
        # Test period moves forward
        test_end_dt = end_dt - timedelta(days=(n_windows - i - 1) * test_days)
        test_start_dt = test_end_dt - timedelta(days=test_days)
        
        # Train period: from start to test_start (expanding)
        train_start_dt = start_dt
        train_end_dt = test_start_dt - timedelta(days=1)
        
        # Skip if invalid window
        if train_end_dt <= train_start_dt:
            continue
        
        windows.append((
            train_start_dt.strftime('%Y-%m-%d'),
            train_end_dt.strftime('%Y-%m-%d'),
            test_start_dt.strftime('%Y-%m-%d'),
            test_end_dt.strftime('%Y-%m-%d')
        ))
    
    # Run walk-forward validation
    return walk_forward_validation(strategy_name, params, windows, backtester_func)


def _calculate_stability(metrics_list: List[Dict[str, float]]) -> float:
    """
    Calculate stability score based on consistency of metrics.
    
    Returns a score from 0 to 100, where 100 is perfectly stable.
    """
    if not metrics_list or len(metrics_list) < 2:
        return 0.0
    
    # Use Sharpe ratio as primary stability metric
    sharpes = [m.get('sharpe_ratio', 0) for m in metrics_list]
    
    # Remove any NaN or inf
    sharpes = [s for s in sharpes if np.isfinite(s)]
    
    if len(sharpes) < 2:
        return 0.0
    
    # Calculate coefficient of variation (lower is more stable)
    mean_sharpe = np.mean(sharpes)
    std_sharpe = np.std(sharpes)
    
    if mean_sharpe == 0:
        return 0.0
    
    cv = std_sharpe / abs(mean_sharpe)
    
    # Convert to 0-100 scale (lower CV = higher score)
    # CV of 0 = 100, CV of 1 = 50, CV > 2 = 0
    stability = max(0, min(100, 100 * (1 - cv / 2)))
    
    return float(stability)


def _calculate_degradation(
    train_metrics: List[Dict[str, float]], 
    test_metrics: List[Dict[str, float]]
) -> float:
    """
    Calculate how much performance degrades from train to test.
    
    Returns ratio: test_performance / train_performance
    A value of 1.0 means no degradation, < 1.0 means degradation.
    """
    if not train_metrics or not test_metrics:
        return 1.0
    
    train_sharpes = [m.get('sharpe_ratio', 0) for m in train_metrics if 'error' not in m]
    test_sharpes = [m.get('sharpe_ratio', 0) for m in test_metrics if 'error' not in m]
    
    if not train_sharpes or not test_sharpes:
        return 1.0
    
    avg_train = np.mean([s for s in train_sharpes if s > 0])
    avg_test = np.mean([s for s in test_sharpes if s > 0])
    
    if avg_train == 0:
        return 1.0
    
    return float(avg_test / avg_train)


def _safe_mean(values: List[float]) -> float:
    """Calculate mean, handling empty lists and NaN"""
    clean_values = [v for v in values if np.isfinite(v)]
    return float(np.mean(clean_values)) if clean_values else 0.0


def _safe_std(values: List[float]) -> float:
    """Calculate std dev, handling empty lists and NaN"""
    clean_values = [v for v in values if np.isfinite(v)]
    return float(np.std(clean_values)) if len(clean_values) > 1 else 0.0


