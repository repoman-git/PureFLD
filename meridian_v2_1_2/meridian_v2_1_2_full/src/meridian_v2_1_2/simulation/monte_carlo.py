"""
Monte Carlo Equity Simulation

Block bootstrap Monte Carlo simulation for equity curves.
Preserves autocorrelation structure while generating probabilistic scenarios.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Tuple
from dataclasses import dataclass


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation"""
    simulations: List[np.ndarray]  # All simulated equity curves
    final_values: np.ndarray  # Final equity values from each simulation
    drawdowns: np.ndarray  # Maximum drawdown from each simulation
    confidence_intervals: Dict[str, float]  # CI percentiles
    stats: Dict[str, Any]  # Summary statistics
    risk_of_ruin: float  # Probability of losing > 50%
    downside_probability: float  # Probability of underperforming initial


def monte_carlo_equity_simulation(
    equity_curve: Union[List, pd.Series, np.ndarray],
    n: int = 500,
    block_size: int = 20,
    seed: int = None
) -> MonteCarloResult:
    """
    Perform block-bootstrap Monte Carlo simulations on equity curve.
    
    Block bootstrap preserves autocorrelation structure in returns while
    generating probabilistic scenarios for robustness testing.
    
    Args:
        equity_curve: Historical equity curve (list, Series, or array)
        n: Number of Monte Carlo simulations to run (default: 500)
        block_size: Size of blocks for bootstrap (default: 20)
        seed: Random seed for reproducibility (optional)
    
    Returns:
        MonteCarloResult: Complete simulation results with statistics
    
    Example:
        >>> equity = [100000, 102000, 101500, 103000, 105000]
        >>> result = monte_carlo_equity_simulation(equity, n=1000)
        >>> print(f"95% CI: {result.confidence_intervals['95']}")
        >>> print(f"Risk of Ruin: {result.risk_of_ruin:.2%}")
    """
    
    # Set random seed if provided
    if seed is not None:
        np.random.seed(seed)
    
    # Convert to numpy array
    equity = np.array(equity_curve)
    
    if len(equity) < 2:
        raise ValueError("Equity curve must have at least 2 points")
    
    # Calculate returns
    returns = np.diff(equity) / equity[:-1]
    
    # Initialize storage for simulations
    simulations = []
    final_values = np.zeros(n)
    max_drawdowns = np.zeros(n)
    
    initial_capital = equity[0]
    n_periods = len(equity) - 1
    
    # Run Monte Carlo simulations
    for i in range(n):
        # Block bootstrap sampling
        sim_returns = _block_bootstrap(returns, n_periods, block_size)
        
        # Generate equity curve from bootstrapped returns
        sim_equity = np.zeros(len(sim_returns) + 1)
        sim_equity[0] = initial_capital
        
        for t in range(len(sim_returns)):
            sim_equity[t + 1] = sim_equity[t] * (1 + sim_returns[t])
        
        # Store results
        simulations.append(sim_equity)
        final_values[i] = sim_equity[-1]
        max_drawdowns[i] = _calculate_max_drawdown(sim_equity)
    
    # Calculate confidence intervals
    percentiles = [5, 10, 25, 50, 75, 90, 95]
    confidence_intervals = {
        f"{p}": np.percentile(final_values, p)
        for p in percentiles
    }
    
    # Calculate risk metrics
    risk_of_ruin = np.mean(final_values < initial_capital * 0.5)
    downside_probability = np.mean(final_values < initial_capital)
    
    # Summary statistics
    stats = {
        'mean_final': float(np.mean(final_values)),
        'median_final': float(np.median(final_values)),
        'std_final': float(np.std(final_values)),
        'mean_drawdown': float(np.mean(max_drawdowns)),
        'median_drawdown': float(np.median(max_drawdowns)),
        'worst_drawdown': float(np.max(max_drawdowns)),
        'best_final': float(np.max(final_values)),
        'worst_final': float(np.min(final_values)),
        'initial_capital': float(initial_capital),
        'original_final': float(equity[-1]),
        'n_simulations': n,
        'block_size': block_size
    }
    
    return MonteCarloResult(
        simulations=simulations,
        final_values=final_values,
        drawdowns=max_drawdowns,
        confidence_intervals=confidence_intervals,
        stats=stats,
        risk_of_ruin=float(risk_of_ruin),
        downside_probability=float(downside_probability)
    )


def _block_bootstrap(data: np.ndarray, n_samples: int, block_size: int) -> np.ndarray:
    """
    Perform block bootstrap sampling to preserve autocorrelation.
    
    Args:
        data: Original time series data
        n_samples: Number of samples to generate
        block_size: Size of each block
    
    Returns:
        Bootstrapped sample array
    """
    n_data = len(data)
    n_blocks = (n_samples + block_size - 1) // block_size
    
    # Sample random starting points for blocks
    bootstrap_sample = []
    
    for _ in range(n_blocks):
        # Random starting point
        start = np.random.randint(0, n_data - block_size + 1)
        # Extract block
        block = data[start:start + block_size]
        bootstrap_sample.extend(block)
    
    # Trim to exact length needed
    return np.array(bootstrap_sample[:n_samples])


def _calculate_max_drawdown(equity: np.ndarray) -> float:
    """
    Calculate maximum drawdown from equity curve.
    
    Args:
        equity: Equity curve array
    
    Returns:
        Maximum drawdown as negative decimal (e.g., -0.15 for 15% drawdown)
    """
    running_max = np.maximum.accumulate(equity)
    drawdown = (equity - running_max) / running_max
    return float(np.min(drawdown))


def calculate_confidence_intervals(
    simulations: List[np.ndarray],
    percentiles: List[float] = [5, 25, 50, 75, 95]
) -> Dict[str, np.ndarray]:
    """
    Calculate confidence interval bands across all time steps.
    
    Useful for creating fan charts showing uncertainty over time.
    
    Args:
        simulations: List of simulated equity curves
        percentiles: Percentiles to calculate (default: [5, 25, 50, 75, 95])
    
    Returns:
        Dictionary mapping percentile to time series array
    
    Example:
        >>> ci = calculate_confidence_intervals(result.simulations)
        >>> # Plot median with 90% CI band
        >>> plt.fill_between(range(len(ci['5'])), ci['5'], ci['95'], alpha=0.3)
    """
    # Stack all simulations into matrix
    sim_matrix = np.array(simulations)
    
    # Calculate percentiles at each time step
    ci_bands = {}
    for p in percentiles:
        ci_bands[str(p)] = np.percentile(sim_matrix, p, axis=0)
    
    return ci_bands


def calculate_risk_of_ruin(
    final_values: np.ndarray,
    initial_capital: float,
    ruin_threshold: float = 0.5
) -> Dict[str, float]:
    """
    Calculate various risk of ruin metrics.
    
    Args:
        final_values: Array of final equity values from simulations
        initial_capital: Starting capital
        ruin_threshold: Threshold for "ruin" (default: 0.5 = 50% loss)
    
    Returns:
        Dictionary with risk metrics
    
    Example:
        >>> risk = calculate_risk_of_ruin(result.final_values, 100000)
        >>> print(f"Chance of 50% loss: {risk['ruin_50']:.2%}")
    """
    ruin_level = initial_capital * ruin_threshold
    
    return {
        f'ruin_{int(ruin_threshold*100)}': float(np.mean(final_values < ruin_level)),
        'prob_loss': float(np.mean(final_values < initial_capital)),
        'prob_gain': float(np.mean(final_values > initial_capital)),
        'expected_value': float(np.mean(final_values)),
        'value_at_risk_95': float(np.percentile(final_values, 5)),
        'conditional_var_95': float(np.mean(final_values[final_values <= np.percentile(final_values, 5)]))
    }


