"""
Sweep Engine for Meridian v2.1.2

Deterministic parameter grid search for strategy optimization and robustness testing.
"""

import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import json
import itertools
from copy import deepcopy

from .config import MeridianConfig, SweepConfig
from .fld_engine import compute_fld
from .seasonality import compute_tdom_flags, compute_tdoy_flags, combine_seasonal_flags
from .strategy import FLDStrategy
from .backtester import run_backtest as run_backtest_engine, BacktestConfig
from .metrics_engine import compute_basic_metrics, compute_trade_metrics


def run_parameter_sweep(
    prices: pd.Series,
    base_config: MeridianConfig,
    cot_series: Optional[pd.Series] = None,
    tdom_series: Optional[pd.Series] = None,
    tdoy_series: Optional[pd.Series] = None
) -> pd.DataFrame:
    """
    Run deterministic parameter sweep over configured grid.
    
    Args:
        prices: Price series
        base_config: Base configuration to start from
        cot_series: Optional COT data
        tdom_series: Optional pre-computed TDOM series
        tdoy_series: Optional pre-computed TDOY series
    
    Returns:
        pd.DataFrame: Results with one row per parameter combination
        
    Notes:
        - Generates Cartesian product of all parameter lists
        - Each combination runs a complete backtest
        - Results are deterministic (same inputs → same outputs)
    """
    sweep_cfg = base_config.sweep
    
    # Build parameter grid
    grid = _build_parameter_grid(sweep_cfg)
    
    if len(grid) == 0:
        raise ValueError("No parameter combinations to sweep")
    
    print(f"Sweep Engine: Testing {len(grid)} parameter combinations...")
    
    # Run backtest for each combination
    results = []
    for i, params in enumerate(grid):
        if (i + 1) % 10 == 0:
            print(f"  Progress: {i+1}/{len(grid)} combinations tested...")
        
        # Create config for this combination
        config = _apply_parameters(base_config, params)
        
        # Run backtest
        try:
            result = _run_single_combination(
                prices, config, params, cot_series, tdom_series, tdoy_series
            )
            results.append(result)
        except Exception as e:
            print(f"  Warning: Combination {i+1} failed: {e}")
            # Add failed result
            result = params.copy()
            result.update({
                'total_return': np.nan,
                'max_drawdown': np.nan,
                'num_trades': 0,
                'win_rate': np.nan,
                'final_equity': np.nan,
                'error': str(e)
            })
            results.append(result)
    
    print(f"Sweep complete: {len(results)} results")
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    return df


def _build_parameter_grid(sweep_cfg: SweepConfig) -> List[Dict[str, Any]]:
    """
    Build Cartesian product of all sweep parameters.
    
    Returns:
        List of parameter dictionaries
    """
    # Get parameter lists (use defaults if empty)
    cycle_lengths = sweep_cfg.cycle_lengths if sweep_cfg.cycle_lengths else [40]
    displacements = sweep_cfg.displacements if sweep_cfg.displacements else [20]
    cot_long_thresholds = sweep_cfg.cot_long_thresholds if sweep_cfg.cot_long_thresholds else [0.0]
    cot_short_thresholds = sweep_cfg.cot_short_thresholds if sweep_cfg.cot_short_thresholds else [0.0]
    seasonal_minimums = sweep_cfg.seasonal_score_minimums if sweep_cfg.seasonal_score_minimums else [0]
    
    # Generate Cartesian product
    combinations = itertools.product(
        cycle_lengths,
        displacements,
        cot_long_thresholds,
        cot_short_thresholds,
        seasonal_minimums
    )
    
    # Convert to list of dicts
    grid = []
    for cycle, disp, cot_long, cot_short, seasonal_min in combinations:
        grid.append({
            'cycle_length': cycle,
            'displacement': disp,
            'cot_long_threshold': cot_long,
            'cot_short_threshold': cot_short,
            'seasonal_threshold': seasonal_min
        })
    
    return grid


def _apply_parameters(
    base_config: MeridianConfig,
    params: Dict[str, Any]
) -> MeridianConfig:
    """
    Apply parameter combination to config.
    
    Args:
        base_config: Base configuration
        params: Parameter dictionary
    
    Returns:
        New config with parameters applied
    """
    # Deep copy to avoid modifying original
    config = deepcopy(base_config)
    
    # Apply FLD parameters (ensure integers)
    config.fld.cycle_length = int(params['cycle_length'])
    config.fld.displacement = int(params['displacement'])
    
    # Apply COT parameters
    config.strategy.cot_long_threshold = params['cot_long_threshold']
    config.strategy.cot_short_threshold = params['cot_short_threshold']
    
    # Seasonal threshold stored for filtering (applied in strategy)
    # Note: This is stored in params, not directly in config
    # The strategy will use the pre-computed seasonal_score
    
    return config


def _run_single_combination(
    prices: pd.Series,
    config: MeridianConfig,
    params: Dict[str, Any],
    cot_series: Optional[pd.Series],
    tdom_series: Optional[pd.Series],
    tdoy_series: Optional[pd.Series]
) -> Dict[str, Any]:
    """
    Run backtest for a single parameter combination.
    
    Returns:
        Dictionary with parameters and results
    """
    # Compute FLD
    fld = compute_fld(prices, config.fld.cycle_length, config.fld.displacement)
    
    # Compute or use provided seasonal scores
    seasonal_score = None
    if config.seasonality.use_tdom or config.seasonality.use_tdoy:
        # Use provided or compute fresh
        if tdom_series is None and config.seasonality.use_tdom:
            tdom_series = compute_tdom_flags(
                prices.index,
                config.seasonality.favourable_days,
                config.seasonality.unfavourable_days
            )
        
        if tdoy_series is None and config.seasonality.use_tdoy:
            tdoy_series = compute_tdoy_flags(
                prices.index,
                config.seasonality.tdoy_favourable,
                config.seasonality.tdoy_unfavourable
            )
        
        # Combine
        if tdom_series is not None or tdoy_series is not None:
            if tdom_series is not None and tdoy_series is not None:
                seasonal_score = combine_seasonal_flags(tdom_series, tdoy_series)
            elif tdom_series is not None:
                seasonal_score = tdom_series
            else:
                seasonal_score = tdoy_series
    
    # Apply seasonal threshold filter
    # Block entries where seasonal_score < threshold
    if seasonal_score is not None:
        threshold = params['seasonal_threshold']
        # Modify seasonal score to block below threshold
        filtered_score = seasonal_score.copy()
        filtered_score[filtered_score < threshold] = -1  # Block these entries
        seasonal_score = filtered_score
    
    # Generate signals
    strategy = FLDStrategy(config.strategy)
    signals = strategy.generate_signals(
        prices, fld, cot_series=cot_series, seasonal_score=seasonal_score
    )
    
    # Run backtest
    backtest_config = BacktestConfig(
        initial_capital=config.backtest.initial_capital,
        commission=config.backtest.commission,
        slippage=config.backtest.slippage
    )
    backtest_results = run_backtest_engine(prices, signals['position'], backtest_config)
    
    # Extract basic stats
    stats = backtest_results['stats']
    equity = backtest_results['equity']
    trades = backtest_results['trades']
    
    # Compute comprehensive metrics
    equity_metrics = compute_basic_metrics(equity, config.backtest.initial_capital)
    trade_metrics = compute_trade_metrics(trades) if len(trades) > 0 else {}
    
    # Combine parameters and results
    result = params.copy()
    
    # Add equity metrics
    result.update({
        'total_return': equity_metrics['return_pct'],
        'cagr': equity_metrics['cagr'],
        'max_drawdown': equity_metrics['max_drawdown'],
        'volatility': equity_metrics['volatility'],
        'sharpe_ratio': equity_metrics['sharpe_ratio'],
        'calmar_ratio': equity_metrics['calmar_ratio'],
        'final_equity': equity_metrics['final_equity'],
    })
    
    # Add trade metrics
    if trade_metrics:
        result.update({
            'num_trades': trade_metrics['number_of_trades'],
            'win_rate': trade_metrics['win_rate'],
            'expectancy': trade_metrics['expectancy'],
            'payoff_ratio': trade_metrics['payoff_ratio'],
            'average_win': trade_metrics['average_win'],
            'average_loss': trade_metrics['average_loss'],
        })
    else:
        result.update({
            'num_trades': 0,
            'win_rate': 0.0,
            'expectancy': 0.0,
            'payoff_ratio': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
        })
    
    return result


def write_results(df: pd.DataFrame, config: SweepConfig) -> str:
    """
    Write sweep results to file.
    
    Args:
        df: Results DataFrame
        config: Sweep configuration
    
    Returns:
        str: Path to output file
    """
    # Create output directory
    output_dir = Path(config.output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine output file
    format_ext = {
        'csv': 'csv',
        'json': 'json',
        'parquet': 'parquet'
    }
    
    ext = format_ext.get(config.output_format, 'csv')
    output_file = output_dir / f"results.{ext}"
    
    # Write based on format
    if config.output_format == 'csv':
        df.to_csv(output_file, index=False)
    elif config.output_format == 'json':
        df.to_json(output_file, orient='records', indent=2)
    elif config.output_format == 'parquet':
        df.to_parquet(output_file, index=False)
    else:
        raise ValueError(f"Unsupported output format: {config.output_format}")
    
    print(f"Results written to: {output_file}")
    return str(output_file)


def get_best_parameters(
    df: pd.DataFrame,
    metric: str = 'total_return',
    ascending: bool = False
) -> Dict[str, Any]:
    """
    Get best parameter combination based on specified metric.
    
    Args:
        df: Results DataFrame
        metric: Metric to optimize ('total_return', 'max_drawdown', etc.)
        ascending: If True, lower is better (e.g., for drawdown)
    
    Returns:
        Dictionary with best parameters and their results
    """
    if metric not in df.columns:
        raise ValueError(f"Metric '{metric}' not found in results")
    
    # Sort by metric
    sorted_df = df.sort_values(metric, ascending=ascending)
    
    # Get best row
    best = sorted_df.iloc[0].to_dict()
    
    return best


def analyze_sweep_results(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze sweep results and provide summary statistics.
    
    Returns:
        Dictionary with analysis results
    """
    analysis = {
        'total_combinations': len(df),
        'successful_runs': df['total_return'].notna().sum(),
        'failed_runs': df['total_return'].isna().sum(),
        
        'best_total_return': df['total_return'].max(),
        'worst_total_return': df['total_return'].min(),
        'mean_total_return': df['total_return'].mean(),
        
        'best_drawdown': df['max_drawdown'].max(),  # Least negative
        'worst_drawdown': df['max_drawdown'].min(),  # Most negative
        
        'mean_num_trades': df['num_trades'].mean(),
        'mean_win_rate': df['win_rate'].mean(),
        
        'parameter_ranges': {
            'cycle_lengths': sorted(df['cycle_length'].unique().tolist()),
            'displacements': sorted(df['displacement'].unique().tolist()),
            'cot_long_thresholds': sorted(df['cot_long_threshold'].unique().tolist()),
        }
    }
    
    return analysis

