"""
FLD (Future Line of Demarcation) Engine for Meridian v2.1.2

Computes displaced moving averages used for FLD-based trading strategies.
"""

import pandas as pd
import numpy as np
from typing import Optional


def compute_fld(
    prices: pd.Series,
    cycle_length: int = 40,
    displacement: int = 20
) -> pd.Series:
    """
    Compute FLD (Future Line of Demarcation) as a displaced moving average.
    
    The FLD is calculated as:
    1. Simple moving average over cycle_length bars
    2. Shifted forward by displacement bars
    
    Args:
        prices: Price series with DatetimeIndex
        cycle_length: Period for moving average calculation (default: 40)
        displacement: Number of bars to shift forward (default: 20)
    
    Returns:
        pd.Series: FLD line, same index as prices
        
    Notes:
        - First (cycle_length - 1) bars will be NaN due to SMA calculation
        - First displacement bars will also be NaN due to forward shift
        - Total NaN bars at start: max(cycle_length - 1, displacement)
        - This is a deterministic calculation with no randomness
    
    Examples:
        >>> prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range('2020-01-01', periods=5))
        >>> fld = compute_fld(prices, cycle_length=3, displacement=1)
        >>> # Result: [NaN, 101.0, 102.0, 103.0, NaN] (shifted forward)
    """
    if cycle_length < 1:
        raise ValueError(f"cycle_length must be >= 1, got {cycle_length}")
    if displacement < 0:
        raise ValueError(f"displacement must be >= 0, got {displacement}")
    
    # Calculate simple moving average
    sma = prices.rolling(window=cycle_length, min_periods=cycle_length).mean()
    
    # Shift forward by displacement (positive shift = future displacement)
    fld = sma.shift(displacement)
    
    return fld


def compute_fld_with_validation(
    prices: pd.Series,
    cycle_length: int = 40,
    displacement: int = 20,
    min_valid_bars: Optional[int] = None
) -> pd.Series:
    """
    Compute FLD with additional validation checks.
    
    Args:
        prices: Price series
        cycle_length: SMA period
        displacement: Forward shift
        min_valid_bars: Minimum number of valid (non-NaN) FLD bars required.
                       If not met, raises ValueError.
    
    Returns:
        pd.Series: FLD line
        
    Raises:
        ValueError: If validation fails
    """
    if len(prices) < cycle_length:
        raise ValueError(
            f"Price series too short: need at least {cycle_length} bars, "
            f"got {len(prices)}"
        )
    
    fld = compute_fld(prices, cycle_length, displacement)
    
    # Check minimum valid bars if specified
    if min_valid_bars is not None:
        valid_count = fld.notna().sum()
        if valid_count < min_valid_bars:
            raise ValueError(
                f"Insufficient valid FLD bars: need {min_valid_bars}, "
                f"got {valid_count}"
            )
    
    return fld


def get_fld_valid_mask(fld: pd.Series) -> pd.Series:
    """
    Get boolean mask indicating which FLD bars are valid (not NaN).
    
    Args:
        fld: FLD series
    
    Returns:
        pd.Series: Boolean mask, True where FLD is valid
    """
    return fld.notna()


def get_first_valid_fld_index(fld: pd.Series) -> Optional[int]:
    """
    Get the integer position of the first valid (non-NaN) FLD value.
    
    Args:
        fld: FLD series
    
    Returns:
        int or None: Position of first valid value, or None if all NaN
    """
    valid_mask = fld.notna()
    if not valid_mask.any():
        return None
    return valid_mask.idxmax()
