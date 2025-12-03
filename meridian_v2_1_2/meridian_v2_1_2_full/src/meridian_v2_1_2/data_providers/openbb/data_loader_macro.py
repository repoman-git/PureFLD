"""
Macro Data Loader for Meridian v2.1.2

Phase 22: Synthetic macro data - NO external API calls.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict
from .openbb_cache import get_cached_data, save_cached_data


def generate_synthetic_macro(
    start: str,
    end: str
) -> pd.DataFrame:
    """
    Generate synthetic macro data.
    
    Includes:
    - CPI (inflation)
    - GDP growth
    - Unemployment
    - Fed Funds Rate
    - 10Y Treasury Yield
    
    Args:
        start: Start date
        end: End date
    
    Returns:
        DataFrame with macro indicators
    """
    # Generate monthly dates (macro data is typically monthly)
    dates = pd.date_range(start, end, freq='ME')  # Month-end frequency
    n = len(dates)
    
    np.random.seed(42)  # Fixed seed for macro data
    
    # CPI (inflation) - trending upward with noise
    cpi = 250 + np.cumsum(np.random.randn(n) * 0.5 + 0.3)
    
    # GDP growth (quarterly-ish)
    gdp_growth = 2.0 + np.random.randn(n) * 0.5
    
    # Unemployment
    unemployment = 4.0 + np.random.randn(n) * 0.3
    unemployment = np.clip(unemployment, 3.0, 10.0)
    
    # Fed Funds Rate
    fed_funds = 2.5 + np.cumsum(np.random.randn(n) * 0.1)
    fed_funds = np.clip(fed_funds, 0.0, 5.0)
    
    # 10Y Treasury Yield
    treasury_10y = 3.0 + np.cumsum(np.random.randn(n) * 0.1)
    treasury_10y = np.clip(treasury_10y, 1.0, 5.0)
    
    df = pd.DataFrame({
        'cpi': cpi,
        'gdp_growth': gdp_growth,
        'unemployment': unemployment,
        'fed_funds_rate': fed_funds,
        'treasury_10y': treasury_10y,
        'inflation_yoy': np.gradient(cpi) / cpi * 100 * 12  # Annualized
    }, index=dates)
    
    return df


def load_macro_data(
    start: str,
    end: str,
    use_cache: bool = True,
    cache_path: str = "cache/openbb/"
) -> pd.DataFrame:
    """
    Load macro economic data.
    
    Phase 22: Returns synthetic data only.
    Phase 29+: Will fetch from FRED/OpenBB.
    
    Args:
        start: Start date
        end: End date
        use_cache: Whether to use cache
        cache_path: Cache directory
    
    Returns:
        DataFrame with macro indicators
    """
    # Check cache
    if use_cache:
        cache_key = f"macro_{start}_{end}"
        cached = get_cached_data(cache_key, cache_path)
        if cached is not None:
            return cached
    
    # Generate synthetic data
    df = generate_synthetic_macro(start, end)
    
    # Cache it
    if use_cache:
        save_cached_data(cache_key, df, cache_path)
    
    return df

