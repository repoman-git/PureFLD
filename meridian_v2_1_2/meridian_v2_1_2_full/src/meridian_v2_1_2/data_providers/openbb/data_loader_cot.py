"""
COT Data Loader for Meridian v2.1.2

Phase 22: Synthetic COT data - NO external API calls.
"""

import pandas as pd
import numpy as np
from typing import Optional
from .openbb_cache import get_cached_data, save_cached_data


def generate_synthetic_cot(
    symbol: str,
    start: str,
    end: str
) -> pd.DataFrame:
    """
    Generate synthetic COT (Commitment of Traders) data.
    
    Generates weekly data with:
    - Commercials (hedgers)
    - Non-commercials (speculators)
    - Net positions
    
    Args:
        symbol: Symbol (e.g., "GOLD")
        start: Start date
        end: End date
    
    Returns:
        DataFrame with COT data
    """
    # Generate weekly dates (COT reports on Tuesdays)
    dates = pd.date_range(start, end, freq='W-TUE')
    n = len(dates)
    
    # Generate synthetic positions
    np.random.seed(hash(symbol) % (2**32))
    
    # Commercials (tend to be contrarian)
    commercials_long = 50000 + np.cumsum(np.random.randn(n) * 1000)
    commercials_short = 45000 + np.cumsum(np.random.randn(n) * 1000)
    
    # Non-commercials (tend to follow trends)
    non_comm_long = 30000 + np.cumsum(np.random.randn(n) * 500)
    non_comm_short = 28000 + np.cumsum(np.random.randn(n) * 500)
    
    df = pd.DataFrame({
        'commercials_long': commercials_long,
        'commercials_short': commercials_short,
        'commercials_net': commercials_long - commercials_short,
        'non_commercials_long': non_comm_long,
        'non_commercials_short': non_comm_short,
        'non_commercials_net': non_comm_long - non_comm_short,
        'open_interest': commercials_long + commercials_short + non_comm_long + non_comm_short
    }, index=dates)
    
    return df


def load_cot_data(
    symbol: str,
    start: str,
    end: str,
    use_cache: bool = True,
    cache_path: str = "cache/openbb/"
) -> pd.DataFrame:
    """
    Load COT data for symbol.
    
    Phase 22: Returns synthetic data only.
    Phase 29+: Will fetch from CFTC via OpenBB.
    
    Args:
        symbol: Symbol
        start: Start date
        end: End date
        use_cache: Whether to use cache
        cache_path: Cache directory
    
    Returns:
        DataFrame with COT data
    """
    # Check cache
    if use_cache:
        cache_key = f"cot_{symbol}_{start}_{end}"
        cached = get_cached_data(cache_key, cache_path)
        if cached is not None:
            return cached
    
    # Generate synthetic data
    df = generate_synthetic_cot(symbol, start, end)
    
    # Cache it
    if use_cache:
        save_cached_data(cache_key, df, cache_path)
    
    return df


