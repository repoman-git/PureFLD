"""
Real Yields Data Loader for Meridian v2.1.2

Phase 22: Synthetic real yields data - NO external API calls.
Critical for LTPZ (inverse gold) behavior modeling.
"""

import pandas as pd
import numpy as np
from typing import Optional
from .openbb_cache import get_cached_data, save_cached_data


def generate_synthetic_yields(
    start: str,
    end: str
) -> pd.DataFrame:
    """
    Generate synthetic real yields data.
    
    Real Yield = Nominal Yield - Expected Inflation
    
    Critical for:
    - LTPZ inverse-gold logic
    - Regime classification
    - Gold/LTPZ pair dynamics
    
    Args:
        start: Start date
        end: End date
    
    Returns:
        DataFrame with real yields data
    """
    # Generate daily dates
    dates = pd.date_range(start, end, freq='D')
    n = len(dates)
    
    np.random.seed(123)  # Fixed seed for yields
    
    # 10Y nominal yield
    nominal_10y = 3.5 + np.cumsum(np.random.randn(n) * 0.02)
    nominal_10y = np.clip(nominal_10y, 0.5, 5.0)
    
    # Expected inflation (from breakeven)
    expected_inflation = 2.5 + np.cumsum(np.random.randn(n) * 0.01)
    expected_inflation = np.clip(expected_inflation, 1.0, 4.0)
    
    # Real yield = nominal - inflation
    real_yield_10y = nominal_10y - expected_inflation
    
    # 5Y real yield (typically lower)
    real_yield_5y = real_yield_10y - 0.3 + np.random.randn(n) * 0.1
    
    # TIPS spread (real yield indicator)
    tips_spread = real_yield_10y + np.random.randn(n) * 0.05
    
    df = pd.DataFrame({
        'nominal_10y': nominal_10y,
        'expected_inflation': expected_inflation,
        'real_yield_10y': real_yield_10y,
        'real_yield_5y': real_yield_5y,
        'tips_spread': tips_spread,
        'real_yield_regime': np.where(real_yield_10y > 1.0, 'rising', 'falling')
    }, index=dates)
    
    return df


def load_real_yields(
    start: str,
    end: str,
    use_cache: bool = True,
    cache_path: str = "cache/openbb/"
) -> pd.DataFrame:
    """
    Load real yields data.
    
    Phase 22: Returns synthetic data only.
    Phase 29+: Will fetch from FRED/Treasury via OpenBB.
    
    Args:
        start: Start date
        end: End date
        use_cache: Whether to use cache
        cache_path: Cache directory
    
    Returns:
        DataFrame with real yields
    """
    # Check cache
    if use_cache:
        cache_key = f"real_yields_{start}_{end}"
        cached = get_cached_data(cache_key, cache_path)
        if cached is not None:
            return cached
    
    # Generate synthetic data
    df = generate_synthetic_yields(start, end)
    
    # Cache it
    if use_cache:
        save_cached_data(cache_key, df, cache_path)
    
    return df


