"""
EOD Data Fetcher for Meridian v2.1.2

Fetch daily bar data for end-of-day analysis.
"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def fetch_eod_data(
    symbols: List[str],
    lookback_days: int = 500,
    source: str = "local"
) -> Dict[str, pd.DataFrame]:
    """
    Fetch end-of-day data for symbols.
    
    In production, this would connect to:
    - Alpaca API for daily bars
    - OpenBB for supplementary data
    - Local cache for historical data
    
    Args:
        symbols: List of symbols to fetch (e.g., ['GLD', 'LTPZ'])
        lookback_days: How many days of history to fetch
        source: Data source ('local', 'alpaca', 'openbb')
    
    Returns:
        Dict[str, pd.DataFrame]: OHLCV data per symbol
    
    Notes:
        - Returns daily frequency data only
        - No intraday bars
        - Clean EOD closes for analysis
    """
    if source == "local":
        # Placeholder: return synthetic data
        return _generate_synthetic_eod_data(symbols, lookback_days)
    elif source == "alpaca":
        # Would integrate with Alpaca API
        raise NotImplementedError("Alpaca integration pending")
    elif source == "openbb":
        # Would integrate with OpenBB
        raise NotImplementedError("OpenBB integration pending")
    else:
        raise ValueError(f"Unknown data source: {source}")


def _generate_synthetic_eod_data(
    symbols: List[str],
    lookback_days: int
) -> Dict[str, pd.DataFrame]:
    """
    Generate synthetic EOD data for testing.
    
    Returns:
        Dict[str, pd.DataFrame]: Synthetic OHLCV data
    """
    import numpy as np
    
    data = {}
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    for i, symbol in enumerate(symbols):
        # Generate random walk
        base_price = 100 + i * 50
        returns = np.random.RandomState(hash(symbol) % 10000).randn(len(dates)) * 0.02
        closes = base_price * (1 + returns).cumprod()
        
        # Create OHLCV
        df = pd.DataFrame({
            'open': closes * (1 + np.random.RandomState(hash(symbol) % 10000).randn(len(dates)) * 0.005),
            'high': closes * 1.01,
            'low': closes * 0.99,
            'close': closes,
            'volume': np.random.RandomState(hash(symbol) % 10000).randint(1000000, 5000000, len(dates))
        }, index=dates)
        
        data[symbol] = df
    
    return data


def get_latest_close(eod_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    """
    Get latest close price for each symbol.
    
    Args:
        eod_data: EOD data dictionary
    
    Returns:
        Dict[str, float]: Latest close per symbol
    """
    latest = {}
    
    for symbol, df in eod_data.items():
        if len(df) > 0:
            latest[symbol] = df['close'].iloc[-1]
    
    return latest


