"""
Market Shock Scenarios for Meridian v2.1.2

Realistic extreme market events.
"""

import numpy as np
import pandas as pd
from typing import Dict


def volatility_explosion(
    prices: pd.DataFrame,
    shock_day: int,
    magnitude: float = 3.0
) -> pd.DataFrame:
    """
    Simulate VIX-like volatility explosion.
    
    Args:
        prices: OHLC DataFrame
        shock_day: Day of shock
        magnitude: Vol multiplier
    
    Returns:
        Prices with vol explosion
    """
    prices = prices.copy()
    
    # Increase volatility after shock
    post_shock = prices.index[shock_day:]
    
    for col in ['high', 'low']:
        if col in prices.columns:
            baseline = prices.loc[post_shock, 'close']
            spread = (prices.loc[post_shock, col] - baseline).abs()
            prices.loc[post_shock, col] = baseline + spread * magnitude
    
    return prices


def flash_crash(
    prices: pd.DataFrame,
    crash_day: int,
    drop_pct: float = 0.15,
    recovery_days: int = 3
) -> pd.DataFrame:
    """
    Simulate flash crash + recovery.
    
    Args:
        prices: OHLC DataFrame
        crash_day: Day of crash
        drop_pct: Magnitude of drop
        recovery_days: Days to recover
    
    Returns:
        Prices with flash crash
    """
    prices = prices.copy()
    
    if crash_day >= len(prices):
        return prices
    
    # Crash
    prices.loc[prices.index[crash_day], 'low'] *= (1 - drop_pct)
    prices.loc[prices.index[crash_day], 'close'] *= (1 - drop_pct * 0.5)
    
    # Gradual recovery
    for i in range(1, min(recovery_days, len(prices) - crash_day)):
        recovery_factor = i / recovery_days
        idx = prices.index[crash_day + i]
        prices.loc[idx, :] *= (1 + drop_pct * 0.3 * recovery_factor)
    
    return prices


def rate_shock(
    yields_df: pd.DataFrame,
    shock_day: int,
    spike_bps: float = 150
) -> pd.DataFrame:
    """
    Simulate real yield spike.
    
    Args:
        yields_df: Real yields DataFrame
        shock_day: Day of shock
        spike_bps: Basis points spike
    
    Returns:
        Yields with shock
    """
    yields_df = yields_df.copy()
    
    if shock_day >= len(yields_df):
        return yields_df
    
    spike = spike_bps / 100  # Convert to decimal
    
    # Apply shock to all yield columns
    for col in yields_df.columns:
        if 'yield' in col.lower() or 'rate' in col.lower():
            yields_df.loc[yields_df.index[shock_day:], col] += spike
    
    return yields_df


def macro_whiplash(
    macro_df: pd.DataFrame,
    whiplash_start: int,
    severity: float = 2.0
) -> pd.DataFrame:
    """
    Simulate macro indicator whiplash.
    
    Args:
        macro_df: Macro DataFrame
        whiplash_start: Start index
        severity: Whiplash magnitude
    
    Returns:
        Macro with whiplash
    """
    macro_df = macro_df.copy()
    
    if whiplash_start >= len(macro_df):
        return macro_df
    
    # Inflation spike
    if 'inflation_yoy' in macro_df.columns:
        macro_df.loc[macro_df.index[whiplash_start:], 'inflation_yoy'] *= severity
    
    # Unemployment spike
    if 'unemployment' in macro_df.columns:
        macro_df.loc[macro_df.index[whiplash_start:], 'unemployment'] += 2.0 * severity
    
    return macro_df


def liquidity_freeze(
    broker,
    freeze_days: int = 5
) -> None:
    """
    Simulate liquidity freeze (no fills).
    
    Args:
        broker: Simulated broker
        freeze_days: Days with no fills
    """
    # This would be implemented in the broker's fill logic
    # For now, just a placeholder
    pass


def cot_data_freeze(
    cot_df: pd.DataFrame,
    freeze_start: int,
    freeze_weeks: int = 4
) -> pd.DataFrame:
    """
    Simulate missing COT data.
    
    Args:
        cot_df: COT DataFrame
        freeze_start: Start week
        freeze_weeks: Number of missing weeks
    
    Returns:
        COT with missing data
    """
    cot_df = cot_df.copy()
    
    if freeze_start >= len(cot_df):
        return cot_df
    
    # Delete rows
    freeze_end = min(freeze_start + freeze_weeks, len(cot_df))
    indices_to_drop = cot_df.index[freeze_start:freeze_end]
    
    cot_df = cot_df.drop(indices_to_drop)
    
    return cot_df


def regime_whiplash(
    regime_series: pd.Series,
    whiplash_start: int,
    whiplash_days: int = 10
) -> pd.Series:
    """
    Simulate rapid regime switching.
    
    Args:
        regime_series: Regime labels
        whiplash_start: Start day
        whiplash_days: Duration
    
    Returns:
        Regime with whiplash
    """
    regime = regime_series.copy()
    
    if whiplash_start >= len(regime):
        return regime
    
    unique_regimes = regime.unique()
    
    # Flip regime every day
    for i in range(whiplash_days):
        idx = whiplash_start + i
        if idx < len(regime):
            regime.iloc[idx] = np.random.choice(unique_regimes)
    
    return regime


def cycle_inversion(
    cycle_series: pd.Series,
    inversion_start: int,
    inversion_days: int = 20
) -> pd.Series:
    """
    Invert cycle (catastrophic for cycle-based strategies).
    
    Args:
        cycle_series: Cycle data
        inversion_start: Start day
        inversion_days: Duration
    
    Returns:
        Inverted cycle
    """
    cycle = cycle_series.copy()
    
    if inversion_start >= len(cycle):
        return cycle
    
    inversion_end = min(inversion_start + inversion_days, len(cycle))
    
    # Invert
    cycle.iloc[inversion_start:inversion_end] *= -1
    
    return cycle


