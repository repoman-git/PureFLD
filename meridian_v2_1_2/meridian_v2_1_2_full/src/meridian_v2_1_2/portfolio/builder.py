"""
Portfolio Builder

Combines multiple strategy equity curves into unified portfolio.
Handles normalization, missing data, and partial windows.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional


def build_portfolio(
    component_results: Dict[str, Dict[str, Any]],
    structure: Dict[str, float],
    rebalance_frequency: str = 'monthly'
) -> Dict[str, Any]:
    """
    Build portfolio from component strategy results.
    
    Multiplies strategy equity curves by weights and aggregates.
    
    Args:
        component_results: Dict mapping strategy_name -> backtest_result
        structure: Dict mapping strategy_name -> weight
        rebalance_frequency: 'daily', 'weekly', 'monthly', 'never'
    
    Returns:
        Dictionary with combined equity curve and metrics
    
    Example:
        >>> components = {
        ...     'FLD': {'equity_curve': [100k, 102k, 105k]},
        ...     'Momentum': {'equity_curve': [100k, 101k, 103k]}
        ... }
        >>> weights = {'FLD': 0.6, 'Momentum': 0.4}
        >>> portfolio = build_portfolio(components, weights)
    """
    
    # Extract equity curves
    equity_curves = {}
    for name, result in component_results.items():
        if 'equity_curve' in result:
            equity_curves[name] = np.array(result['equity_curve'])
    
    if not equity_curves:
        raise ValueError("No equity curves found in component results")
    
    # Normalize weights
    total_weight = sum(structure.values())
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero")
    
    normalized_weights = {k: v/total_weight for k, v in structure.items()}
    
    # Find common length (minimum)
    lengths = [len(curve) for curve in equity_curves.values()]
    common_length = min(lengths)
    
    # Trim all curves to common length
    for name in equity_curves:
        equity_curves[name] = equity_curves[name][:common_length]
    
    # Build combined equity curve
    combined_equity = np.zeros(common_length)
    contributions = {}
    
    initial_capital = equity_curves[list(equity_curves.keys())[0]][0]
    
    for name, curve in equity_curves.items():
        weight = normalized_weights.get(name, 0)
        
        # Calculate returns for this component
        returns = np.diff(curve) / curve[:-1]
        returns = np.insert(returns, 0, 0)  # Add zero for first period
        
        # Weight the returns
        weighted_returns = returns * weight
        contributions[name] = weighted_returns
        
        combined_equity += weighted_returns * initial_capital
    
    # Reconstruct equity from weighted returns
    portfolio_equity = np.zeros(common_length)
    portfolio_equity[0] = initial_capital
    
    for i in range(1, common_length):
        total_return = sum(contributions[name][i] for name in equity_curves.keys())
        portfolio_equity[i] = portfolio_equity[i-1] * (1 + total_return)
    
    # Calculate portfolio metrics
    metrics = _calculate_portfolio_metrics(portfolio_equity)
    
    return {
        'equity_curve': portfolio_equity.tolist(),
        'contributions': {k: v.tolist() for k, v in contributions.items()},
        'weights': normalized_weights,
        'metrics': metrics,
        'initial_capital': float(initial_capital),
        'final_capital': float(portfolio_equity[-1])
    }


def _calculate_portfolio_metrics(equity: np.ndarray) -> Dict[str, float]:
    """Calculate portfolio performance metrics"""
    
    if len(equity) < 2:
        return {}
    
    # Returns
    returns = np.diff(equity) / equity[:-1]
    
    # Total return
    total_return = (equity[-1] - equity[0]) / equity[0]
    
    # Max drawdown
    running_max = np.maximum.accumulate(equity)
    drawdowns = (equity - running_max) / running_max
    max_drawdown = float(np.min(drawdowns))
    
    # Volatility
    volatility = float(np.std(returns) * np.sqrt(252))
    
    # Sharpe (assuming daily data)
    mean_return = np.mean(returns) * 252
    sharpe = mean_return / volatility if volatility > 0 else 0
    
    return {
        'total_return': float(total_return),
        'max_drawdown': float(max_drawdown),
        'volatility': float(volatility),
        'sharpe_ratio': float(sharpe),
        'final_equity': float(equity[-1])
    }

