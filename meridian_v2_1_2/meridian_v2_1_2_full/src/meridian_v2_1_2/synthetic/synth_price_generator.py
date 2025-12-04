"""
Synthetic Price Generator for Meridian v2.1.2

OHLC price generation combining trend, cycle, and volatility.
"""

import numpy as np
import pandas as pd
from .synth_volatility import generate_volatility_regime
from .synth_trends import generate_trend_component
from .synth_cycles import generate_cycle_component


def generate_synthetic_prices(
    symbol: str,
    length: int = 2000,
    start_price: float = 100.0,
    vol_low: float = 0.005,
    vol_high: float = 0.02,
    trend_strength: float = 0.4,
    cycle_amp: float = 0.03,
    cycle_period: int = 120,
    regime_sequence: pd.Series = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic OHLC prices.
    
    Combines:
    - Trend component
    - Cycle component
    - Volatility regime
    - Random noise
    
    Args:
        symbol: Symbol name
        length: Number of days
        start_price: Starting price
        vol_low: Low volatility
        vol_high: High volatility
        trend_strength: Trend drift
        cycle_amp: Cycle amplitude
        cycle_period: Cycle period
        regime_sequence: Optional regime sequence
        seed: Random seed
    
    Returns:
        DataFrame with OHLC data
    """
    np.random.seed(hash(symbol) % (2**32) + seed)
    
    # Generate components
    trend = generate_trend_component(
        length, trend_strength, mode="alternating", 
        regime_sequence=regime_sequence, seed=seed
    )
    
    cycle = generate_cycle_component(
        length, cycle_amp, cycle_period, deform=True, seed=seed
    )
    
    vol = generate_volatility_regime(
        length, vol_low, vol_high, 
        regime_sequence=regime_sequence, seed=seed
    )
    
    # Combine into returns
    returns = trend / length + cycle / length + vol * np.random.randn(length)
    
    # Generate close prices
    close = start_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC from close
    high = close * (1 + np.abs(np.random.randn(length)) * vol * 0.5)
    low = close * (1 - np.abs(np.random.randn(length)) * vol * 0.5)
    open_price = np.roll(close, 1)
    open_price[0] = start_price
    
    # Add small gap between close and next open
    open_price = open_price * (1 + np.random.randn(length) * vol * 0.3)
    
    # Generate volume
    volume = np.random.randint(1000000, 10000000, length)
    
    # Create DataFrame
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    return df


