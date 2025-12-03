"""
FLD Projection Engine for Meridian v2.1.2

Project FLD (Future Line of Demarcation) forward into the future.
"""

import pandas as pd
import numpy as np
from typing import Optional

from ..fld_engine import compute_fld


def project_fld(
    prices: pd.Series,
    cycle_length: int,
    projection_bars: int,
    displacement: Optional[int] = None
) -> pd.Series:
    """
    Project FLD forward by projection_bars.
    
    Args:
        prices: Historical price series
        cycle_length: FLD cycle length
        projection_bars: Number of bars to project forward
        displacement: FLD displacement (defaults to cycle_length // 2)
    
    Returns:
        pd.Series: FLD with projection (includes NaN for future bars)
    
    Notes:
        - Computes FLD on historical data
        - Projects trend forward
        - Future values are NaN (to be filled with projection)
    """
    if displacement is None:
        displacement = cycle_length // 2
    
    # Compute historical FLD
    fld_historical = compute_fld(prices, cycle_length, displacement)
    
    # Simple projection: extend last trend
    # Get last valid FLD values
    valid_fld = fld_historical.dropna()
    
    if len(valid_fld) < 2:
        # Not enough data for projection
        return fld_historical
    
    # Calculate recent trend
    lookback = min(10, len(valid_fld))
    recent_fld = valid_fld.iloc[-lookback:]
    
    # Linear regression for trend
    x = np.arange(len(recent_fld))
    y = recent_fld.values
    
    if len(x) > 1:
        # Fit linear trend
        slope = np.polyfit(x, y, 1)[0]
    else:
        slope = 0
    
    # Project forward
    last_fld_value = valid_fld.iloc[-1]
    
    # Create future index (projection bars beyond current end)
    last_date = prices.index[-1]
    freq = pd.infer_freq(prices.index) or 'D'
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(1, unit=freq[0] if isinstance(freq, str) else 'D'),
        periods=projection_bars,
        freq=freq
    )
    
    # Project values
    projected_values = [last_fld_value + slope * (i + 1) for i in range(projection_bars)]
    fld_projection = pd.Series(projected_values, index=future_dates, name='fld_projection')
    
    # Combine historical and projected
    # Note: This creates a series with future dates beyond the price series
    combined = pd.concat([fld_historical, fld_projection])
    
    return combined

