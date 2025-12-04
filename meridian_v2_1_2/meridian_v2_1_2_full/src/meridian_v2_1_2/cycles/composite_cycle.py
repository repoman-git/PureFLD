"""
Composite Cycle Model for Meridian v2.1.2

Build composite waveform from multiple cycle components.
"""

import pandas as pd
import numpy as np
from typing import List


def build_composite_cycle(
    prices: pd.Series,
    cycles: List[int],
    projection_bars: int = 40
) -> pd.DataFrame:
    """
    Build composite cycle from multiple cycle lengths.
    
    For each cycle length:
    1. Compute smoothed cycle waveform (rolling mean)
    2. Add them together to produce composite
    3. Create projected version into future
    
    Args:
        prices: Price series
        cycles: List of cycle lengths to include
        projection_bars: Number of bars to project forward
    
    Returns:
        pd.DataFrame with columns:
            - cycle_N: Individual cycle components (one per cycle length)
            - composite_cycle: Sum of all cycles
            - composite_projection: Projected composite (future bars)
    
    Notes:
        - Each cycle is extracted using rolling mean
        - Composite = sum of all cycle components
        - Projection uses linear extrapolation of recent trend
    """
    if len(prices) == 0:
        return pd.DataFrame()
    
    result_df = pd.DataFrame(index=prices.index)
    
    # Extract each cycle component
    cycle_components = []
    
    for cycle_length in cycles:
        if cycle_length > len(prices):
            continue
        
        # Smooth at cycle length to extract that cycle
        cycle_component = prices.rolling(window=cycle_length, min_periods=cycle_length//2).mean()
        
        # Detrend by removing long-term mean
        # This isolates the cycle oscillation
        longterm_window = max(cycle_length * 2, 50)
        if longterm_window <= len(prices):
            longterm_trend = prices.rolling(window=longterm_window, min_periods=longterm_window//2).mean()
            cycle_oscillation = cycle_component - longterm_trend
        else:
            cycle_oscillation = cycle_component - cycle_component.mean()
        
        # Store cycle component
        result_df[f'cycle_{cycle_length}'] = cycle_oscillation
        cycle_components.append(cycle_oscillation)
    
    # Build composite (sum of all cycles)
    if len(cycle_components) > 0:
        composite = sum(cycle_components)
        result_df['composite_cycle'] = composite
    else:
        result_df['composite_cycle'] = 0.0
    
    # Project composite forward
    if 'composite_cycle' in result_df.columns:
        projection = _project_composite_forward(
            result_df['composite_cycle'],
            projection_bars,
            prices.index
        )
        
        # Add projection to result
        # Note: projection index extends beyond prices index
        result_df['composite_projection'] = np.nan
        
        # Mark where projection starts
        result_df['projection_start'] = False
        if len(result_df) > 0:
            result_df.loc[result_df.index[-1], 'projection_start'] = True
    
    return result_df


def _project_composite_forward(
    composite: pd.Series,
    projection_bars: int,
    price_index: pd.DatetimeIndex
) -> pd.Series:
    """
    Project composite cycle forward.
    
    Uses linear extrapolation of recent trend.
    
    Args:
        composite: Historical composite cycle
        projection_bars: Number of bars to project
        price_index: Original price index for date generation
    
    Returns:
        pd.Series: Projected composite values
    """
    # Get last valid values
    valid_composite = composite.dropna()
    
    if len(valid_composite) < 2:
        # Not enough data for projection
        # Return flat projection at last value
        last_val = composite.iloc[-1] if len(composite) > 0 else 0
        freq = pd.infer_freq(price_index) or 'D'
        future_dates = pd.date_range(
            start=price_index[-1] + pd.Timedelta(1, unit=freq[0] if isinstance(freq, str) else 'D'),
            periods=projection_bars,
            freq=freq
        )
        return pd.Series([last_val] * projection_bars, index=future_dates)
    
    # Calculate recent trend
    lookback = min(20, len(valid_composite))
    recent = valid_composite.iloc[-lookback:]
    
    # Linear fit
    x = np.arange(len(recent))
    y = recent.values
    slope = np.polyfit(x, y, 1)[0]
    
    # Last value
    last_value = valid_composite.iloc[-1]
    
    # Generate future dates
    freq = pd.infer_freq(price_index) or 'D'
    future_dates = pd.date_range(
        start=price_index[-1] + pd.Timedelta(1, unit=freq[0] if isinstance(freq, str) else 'D'),
        periods=projection_bars,
        freq=freq
    )
    
    # Project forward
    projected_values = [last_value + slope * (i + 1) for i in range(projection_bars)]
    projection = pd.Series(projected_values, index=future_dates, name='composite_projection')
    
    return projection


