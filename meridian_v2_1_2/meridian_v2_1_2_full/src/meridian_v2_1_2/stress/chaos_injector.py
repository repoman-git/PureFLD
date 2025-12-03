"""
Chaos Injector for Meridian v2.1.2

Controlled data corruption and fault injection.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
import random


def inject_price_gaps(
    prices: pd.DataFrame,
    severity: float = 0.5,
    seed: int = None
) -> pd.DataFrame:
    """
    Inject random price gaps (opens/closes).
    
    Args:
        prices: OHLC DataFrame
        severity: Shock magnitude (0-1)
        seed: Random seed
    
    Returns:
        Modified prices with gaps
    """
    if seed is not None:
        np.random.seed(seed)
    
    prices = prices.copy()
    n = len(prices)
    
    # Number of gaps to inject
    num_gaps = max(1, int(n * 0.05 * severity))
    
    gap_indices = np.random.choice(n, size=num_gaps, replace=False)
    
    for idx in gap_indices:
        # Random gap direction and size
        gap_size = np.random.uniform(0.02, 0.10) * severity
        direction = np.random.choice([-1, 1])
        
        # Apply gap
        prices.iloc[idx:, :] *= (1 + direction * gap_size)
    
    return prices


def inject_missing_bars(
    prices: pd.DataFrame,
    severity: float = 0.5,
    seed: int = None
) -> pd.DataFrame:
    """
    Delete random bars (missing data).
    
    Args:
        prices: OHLC DataFrame
        severity: Fraction of bars to delete
        seed: Random seed
    
    Returns:
        Prices with missing bars
    """
    if seed is not None:
        random.seed(seed)
    
    prices = prices.copy()
    n = len(prices)
    
    # Number of bars to delete
    num_missing = max(1, int(n * 0.10 * severity))
    
    indices_to_drop = random.sample(range(n), num_missing)
    
    prices = prices.drop(prices.index[indices_to_drop])
    
    return prices


def inject_nan_bursts(
    prices: pd.DataFrame,
    severity: float = 0.5,
    seed: int = None
) -> pd.DataFrame:
    """
    Inject NaN bursts (data corruption).
    
    Args:
        prices: OHLC DataFrame
        severity: Corruption intensity
        seed: Random seed
    
    Returns:
        Prices with NaN bursts
    """
    if seed is not None:
        np.random.seed(seed)
    
    prices = prices.copy()
    n = len(prices)
    
    # Number of NaN bursts
    num_bursts = max(1, int(3 * severity))
    
    for _ in range(num_bursts):
        burst_start = np.random.randint(0, n - 5)
        burst_length = np.random.randint(1, int(7 * severity) + 1)
        
        # Wipe random columns
        cols_to_wipe = np.random.choice(
            prices.columns,
            size=min(2, len(prices.columns)),
            replace=False
        )
        
        prices.loc[prices.index[burst_start:burst_start+burst_length], cols_to_wipe] = np.nan
    
    return prices


def inject_cycle_breaks(
    cycle_series: pd.Series,
    severity: float = 0.5,
    seed: int = None
) -> pd.Series:
    """
    Break cycle structure (flatten, invert, corrupt).
    
    Args:
        cycle_series: Cycle data
        severity: Break intensity
        seed: Random seed
    
    Returns:
        Corrupted cycle
    """
    if seed is not None:
        np.random.seed(seed)
    
    cycle = cycle_series.copy()
    n = len(cycle)
    
    break_type = np.random.choice(['flatten', 'invert', 'noise'])
    
    if break_type == 'flatten':
        # Flatten amplitude
        start_idx = np.random.randint(0, n // 2)
        end_idx = start_idx + int(n * 0.3 * severity)
        cycle.iloc[start_idx:end_idx] *= (1 - severity * 0.9)
    
    elif break_type == 'invert':
        # Invert cycle
        start_idx = np.random.randint(0, n // 2)
        end_idx = start_idx + int(n * 0.2 * severity)
        cycle.iloc[start_idx:end_idx] *= -1
    
    elif break_type == 'noise':
        # Add extreme noise
        noise = np.random.randn(n) * cycle.std() * severity * 2
        cycle += noise
    
    return cycle


def inject_regime_corruption(
    regime_series: pd.Series,
    severity: float = 0.5,
    seed: int = None
) -> pd.Series:
    """
    Corrupt regime labels (erratic switching).
    
    Args:
        regime_series: Regime labels
        severity: Corruption level
        seed: Random seed
    
    Returns:
        Corrupted regimes
    """
    if seed is not None:
        np.random.seed(seed)
    
    regime = regime_series.copy()
    n = len(regime)
    
    # Number of erratic flips
    num_flips = int(n * 0.05 * severity)
    
    flip_indices = np.random.choice(n, size=num_flips, replace=False)
    
    # Randomly flip regimes
    unique_regimes = regime.unique()
    
    for idx in flip_indices:
        new_regime = np.random.choice(unique_regimes)
        regime.iloc[idx] = new_regime
    
    return regime


def inject_correlation_breaks(
    prices_dict: Dict[str, pd.DataFrame],
    severity: float = 0.5,
    seed: int = None
) -> Dict[str, pd.DataFrame]:
    """
    Break correlations between assets (GLD/LTPZ).
    
    Args:
        prices_dict: Dict of symbol -> prices
        severity: Break intensity
        seed: Random seed
    
    Returns:
        Prices with broken correlations
    """
    if seed is not None:
        np.random.seed(seed)
    
    prices_dict = {k: v.copy() for k, v in prices_dict.items()}
    
    # Force positive correlation on GLD/LTPZ
    if 'GLD' in prices_dict and 'LTPZ' in prices_dict:
        gld = prices_dict['GLD']
        ltpz = prices_dict['LTPZ']
        
        # Make them move together (break inverse relationship)
        gld_returns = gld['close'].pct_change()
        
        # Apply correlation break
        ltpz['close'] = ltpz['close'].iloc[0] * (1 + gld_returns * severity).cumprod()
        ltpz['open'] = ltpz['close'].shift(1).fillna(ltpz['close'].iloc[0])
        ltpz['high'] = ltpz[['open', 'close']].max(axis=1) * 1.01
        ltpz['low'] = ltpz[['open', 'close']].min(axis=1) * 0.99
        
        prices_dict['LTPZ'] = ltpz
    
    return prices_dict


def inject_oms_corruption(
    orders: list,
    severity: float = 0.5,
    seed: int = None
) -> list:
    """
    Corrupt OMS logs (duplicate/missing orders).
    
    Args:
        orders: List of order dicts
        severity: Corruption level
        seed: Random seed
    
    Returns:
        Corrupted orders
    """
    if seed is not None:
        random.seed(seed)
    
    orders = orders.copy()
    
    if not orders:
        return orders
    
    # Duplicate some orders
    num_duplicates = int(len(orders) * 0.1 * severity)
    for _ in range(num_duplicates):
        if orders:
            order_to_dup = random.choice(orders)
            orders.append(order_to_dup.copy())
    
    # Delete some orders
    num_deletions = int(len(orders) * 0.05 * severity)
    for _ in range(num_deletions):
        if len(orders) > 1:
            orders.pop(random.randint(0, len(orders) - 1))
    
    return orders

