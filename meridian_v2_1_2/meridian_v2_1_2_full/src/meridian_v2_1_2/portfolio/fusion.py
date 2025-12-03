"""
Multi-Strategy Fusion Module

Combine multiple strategies into blended portfolios with weighted allocation.
Supports equity curve blending, return fusion, and combined metrics calculation.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FusionResult:
    """Results from strategy fusion"""
    blended_equity: np.ndarray  # Combined equity curve
    blended_returns: np.ndarray  # Combined returns
    weights: Dict[str, float]  # Strategy weights
    metrics: Dict[str, float]  # Combined performance metrics
    individual_contributions: Dict[str, np.ndarray]  # Per-strategy contributions
    correlation_matrix: np.ndarray  # Strategy correlation matrix


def blend_equity_curves(
    curves: Dict[str, Union[List, np.ndarray]],
    weights: Optional[Dict[str, float]] = None,
    normalize_weights: bool = True
) -> FusionResult:
    """
    Combine multiple equity curves using weighted allocation.
    
    Blends strategies at the equity level, properly handling correlation
    and computing combined metrics.
    
    Args:
        curves: Dictionary mapping strategy_name -> equity_curve
        weights: Dictionary mapping strategy_name -> weight (optional, equal if None)
        normalize_weights: Whether to normalize weights to sum to 1.0
    
    Returns:
        FusionResult: Complete fusion results with blended curve and metrics
    
    Example:
        >>> curves = {
        ...     'FLD': [100000, 102000, 105000, 103000],
        ...     'COT': [100000, 101000, 102000, 104000],
        ... }
        >>> result = blend_equity_curves(curves, weights={'FLD': 0.6, 'COT': 0.4})
        >>> print(f"Blended Sharpe: {result.metrics['sharpe_ratio']:.2f}")
    """
    
    if not curves or len(curves) == 0:
        raise ValueError("Must provide at least one equity curve")
    
    # Get strategy names
    strategy_names = list(curves.keys())
    n_strategies = len(strategy_names)
    
    # Convert curves to numpy arrays
    equity_arrays = {name: np.array(curve) for name, curve in curves.items()}
    
    # Validate all curves have same length
    lengths = [len(curve) for curve in equity_arrays.values()]
    if len(set(lengths)) > 1:
        raise ValueError(f"All equity curves must have same length. Got: {lengths}")
    
    curve_length = lengths[0]
    
    # Set default equal weights if not provided
    if weights is None:
        weights = {name: 1.0 / n_strategies for name in strategy_names}
    
    # Normalize weights if requested
    if normalize_weights:
        total_weight = sum(weights.values())
        if total_weight == 0:
            raise ValueError("Total weight cannot be zero")
        weights = {name: w / total_weight for name, w in weights.items()}
    
    # Validate weights match strategies
    if set(weights.keys()) != set(strategy_names):
        raise ValueError("Weights must be provided for all strategies")
    
    # Calculate returns for each strategy
    returns_dict = {}
    for name, equity in equity_arrays.items():
        if len(equity) < 2:
            returns_dict[name] = np.array([])
        else:
            returns_dict[name] = np.diff(equity) / equity[:-1]
    
    # Calculate weighted blended returns
    n_returns = curve_length - 1
    blended_returns = np.zeros(n_returns)
    individual_contributions = {}
    
    for name in strategy_names:
        weight = weights[name]
        strategy_returns = returns_dict[name]
        contribution = weight * strategy_returns
        blended_returns += contribution
        individual_contributions[name] = contribution
    
    # Generate blended equity curve
    initial_capital = np.mean([equity[0] for equity in equity_arrays.values()])
    blended_equity = np.zeros(curve_length)
    blended_equity[0] = initial_capital
    
    for i in range(n_returns):
        blended_equity[i + 1] = blended_equity[i] * (1 + blended_returns[i])
    
    # Calculate correlation matrix
    returns_matrix = np.array([returns_dict[name] for name in strategy_names])
    correlation_matrix = np.corrcoef(returns_matrix)
    
    # Calculate combined metrics
    metrics = _calculate_fusion_metrics(
        blended_equity, 
        blended_returns, 
        equity_arrays,
        weights
    )
    
    return FusionResult(
        blended_equity=blended_equity,
        blended_returns=blended_returns,
        weights=weights,
        metrics=metrics,
        individual_contributions=individual_contributions,
        correlation_matrix=correlation_matrix
    )


def optimize_weights(
    curves: Dict[str, Union[List, np.ndarray]],
    objective: str = 'sharpe',
    constraints: Optional[Dict[str, Tuple[float, float]]] = None
) -> Dict[str, float]:
    """
    Optimize strategy weights to maximize objective function.
    
    Args:
        curves: Dictionary of equity curves
        objective: Optimization objective ('sharpe', 'return', 'min_dd')
        constraints: Optional weight constraints per strategy (min, max)
    
    Returns:
        Dictionary of optimal weights
    
    Example:
        >>> curves = {'FLD': [...], 'COT': [...], 'TDOM': [...]}
        >>> weights = optimize_weights(curves, objective='sharpe')
        >>> print(weights)  # {'FLD': 0.4, 'COT': 0.35, 'TDOM': 0.25}
    """
    
    strategy_names = list(curves.keys())
    n_strategies = len(strategy_names)
    
    # Set default constraints (0 to 1 for each strategy)
    if constraints is None:
        constraints = {name: (0.0, 1.0) for name in strategy_names}
    
    # Simple grid search optimization (can be replaced with scipy.optimize)
    best_weights = None
    best_score = -np.inf
    
    # Try different weight combinations
    n_samples = 50
    for _ in range(n_samples):
        # Generate random weights
        test_weights = {}
        remaining = 1.0
        
        for i, name in enumerate(strategy_names[:-1]):
            min_w, max_w = constraints.get(name, (0.0, 1.0))
            max_possible = min(max_w, remaining)
            weight = np.random.uniform(min_w, max_possible)
            test_weights[name] = weight
            remaining -= weight
        
        # Last strategy gets remainder
        last_name = strategy_names[-1]
        test_weights[last_name] = max(0, remaining)
        
        # Evaluate
        try:
            result = blend_equity_curves(curves, test_weights, normalize_weights=False)
            
            if objective == 'sharpe':
                score = result.metrics.get('sharpe_ratio', -999)
            elif objective == 'return':
                score = result.metrics.get('total_return', -999)
            elif objective == 'min_dd':
                score = -result.metrics.get('max_drawdown', 999)  # Minimize drawdown
            else:
                score = result.metrics.get('sharpe_ratio', -999)
            
            if score > best_score:
                best_score = score
                best_weights = test_weights
                
        except:
            continue
    
    # Normalize best weights
    if best_weights:
        total = sum(best_weights.values())
        best_weights = {name: w / total for name, w in best_weights.items()}
    else:
        # Fallback to equal weights
        best_weights = {name: 1.0 / n_strategies for name in strategy_names}
    
    return best_weights


def _calculate_fusion_metrics(
    blended_equity: np.ndarray,
    blended_returns: np.ndarray,
    individual_curves: Dict[str, np.ndarray],
    weights: Dict[str, float]
) -> Dict[str, float]:
    """Calculate performance metrics for blended portfolio"""
    
    if len(blended_returns) == 0:
        return {}
    
    # Total return
    initial = blended_equity[0]
    final = blended_equity[-1]
    total_return = (final - initial) / initial
    
    # Max drawdown
    running_max = np.maximum.accumulate(blended_equity)
    drawdowns = (blended_equity - running_max) / running_max
    max_drawdown = float(np.min(drawdowns))
    
    # Sharpe ratio (annualized, assuming daily returns)
    mean_return = np.mean(blended_returns)
    std_return = np.std(blended_returns)
    sharpe_ratio = (mean_return / std_return * np.sqrt(252)) if std_return > 0 else 0.0
    
    # Win rate
    winning_periods = np.sum(blended_returns > 0)
    win_rate = winning_periods / len(blended_returns) if len(blended_returns) > 0 else 0.0
    
    # Volatility (annualized)
    volatility = std_return * np.sqrt(252)
    
    # Calmar ratio
    calmar_ratio = total_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
    
    return {
        'total_return': float(total_return),
        'max_drawdown': float(max_drawdown),
        'sharpe_ratio': float(sharpe_ratio),
        'win_rate': float(win_rate),
        'volatility': float(volatility),
        'calmar_ratio': float(calmar_ratio),
        'final_equity': float(final),
        'initial_equity': float(initial),
        'n_strategies': len(weights),
        'effective_n': float(1 / sum(w**2 for w in weights.values()))  # Diversification measure
    }

