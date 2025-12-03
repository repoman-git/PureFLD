"""
Seasonality Module for Meridian v2.1.2

Provides TDOM (Time Day of Month) and TDOY (Trading Day of Year) seasonal overlays.
"""

import pandas as pd
from typing import List, Optional


def compute_tdom_flags(
    index: pd.DatetimeIndex,
    favourable_days: List[int],
    unfavourable_days: List[int]
) -> pd.Series:
    """
    Compute TDOM (Time Day of Month) flags.
    
    Args:
        index: DatetimeIndex
        favourable_days: List of favourable days (1-31)
        unfavourable_days: List of unfavourable days (1-31)
    
    Returns:
        pd.Series with values:
            +1: Favourable day
             0: Neutral day
            -1: Unfavourable day
    """
    flags = []
    for d in index:
        day = d.day
        if day in favourable_days:
            flags.append(1)
        elif day in unfavourable_days:
            flags.append(-1)
        else:
            flags.append(0)
    
    return pd.Series(flags, index=index, name='tdom')


def compute_tdoy_flags(
    index: pd.DatetimeIndex,
    favourable: List[int],
    unfavourable: List[int]
) -> pd.Series:
    """
    Compute TDOY (Trading Day of Year) flags.
    
    Uses day of year (1-366) to determine seasonal regime.
    
    Args:
        index: DatetimeIndex
        favourable: List of favourable days (1-366)
        unfavourable: List of unfavourable days (1-366)
    
    Returns:
        pd.Series with values:
            +1: Favourable day
             0: Neutral day
            -1: Unfavourable day
    
    Examples:
        >>> dates = pd.date_range('2020-01-01', '2020-01-10')
        >>> tdoy = compute_tdoy_flags(dates, favourable=[1,2,3], unfavourable=[])
        >>> # Jan 1-3 will be +1, rest will be 0
    """
    flags = []
    for d in index:
        day_of_year = d.dayofyear
        if day_of_year in favourable:
            flags.append(1)
        elif day_of_year in unfavourable:
            flags.append(-1)
        else:
            flags.append(0)
    
    return pd.Series(flags, index=index, name='tdoy')


def combine_seasonal_flags(
    tdom: Optional[pd.Series] = None,
    tdoy: Optional[pd.Series] = None
) -> pd.Series:
    """
    Combine TDOM and TDOY into a single seasonal score.
    
    Each dimension contributes +1/0/-1, so combined score ranges from -2 to +2:
        +2: Strong favourable (both positive)
        +1: Mild favourable (one positive, one neutral)
         0: Neutral (both neutral, or one positive one negative)
        -1: Mild unfavourable (one negative, one neutral)
        -2: Strong unfavourable (both negative)
    
    Args:
        tdom: TDOM series (+1/0/-1), or None
        tdoy: TDOY series (+1/0/-1), or None
    
    Returns:
        pd.Series: Combined seasonal score (-2 to +2)
    
    Examples:
        >>> tdom = pd.Series([1, 0, -1], index=dates)
        >>> tdoy = pd.Series([1, 1, -1], index=dates)
        >>> score = combine_seasonal_flags(tdom, tdoy)
        >>> # Result: [2, 1, -2]
    
    Notes:
        - If both None, returns series of zeros
        - If one is None, returns the other
        - Index must match if both provided
    """
    # Handle None cases
    if tdom is None and tdoy is None:
        raise ValueError("At least one of tdom or tdoy must be provided")
    
    if tdom is None:
        return tdoy.copy()
    
    if tdoy is None:
        return tdom.copy()
    
    # Both provided - validate indices match
    if not tdom.index.equals(tdoy.index):
        raise ValueError("TDOM and TDOY indices must match")
    
    # Combine: simple addition
    combined = tdom + tdoy
    combined.name = 'seasonal_score'
    
    return combined


def get_seasonal_regime_label(score: int) -> str:
    """
    Get human-readable label for seasonal score.
    
    Args:
        score: Seasonal score (-2 to +2)
    
    Returns:
        str: Regime label
    """
    labels = {
        2: "Strong Favourable",
        1: "Mild Favourable",
        0: "Neutral",
        -1: "Mild Unfavourable",
        -2: "Strong Unfavourable"
    }
    return labels.get(score, f"Unknown ({score})")
