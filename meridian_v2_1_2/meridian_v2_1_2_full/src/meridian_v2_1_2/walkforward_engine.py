"""
Walk-Forward Engine for Meridian v2.1.2

Out-of-sample testing with rolling optimization windows for robust strategy validation.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from copy import deepcopy

from .config import MeridianConfig, WalkForwardConfig
from .sweep_engine import run_parameter_sweep, _apply_parameters, _run_single_combination
from .fld_engine import compute_fld
from .seasonality import compute_tdom_flags, compute_tdoy_flags, combine_seasonal_flags
from .strategy import FLDStrategy
from .backtester import run_backtest as run_backtest_engine, BacktestConfig


def generate_walkforward_splits(
    index: pd.DatetimeIndex,
    config: WalkForwardConfig,
    periods_per_year: int = 252
) -> List[Tuple[datetime, datetime, datetime, datetime]]:
    """
    Generate walk-forward train/test splits.
    
    Args:
        index: Full data DatetimeIndex
        config: Walk-forward configuration
        periods_per_year: Trading days per year (default 252)
    
    Returns:
        List of tuples: [(train_start, train_end, test_start, test_end), ...]
        
    Notes:
        - Windows slide by step_years
        - Each split has in_sample_years training + out_sample_years testing
        - Returns empty list if insufficient data
    """
    if len(index) < config.min_bars:
        raise ValueError(f"Insufficient data: need {config.min_bars} bars, got {len(index)}")
    
    splits = []
    
    # Calculate window sizes in bars
    is_bars = int(config.in_sample_years * periods_per_year)
    os_bars = int(config.out_sample_years * periods_per_year)
    step_bars = int(config.step_years * periods_per_year)
    
    # Start from first possible IS window
    start_idx = 0
    
    while start_idx + is_bars <= len(index):
        # Define IS window
        train_start = index[start_idx]
        train_end_idx = start_idx + is_bars - 1
        
        if train_end_idx >= len(index):
            break
        
        train_end = index[train_end_idx]
        
        # Define OS window
        test_start_idx = train_end_idx + 1
        test_end_idx = min(test_start_idx + os_bars - 1, len(index) - 1)
        
        if test_start_idx >= len(index):
            break
        
        test_start = index[test_start_idx]
        test_end = index[test_end_idx]
        
        # Check if OS window is too small
        os_actual_bars = test_end_idx - test_start_idx + 1
        
        if os_actual_bars < os_bars and not config.allow_partial_final_window:
            # Skip partial final window
            break
        
        # Add split
        splits.append((train_start, train_end, test_start, test_end))
        
        # Slide window
        start_idx += step_bars
        
        # Check if we've covered enough
        if test_end_idx >= len(index) - 1:
            break
    
    return splits


def walkforward_run(
    prices: pd.Series,
    base_config: MeridianConfig,
    cot_series: Optional[pd.Series] = None,
    tdom_series: Optional[pd.Series] = None,
    tdoy_series: Optional[pd.Series] = None
) -> pd.DataFrame:
    """
    Execute walk-forward testing with rolling optimization.
    
    For each time window:
    1. Run parameter sweep on in-sample (IS) data
    2. Select best parameters based on optimization metric
    3. Test selected parameters on out-of-sample (OS) data
    4. Record IS and OS performance
    
    Args:
        prices: Full price series
        base_config: Base configuration
        cot_series: Optional COT data
        tdom_series: Optional pre-computed TDOM
        tdoy_series: Optional pre-computed TDOY
    
    Returns:
        pd.DataFrame with one row per walk-forward split containing:
            - Window dates
            - Selected parameters
            - IS metrics
            - OS metrics
    """
    wf_cfg = base_config.walkforward
    
    # Generate splits
    splits = generate_walkforward_splits(prices.index, wf_cfg)
    
    if len(splits) == 0:
        raise ValueError("No valid walk-forward splits generated")
    
    print(f"Walk-Forward Engine: Generated {len(splits)} splits")
    print(f"  IS window: {wf_cfg.in_sample_years} years")
    print(f"  OS window: {wf_cfg.out_sample_years} years")
    print(f"  Step size: {wf_cfg.step_years} years")
    
    results = []
    
    for i, (train_start, train_end, test_start, test_end) in enumerate(splits):
        print(f"\nSplit {i+1}/{len(splits)}: IS {train_start.date()} to {train_end.date()}")
        
        # Extract IS data
        is_prices = prices.loc[train_start:train_end]
        is_cot = cot_series.loc[train_start:train_end] if cot_series is not None else None
        is_tdom = tdom_series.loc[train_start:train_end] if tdom_series is not None else None
        is_tdoy = tdoy_series.loc[train_start:train_end] if tdoy_series is not None else None
        
        # Run parameter sweep on IS
        print(f"  Running IS optimization...")
        is_results = run_parameter_sweep(
            is_prices, base_config, 
            cot_series=is_cot,
            tdom_series=is_tdom,
            tdoy_series=is_tdoy
        )
        
        # Select best parameters
        optimization_metric = wf_cfg.optimization_metric
        best_params = _select_best_parameters(is_results, optimization_metric)
        
        print(f"  Best IS params: cycle={best_params['cycle_length']}, "
              f"disp={best_params['displacement']}, "
              f"{optimization_metric}={best_params[optimization_metric]:.4f}")
        
        # Extract OS data
        os_prices = prices.loc[test_start:test_end]
        os_cot = cot_series.loc[test_start:test_end] if cot_series is not None else None
        os_tdom = tdom_series.loc[test_start:test_end] if tdom_series is not None else None
        os_tdoy = tdoy_series.loc[test_start:test_end] if tdoy_series is not None else None
        
        # Apply best parameters on OS
        print(f"  Testing on OS {test_start.date()} to {test_end.date()}...")
        os_result = _run_out_of_sample(
            os_prices, base_config, best_params,
            os_cot, os_tdom, os_tdoy
        )
        
        print(f"  OS result: return={os_result['total_return']:.4f}, "
              f"trades={os_result['num_trades']}")
        
        # Combine results
        result_row = {
            'split_index': i,
            'train_start': train_start,
            'train_end': train_end,
            'test_start': test_start,
            'test_end': test_end,
            
            # Selected parameters
            'cycle_length': best_params['cycle_length'],
            'displacement': best_params['displacement'],
            'cot_long_threshold': best_params.get('cot_long_threshold', 0.0),
            'cot_short_threshold': best_params.get('cot_short_threshold', 0.0),
            'seasonal_threshold': best_params.get('seasonal_threshold', 0),
            
            # IS metrics
            'is_cagr': best_params['cagr'],
            'is_sharpe': best_params['sharpe_ratio'],
            'is_calmar': best_params['calmar_ratio'],
            'is_return': best_params['total_return'],
            'is_max_drawdown': best_params['max_drawdown'],
            'is_num_trades': best_params['num_trades'],
            
            # OS metrics
            'os_cagr': os_result['cagr'],
            'os_sharpe': os_result['sharpe_ratio'],
            'os_calmar': os_result['calmar_ratio'],
            'os_return': os_result['total_return'],
            'os_max_drawdown': os_result['max_drawdown'],
            'os_num_trades': os_result['num_trades'],
        }
        
        results.append(result_row)
    
    print(f"\nWalk-Forward complete: {len(results)} splits tested")
    
    return pd.DataFrame(results)


def _select_best_parameters(
    sweep_results: pd.DataFrame,
    optimization_metric: str = 'calmar_ratio'
) -> Dict[str, Any]:
    """
    Select best parameter combination from sweep results.
    
    Args:
        sweep_results: DataFrame from run_parameter_sweep()
        optimization_metric: Metric to optimize
    
    Returns:
        Dictionary with best parameters and their metrics
    """
    if len(sweep_results) == 0:
        raise ValueError("No sweep results to select from")
    
    if optimization_metric not in sweep_results.columns:
        raise ValueError(f"Optimization metric '{optimization_metric}' not in results")
    
    # Handle NaN values - they should not be selected
    valid_results = sweep_results[sweep_results[optimization_metric].notna()]
    
    if len(valid_results) == 0:
        raise ValueError("All sweep results have NaN for optimization metric")
    
    # Sort by metric (descending for most metrics)
    if 'drawdown' in optimization_metric.lower():
        # For drawdown, less negative is better (ascending=False means most positive first)
        sorted_results = valid_results.sort_values(optimization_metric, ascending=False)
    else:
        # For returns, ratios, higher is better
        sorted_results = valid_results.sort_values(optimization_metric, ascending=False)
    
    # Get best row as dictionary
    best = sorted_results.iloc[0].to_dict()
    
    return best


def _run_out_of_sample(
    prices: pd.Series,
    base_config: MeridianConfig,
    params: Dict[str, Any],
    cot_series: Optional[pd.Series],
    tdom_series: Optional[pd.Series],
    tdoy_series: Optional[pd.Series]
) -> Dict[str, Any]:
    """
    Run single backtest on out-of-sample data with specified parameters.
    
    Args:
        prices: OS price series
        base_config: Base configuration
        params: Parameters selected from IS optimization
        cot_series: OS COT data
        tdom_series: OS TDOM data
        tdoy_series: OS TDOY data
    
    Returns:
        Dictionary with OS results
    """
    # Apply parameters to config
    config = _apply_parameters(base_config, params)
    
    # Run the backtest using _run_single_combination from sweep engine
    result = _run_single_combination(
        prices, config, params,
        cot_series, tdom_series, tdoy_series
    )
    
    return result


def analyze_walkforward_results(wf_results: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze walk-forward results and compute summary statistics.
    
    Args:
        wf_results: DataFrame from walkforward_run()
    
    Returns:
        Dictionary with analysis:
            - num_splits: Number of WF splits
            - avg_os_return: Average OS return
            - std_os_return: OS return volatility
            - pct_profitable_os: Percentage of profitable OS periods
            - avg_is_return: Average IS return
            - is_os_correlation: Correlation between IS and OS returns
            - parameter_stability: Consistency of selected parameters
    """
    analysis = {
        'num_splits': len(wf_results),
        
        # OS performance
        'avg_os_return': wf_results['os_return'].mean(),
        'std_os_return': wf_results['os_return'].std(),
        'median_os_return': wf_results['os_return'].median(),
        'pct_profitable_os': (wf_results['os_return'] > 0).sum() / len(wf_results),
        
        # IS performance
        'avg_is_return': wf_results['is_return'].mean(),
        'std_is_return': wf_results['is_return'].std(),
        
        # IS vs OS comparison
        'is_os_correlation': wf_results['is_return'].corr(wf_results['os_return']),
        
        # Parameter stability
        'cycle_length_std': wf_results['cycle_length'].std(),
        'displacement_std': wf_results['displacement'].std(),
        
        # Overall metrics
        'avg_os_sharpe': wf_results['os_sharpe'].mean(),
        'avg_os_calmar': wf_results['os_calmar'].mean(),
    }
    
    return analysis


def compute_combined_equity_curve(
    wf_results: pd.DataFrame,
    prices: pd.Series,
    base_config: MeridianConfig,
    cot_series: Optional[pd.Series] = None
) -> pd.Series:
    """
    Reconstruct combined equity curve from walk-forward OS results.
    
    This shows what the equity would look like if you used walk-forward
    optimization in real-time.
    
    Args:
        wf_results: Walk-forward results
        prices: Full price series
        base_config: Base configuration
        cot_series: Optional COT data
    
    Returns:
        pd.Series: Combined equity curve across all OS periods
    """
    # This is a placeholder - full implementation would stitch together OS equity curves
    # For now, return a simple equity series
    equity = pd.Series(base_config.backtest.initial_capital, index=prices.index)
    return equity

