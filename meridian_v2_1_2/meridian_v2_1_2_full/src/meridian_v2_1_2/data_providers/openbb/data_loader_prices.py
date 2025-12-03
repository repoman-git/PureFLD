"""
Price Data Loader for Meridian v2.1.2

Phase 22: Synthetic data generation only - NO external API calls.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional
from .openbb_cache import get_cached_data, save_cached_data


def generate_synthetic_prices(
    symbol: str,
    start: str,
    end: str,
    start_price: float = 100.0,
    volatility: float = 0.02,
    drift: float = 0.0001
) -> pd.DataFrame:
    """
    Generate synthetic OHLC price data.
    
    Used for testing and development when no external data is available.
    
    Args:
        symbol: Ticker symbol
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        start_price: Starting price
        volatility: Daily volatility
        drift: Daily drift (trend)
    
    Returns:
        DataFrame with OHLC data
    """
    # Generate date range
    dates = pd.date_range(start, end, freq='D')
    n = len(dates)
    
    # Generate random walk
    np.random.seed(hash(symbol) % (2**32))  # Deterministic per symbol
    returns = np.random.randn(n) * volatility + drift
    
    # Compute close prices
    close = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC from close
    high = close * (1 + np.abs(np.random.randn(n)) * volatility * 0.5)
    low = close * (1 - np.abs(np.random.randn(n)) * volatility * 0.5)
    open_price = close * (1 + np.random.randn(n) * volatility * 0.3)
    
    # Generate volume
    volume = np.random.randint(1000000, 10000000, n)
    
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    return df


def load_prices(
    symbol: str,
    start: str,
    end: str,
    use_cache: bool = True,
    cache_path: str = "cache/openbb/"
) -> pd.DataFrame:
    """
    Load price data for symbol.
    
    Phase 22: Returns synthetic data only.
    Phase 29+: Will fetch from OpenBB API.
    
    Args:
        symbol: Ticker symbol
        start: Start date
        end: End date
        use_cache: Whether to use cache
        cache_path: Cache directory
    
    Returns:
        DataFrame with OHLC data
    """
    # Check cache
    if use_cache:
        cache_key = f"prices_{symbol}_{start}_{end}"
        cached = get_cached_data(cache_key, cache_path)
        if cached is not None:
            return cached
    
    # Generate synthetic data (Phase 22 mode)
    df = generate_synthetic_prices(symbol, start, end)
    
    # Cache it
    if use_cache:
        save_cached_data(cache_key, df, cache_path)
    
    return df

