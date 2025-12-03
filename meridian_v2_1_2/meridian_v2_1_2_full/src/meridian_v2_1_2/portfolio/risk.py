"""
Portfolio Risk Engine

Comprehensive risk analytics for portfolios:
- VaR (Value at Risk)
- CVaR (Conditional VaR / Expected Shortfall)
- Max Drawdown
- Rolling volatility
- Beta to benchmark
- Tail risk analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from scipy import stats


def calculate_var(
    returns: np.ndarray,
    confidence_level: float = 0.95,
    method: str = 'historical'
) -> float:
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns: Array of portfolio returns
        confidence_level: Confidence level (default: 0.95 for 95% VaR)
        method: 'historical' or 'parametric'
    
    Returns:
        VaR value (negative number representing potential loss)
    """
    if method == 'historical':
        return float(np.percentile(returns, (1 - confidence_level) * 100))
    
    elif method == 'parametric':
        mean = np.mean(returns)
        std = np.std(returns)
        z_score = stats.norm.ppf(1 - confidence_level)
        return float(mean + z_score * std)
    
    else:
        raise ValueError(f"Unknown VaR method: {method}")


def calculate_cvar(
    returns: np.ndarray,
    confidence_level: float = 0.95
) -> float:
    """
    Calculate Conditional VaR (CVaR / Expected Shortfall).
    
    Average of all losses beyond VaR threshold.
    
    Args:
        returns: Array of portfolio returns
        confidence_level: Confidence level
    
    Returns:
        CVaR value
    """
    var = calculate_var(returns, confidence_level, method='historical')
    
    # Get all returns worse than VaR
    tail_losses = returns[returns <= var]
    
    if len(tail_losses) > 0:
        return float(np.mean(tail_losses))
    else:
        return var


def calculate_max_drawdown_series(equity: np.ndarray) -> Dict[str, Any]:
    """
    Calculate maximum drawdown and related metrics.
    
    Args:
        equity: Equity curve array
    
    Returns:
        Dictionary with drawdown metrics
    """
    running_max = np.maximum.accumulate(equity)
    drawdown_series = (equity - running_max) / running_max
    
    max_dd = float(np.min(drawdown_series))
    max_dd_idx = int(np.argmin(drawdown_series))
    
    # Find drawdown duration
    peak_idx = int(np.argmax(equity[:max_dd_idx+1]))
    drawdown_duration = max_dd_idx - peak_idx
    
    return {
        'max_drawdown': max_dd,
        'max_dd_date_idx': max_dd_idx,
        'peak_date_idx': peak_idx,
        'drawdown_duration': drawdown_duration,
        'drawdown_series': drawdown_series.tolist()
    }


def calculate_rolling_volatility(
    returns: pd.Series,
    window: int = 30
) -> pd.Series:
    """
    Calculate rolling volatility (annualized).
    
    Args:
        returns: Return series
        window: Rolling window size
    
    Returns:
        Rolling volatility series
    """
    return returns.rolling(window).std() * np.sqrt(252)


def calculate_beta(
    portfolio_returns: np.ndarray,
    benchmark_returns: np.ndarray
) -> float:
    """
    Calculate portfolio beta relative to benchmark.
    
    Args:
        portfolio_returns: Portfolio return array
        benchmark_returns: Benchmark return array (e.g., SPY)
    
    Returns:
        Beta coefficient
    """
    covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
    benchmark_variance = np.var(benchmark_returns)
    
    if benchmark_variance == 0:
        return 0.0
    
    return float(covariance / benchmark_variance)


def tail_risk_analysis(returns: np.ndarray) -> Dict[str, float]:
    """
    Comprehensive tail risk analysis.
    
    Args:
        returns: Portfolio returns
    
    Returns:
        Dictionary with tail risk metrics
    """
    # Sort returns
    sorted_returns = np.sort(returns)
    
    # Percentiles
    p1 = float(np.percentile(returns, 1))
    p5 = float(np.percentile(returns, 5))
    p10 = float(np.percentile(returns, 10))
    
    # Worst returns
    worst_1pct = sorted_returns[:max(1, len(sorted_returns) // 100)]
    worst_5pct = sorted_returns[:max(1, len(sorted_returns) // 20)]
    
    # Skewness and kurtosis
    skewness = float(stats.skew(returns))
    kurtosis = float(stats.kurtosis(returns))
    
    return {
        'var_95': calculate_var(returns, 0.95),
        'var_99': calculate_var(returns, 0.99),
        'cvar_95': calculate_cvar(returns, 0.95),
        'cvar_99': calculate_cvar(returns, 0.99),
        'percentile_1': p1,
        'percentile_5': p5,
        'percentile_10': p10,
        'worst_day': float(np.min(returns)),
        'best_day': float(np.max(returns)),
        'avg_worst_1pct': float(np.mean(worst_1pct)),
        'avg_worst_5pct': float(np.mean(worst_5pct)),
        'skewness': skewness,
        'kurtosis': kurtosis
    }


def comprehensive_risk_report(
    equity_curve: np.ndarray,
    benchmark_equity: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Generate comprehensive risk report for portfolio.
    
    Args:
        equity_curve: Portfolio equity curve
        benchmark_equity: Optional benchmark for beta calculation
    
    Returns:
        Complete risk analysis dictionary
    """
    # Calculate returns
    returns = np.diff(equity_curve) / equity_curve[:-1]
    
    # Drawdown analysis
    dd_metrics = calculate_max_drawdown_series(equity_curve)
    
    # VaR and CVaR
    var_95 = calculate_var(returns, 0.95)
    cvar_95 = calculate_cvar(returns, 0.95)
    
    # Volatility
    daily_vol = float(np.std(returns))
    annual_vol = daily_vol * np.sqrt(252)
    
    # Tail risk
    tail_metrics = tail_risk_analysis(returns)
    
    # Beta (if benchmark provided)
    beta = None
    if benchmark_equity is not None and len(benchmark_equity) == len(equity_curve):
        benchmark_returns = np.diff(benchmark_equity) / benchmark_equity[:-1]
        beta = calculate_beta(returns, benchmark_returns)
    
    return {
        'var_95': var_95,
        'cvar_95': cvar_95,
        'max_drawdown': dd_metrics['max_drawdown'],
        'drawdown_duration': dd_metrics['drawdown_duration'],
        'volatility_daily': daily_vol,
        'volatility_annual': annual_vol,
        'tail_risk': tail_metrics,
        'beta': beta,
        'final_equity': float(equity_curve[-1]),
        'total_return': float((equity_curve[-1] - equity_curve[0]) / equity_curve[0])
    }

