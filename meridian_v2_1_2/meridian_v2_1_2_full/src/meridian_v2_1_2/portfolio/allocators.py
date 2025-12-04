"""
Portfolio Allocators

Multiple allocation strategies for portfolio construction:
- Mean-Variance Optimization (MPT)
- Minimum Variance
- Risk Parity
- Hierarchical Risk Parity (HRP)
- Kelly Criterion
- Ensemble (combines multiple allocators)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from scipy.optimize import minimize
from scipy.cluster.hierarchy import linkage, dendrogram
import warnings
warnings.filterwarnings('ignore')


def mean_variance_optimization(
    returns: pd.DataFrame,
    target_return: Optional[float] = None,
    risk_free_rate: float = 0.02
) -> Dict[str, Any]:
    """
    Mean-Variance Optimization (Markowitz).
    
    Maximizes Sharpe ratio or achieves target return with minimum variance.
    
    Args:
        returns: DataFrame with returns for each asset
        target_return: Target portfolio return (optional, maximizes Sharpe if None)
        risk_free_rate: Risk-free rate for Sharpe calculation
    
    Returns:
        Dictionary with weights and details
    """
    mean_returns = returns.mean() * 252  # Annualize
    cov_matrix = returns.cov() * 252
    
    n_assets = len(returns.columns)
    
    def portfolio_stats(weights):
        port_return = np.dot(weights, mean_returns)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = (port_return - risk_free_rate) / port_vol if port_vol > 0 else 0
        return port_return, port_vol, sharpe
    
    def neg_sharpe(weights):
        return -portfolio_stats(weights)[2]
    
    # Constraints
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    
    if target_return:
        constraints.append({
            'type': 'eq',
            'fun': lambda w: portfolio_stats(w)[0] - target_return
        })
    
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_guess = np.array([1/n_assets] * n_assets)
    
    # Optimize
    result = minimize(
        neg_sharpe,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if result.success:
        weights = result.x
        ret, vol, sharpe = portfolio_stats(weights)
        
        return {
            'weights': dict(zip(returns.columns, weights)),
            'details': {
                'expected_return': float(ret),
                'volatility': float(vol),
                'sharpe_ratio': float(sharpe),
                'method': 'Mean-Variance Optimization'
            }
        }
    else:
        # Fallback to equal weights
        return equal_weight(returns)


def minimum_variance(returns: pd.DataFrame) -> Dict[str, Any]:
    """
    Minimum Variance Portfolio.
    
    Finds allocation with lowest portfolio variance.
    """
    cov_matrix = returns.cov() * 252
    n_assets = len(returns.columns)
    
    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))
    
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = tuple((0, 1) for _ in range(n_assets))
    initial_guess = np.array([1/n_assets] * n_assets)
    
    result = minimize(
        portfolio_variance,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if result.success:
        weights = result.x
        vol = np.sqrt(portfolio_variance(weights))
        
        return {
            'weights': dict(zip(returns.columns, weights)),
            'details': {
                'volatility': float(vol),
                'method': 'Minimum Variance'
            }
        }
    else:
        return equal_weight(returns)


def risk_parity(returns: pd.DataFrame) -> Dict[str, Any]:
    """
    Risk Parity allocation.
    
    Each asset contributes equally to portfolio risk.
    """
    cov_matrix = returns.cov() * 252
    n_assets = len(returns.columns)
    
    def risk_contribution(weights):
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        marginal_contrib = np.dot(cov_matrix, weights)
        contrib = weights * marginal_contrib / portfolio_vol
        return contrib
    
    def risk_parity_objective(weights):
        contrib = risk_contribution(weights)
        target = np.mean(contrib)
        return np.sum((contrib - target) ** 2)
    
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
    bounds = tuple((0.001, 1) for _ in range(n_assets))
    initial_guess = np.array([1/n_assets] * n_assets)
    
    result = minimize(
        risk_parity_objective,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )
    
    if result.success:
        weights = result.x / np.sum(result.x)  # Normalize
        
        return {
            'weights': dict(zip(returns.columns, weights)),
            'details': {
                'method': 'Risk Parity',
                'risk_contributions': dict(zip(returns.columns, risk_contribution(weights)))
            }
        }
    else:
        return equal_weight(returns)


def hierarchical_risk_parity(returns: pd.DataFrame) -> Dict[str, Any]:
    """
    Hierarchical Risk Parity (HRP).
    
    Uses hierarchical clustering to build diversified portfolio.
    More robust to estimation error than MPT.
    """
    cov_matrix = returns.cov() * 252
    corr_matrix = returns.corr()
    
    # Compute distance matrix
    dist = np.sqrt((1 - corr_matrix) / 2)
    
    # Hierarchical clustering
    link = linkage(dist, method='single')
    
    # Get cluster structure
    n_assets = len(returns.columns)
    
    # Recursive bisection for weights
    weights = np.ones(n_assets)
    _recursive_bisection(weights, cov_matrix, list(range(n_assets)))
    
    # Normalize
    weights = weights / np.sum(weights)
    
    return {
        'weights': dict(zip(returns.columns, weights)),
        'details': {
            'method': 'Hierarchical Risk Parity',
            'clustering': 'complete'
        }
    }


def kelly_criterion(
    returns: pd.DataFrame,
    max_leverage: float = 1.0,
    shrinkage: float = 0.5
) -> Dict[str, Any]:
    """
    Kelly Criterion allocation (bounded).
    
    Maximizes log utility, bounded for practical use.
    
    Args:
        returns: Asset returns
        max_leverage: Maximum portfolio leverage
        shrinkage: Shrink Kelly by this factor (0.5 = half-Kelly)
    
    Returns:
        Allocation dictionary
    """
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    
    try:
        # Kelly weights: inv(Cov) * mean_returns
        inv_cov = np.linalg.inv(cov_matrix)
        kelly_weights = np.dot(inv_cov, mean_returns)
        
        # Apply shrinkage
        kelly_weights = kelly_weights * shrinkage
        
        # Bound leverage
        total_leverage = np.sum(np.abs(kelly_weights))
        if total_leverage > max_leverage:
            kelly_weights = kelly_weights * (max_leverage / total_leverage)
        
        # Normalize to positive weights only (no short)
        kelly_weights = np.maximum(kelly_weights, 0)
        kelly_weights = kelly_weights / np.sum(kelly_weights) if np.sum(kelly_weights) > 0 else np.ones(len(kelly_weights)) / len(kelly_weights)
        
        return {
            'weights': dict(zip(returns.columns, kelly_weights)),
            'details': {
                'method': 'Kelly Criterion',
                'shrinkage': shrinkage,
                'max_leverage': max_leverage
            }
        }
        
    except np.linalg.LinAlgError:
        return equal_weight(returns)


def ensemble_allocator(
    returns: pd.DataFrame,
    methods: List[str] = None,
    ensemble_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Ensemble allocator - combines multiple allocation methods.
    
    Args:
        returns: Asset returns
        methods: List of methods to ensemble (default: all)
        ensemble_weights: Weights for each method (default: equal)
    
    Returns:
        Blended allocation
    """
    if methods is None:
        methods = ['mvo', 'minvar', 'riskparity', 'kelly']
    
    if ensemble_weights is None:
        ensemble_weights = {m: 1/len(methods) for m in methods}
    
    # Get allocations from each method
    allocations = {}
    
    if 'mvo' in methods:
        allocations['mvo'] = mean_variance_optimization(returns)['weights']
    if 'minvar' in methods:
        allocations['minvar'] = minimum_variance(returns)['weights']
    if 'riskparity' in methods:
        allocations['riskparity'] = risk_parity(returns)['weights']
    if 'hrp' in methods:
        allocations['hrp'] = hierarchical_risk_parity(returns)['weights']
    if 'kelly' in methods:
        allocations['kelly'] = kelly_criterion(returns)['weights']
    
    # Blend allocations
    assets = returns.columns
    final_weights = {}
    
    for asset in assets:
        weighted_sum = 0
        for method, alloc in allocations.items():
            method_weight = ensemble_weights.get(method, 0)
            asset_weight = alloc.get(asset, 0)
            weighted_sum += method_weight * asset_weight
        
        final_weights[asset] = weighted_sum
    
    # Normalize
    total = sum(final_weights.values())
    if total > 0:
        final_weights = {k: v/total for k, v in final_weights.items()}
    
    return {
        'weights': final_weights,
        'details': {
            'method': 'Ensemble',
            'methods_used': methods,
            'ensemble_weights': ensemble_weights
        }
    }


def equal_weight(returns: pd.DataFrame) -> Dict[str, Any]:
    """Equal weight allocation (1/N)"""
    n = len(returns.columns)
    weights = {col: 1/n for col in returns.columns}
    
    return {
        'weights': weights,
        'details': {'method': 'Equal Weight'}
    }


def _recursive_bisection(weights, cov_matrix, items):
    """Helper for HRP recursive bisection"""
    if len(items) == 1:
        return
    
    # Split into two clusters (simplified)
    mid = len(items) // 2
    left = items[:mid]
    right = items[mid:]
    
    # Calculate cluster variances
    if len(left) > 0 and len(right) > 0:
        left_var = _cluster_variance(cov_matrix, left)
        right_var = _cluster_variance(cov_matrix, right)
        
        # Allocate inversely to variance
        alpha = 1 - left_var / (left_var + right_var)
        
        weights[left] *= alpha
        weights[right] *= (1 - alpha)
        
        # Recurse
        _recursive_bisection(weights, cov_matrix, left)
        _recursive_bisection(weights, cov_matrix, right)


def _cluster_variance(cov_matrix, items):
    """Calculate variance of a cluster"""
    if len(items) == 0:
        return 0
    
    sub_cov = cov_matrix[np.ix_(items, items)]
    ivp = 1 / np.diag(sub_cov)
    ivp = ivp / np.sum(ivp)
    
    return np.dot(ivp, np.dot(sub_cov, ivp))


