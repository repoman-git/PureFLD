"""
Metrics Engine for Meridian v2.1.2

Comprehensive performance and risk analytics for backtest results and parameter sweeps.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def compute_basic_metrics(
    equity_curve: pd.Series,
    initial_capital: float = 100000.0,
    periods_per_year: int = 252
) -> Dict[str, float]:
    """
    Compute basic performance and risk metrics from equity curve.
    
    Args:
        equity_curve: Equity curve series
        initial_capital: Starting capital
        periods_per_year: Number of trading periods per year (252 for daily)
    
    Returns:
        Dictionary with metrics:
            - final_equity: Final equity value
            - return_pct: Total return percentage
            - total_return: Absolute return
            - cagr: Compound Annual Growth Rate
            - max_drawdown: Maximum drawdown (negative)
            - volatility: Annualized volatility
            - sharpe_ratio: Annualized Sharpe ratio (risk-free = 0)
            - calmar_ratio: CAGR / |MaxDD|
    """
    if len(equity_curve) == 0:
        return _empty_metrics()
    
    if len(equity_curve) == 1:
        # Single point - no returns to calculate
        final_equity = equity_curve.iloc[0]
        return {
            'final_equity': float(final_equity),
            'return_pct': float((final_equity / initial_capital) - 1.0),
            'total_return': float(final_equity - initial_capital),
            'cagr': 0.0,
            'max_drawdown': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'calmar_ratio': 0.0
        }
    
    # Basic returns
    final_equity = equity_curve.iloc[-1]
    total_return = final_equity - initial_capital
    return_pct = (final_equity / initial_capital) - 1.0
    
    # Calculate returns series
    returns = equity_curve.pct_change().fillna(0)
    
    # CAGR
    years = len(equity_curve) / periods_per_year
    if years > 0 and final_equity > 0:
        cagr = (final_equity / initial_capital) ** (1 / years) - 1
    else:
        cagr = 0.0
    
    # Maximum Drawdown
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    max_drawdown = drawdown.min()  # Most negative value
    
    # Volatility (annualized)
    volatility = returns.std() * np.sqrt(periods_per_year)
    
    # Sharpe Ratio (annualized, risk-free = 0)
    if volatility > 0:
        sharpe_ratio = (returns.mean() * periods_per_year) / volatility
    else:
        sharpe_ratio = 0.0
    
    # Calmar Ratio (CAGR / |MaxDD|)
    if max_drawdown < 0:
        calmar_ratio = cagr / abs(max_drawdown)
    else:
        calmar_ratio = 0.0 if cagr == 0 else np.inf
    
    return {
        'final_equity': float(final_equity),
        'return_pct': float(return_pct),
        'total_return': float(total_return),
        'cagr': float(cagr),
        'max_drawdown': float(max_drawdown),
        'volatility': float(volatility),
        'sharpe_ratio': float(sharpe_ratio),
        'calmar_ratio': float(calmar_ratio)
    }


def compute_trade_metrics(trades_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute trade-level metrics from trades DataFrame.
    
    Args:
        trades_df: DataFrame with columns:
            - entry_price
            - exit_price
            - entry_date (optional)
            - exit_date (optional)
            - pnl
            - bars (optional, hold period)
    
    Returns:
        Dictionary with trade metrics:
            - number_of_trades
            - win_rate
            - average_win
            - average_loss
            - payoff_ratio
            - expectancy
            - median_hold_period (if available)
            - mean_hold_period (if available)
    """
    if len(trades_df) == 0:
        return _empty_trade_metrics()
    
    # Basic counts
    number_of_trades = len(trades_df)
    
    # Separate wins and losses
    wins = trades_df[trades_df['pnl'] > 0]
    losses = trades_df[trades_df['pnl'] < 0]
    
    num_wins = len(wins)
    num_losses = len(losses)
    
    # Win rate
    win_rate = num_wins / number_of_trades if number_of_trades > 0 else 0.0
    
    # Average win/loss
    average_win = wins['pnl'].mean() if len(wins) > 0 else 0.0
    average_loss = losses['pnl'].mean() if len(losses) > 0 else 0.0
    
    # Payoff ratio (avg_win / |avg_loss|)
    if average_loss < 0:
        payoff_ratio = average_win / abs(average_loss)
    else:
        payoff_ratio = 0.0 if average_win == 0 else np.inf
    
    # Expectancy
    loss_rate = 1.0 - win_rate
    expectancy = (win_rate * average_win) + (loss_rate * average_loss)
    
    # Hold periods (if available)
    median_hold_period = None
    mean_hold_period = None
    if 'bars' in trades_df.columns:
        median_hold_period = trades_df['bars'].median()
        mean_hold_period = trades_df['bars'].mean()
    
    return {
        'number_of_trades': int(number_of_trades),
        'win_rate': float(win_rate),
        'num_wins': int(num_wins),
        'num_losses': int(num_losses),
        'average_win': float(average_win),
        'average_loss': float(average_loss),
        'payoff_ratio': float(payoff_ratio),
        'expectancy': float(expectancy),
        'median_hold_period': float(median_hold_period) if median_hold_period is not None else None,
        'mean_hold_period': float(mean_hold_period) if mean_hold_period is not None else None
    }


def compute_robustness_score(
    sweep_df: pd.DataFrame,
    return_col: str = 'total_return',
    dd_col: str = 'max_drawdown'
) -> Dict[str, Any]:
    """
    Compute robustness score for parameter sweep results.
    
    Robustness indicates how stable and reliable the strategy is across
    different parameter combinations.
    
    Args:
        sweep_df: Sweep results DataFrame
        return_col: Column name for returns
        dd_col: Column name for drawdown
    
    Returns:
        Dictionary with robustness metrics:
            - robustness_score: Overall score (0-1, higher is better)
            - pct_profitable: Percentage of profitable combinations
            - avg_return: Average return across all combinations
            - std_return: Standard deviation of returns
            - avg_mar: Average MAR ratio (return / |drawdown|)
            - parameter_smoothness: Smoothness score (0-1)
            - num_combinations: Total combinations tested
    """
    if len(sweep_df) == 0:
        return _empty_robustness_metrics()
    
    # Remove failed runs
    valid_df = sweep_df[sweep_df[return_col].notna()].copy()
    num_combinations = len(valid_df)
    
    if num_combinations == 0:
        return _empty_robustness_metrics()
    
    # 1. Percentage profitable
    pct_profitable = (valid_df[return_col] > 0).sum() / num_combinations
    
    # 2. Return statistics
    avg_return = valid_df[return_col].mean()
    std_return = valid_df[return_col].std()
    
    # 3. MAR ratio (return / |drawdown|)
    # Calculate MAR for each combination
    mar_values = []
    for _, row in valid_df.iterrows():
        ret = row[return_col]
        dd = row[dd_col]
        if dd < 0:
            mar = ret / abs(dd)
            mar_values.append(mar)
    
    avg_mar = np.mean(mar_values) if len(mar_values) > 0 else 0.0
    
    # 4. Parameter smoothness
    # Measure how smoothly returns vary across parameter space
    # Simple version: coefficient of variation (lower is smoother)
    if avg_return != 0:
        cv = abs(std_return / avg_return)
        # Normalize to 0-1 (lower CV = higher smoothness)
        parameter_smoothness = max(0, 1 - min(cv, 1))
    else:
        parameter_smoothness = 0.0
    
    # 5. Compute overall robustness score
    # Weighted combination of factors
    # Normalize components to 0-1 scale
    
    # Normalize MAR (assume MAR of 2+ is excellent)
    normalized_mar = min(avg_mar / 2.0, 1.0) if avg_mar > 0 else 0.0
    
    # Combine factors
    robustness_score = (
        pct_profitable * 0.3 +         # 30% weight on profitability rate
        normalized_mar * 0.3 +           # 30% weight on risk-adjusted return
        parameter_smoothness * 0.4       # 40% weight on stability
    )
    
    return {
        'robustness_score': float(robustness_score),
        'pct_profitable': float(pct_profitable),
        'avg_return': float(avg_return),
        'std_return': float(std_return),
        'avg_mar': float(avg_mar),
        'parameter_smoothness': float(parameter_smoothness),
        'num_combinations': int(num_combinations)
    }


def _empty_metrics() -> Dict[str, float]:
    """Return empty metrics dict"""
    return {
        'final_equity': 0.0,
        'return_pct': 0.0,
        'total_return': 0.0,
        'cagr': 0.0,
        'max_drawdown': 0.0,
        'volatility': 0.0,
        'sharpe_ratio': 0.0,
        'calmar_ratio': 0.0
    }


def _empty_trade_metrics() -> Dict[str, Any]:
    """Return empty trade metrics dict"""
    return {
        'number_of_trades': 0,
        'win_rate': 0.0,
        'num_wins': 0,
        'num_losses': 0,
        'average_win': 0.0,
        'average_loss': 0.0,
        'payoff_ratio': 0.0,
        'expectancy': 0.0,
        'median_hold_period': None,
        'mean_hold_period': None
    }


def _empty_robustness_metrics() -> Dict[str, Any]:
    """Return empty robustness metrics dict"""
    return {
        'robustness_score': 0.0,
        'pct_profitable': 0.0,
        'avg_return': 0.0,
        'std_return': 0.0,
        'avg_mar': 0.0,
        'parameter_smoothness': 0.0,
        'num_combinations': 0
    }


def compute_drawdown_series(equity_curve: pd.Series) -> pd.Series:
    """
    Compute drawdown series from equity curve.
    
    Args:
        equity_curve: Equity curve series
    
    Returns:
        pd.Series: Drawdown at each point (negative values)
    """
    cummax = equity_curve.cummax()
    drawdown = (equity_curve - cummax) / cummax
    return drawdown


def compute_underwater_curve(equity_curve: pd.Series) -> pd.Series:
    """
    Compute underwater curve (time below previous peak).
    
    Args:
        equity_curve: Equity curve series
    
    Returns:
        pd.Series: Drawdown percentage at each point
    """
    return compute_drawdown_series(equity_curve) * 100

