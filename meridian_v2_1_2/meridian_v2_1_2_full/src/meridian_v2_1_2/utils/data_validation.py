"""
Data Validation Utilities

Decorators and validators for enforcing Meridian's data quality policy.

Author: Meridian Team
Date: December 4, 2025
"""

import pandas as pd
import functools
import datetime as dt
from typing import Optional, Union


def minimum_history_required(start_year: int = 2000, min_bars: Optional[int] = None):
    """
    Decorator enforcing minimum historical depth for cycle analysis.
    
    Validates that data passed to a function meets Meridian's strict
    historical requirements for reliable cycle analysis.
    
    Args:
        start_year: Minimum year data must start from (default: 2000)
        min_bars: Minimum number of bars required
        
    Example:
        >>> @minimum_history_required(start_year=2000, min_bars=1500)
        >>> def analyze_cycles(price_df):
        ...     # This function now guaranteed to have data from ≥2000
        ...     return results
        
    Raises:
        ValueError: If data doesn't meet minimum requirements
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Locate DataFrame or Series argument
            data = None
            data_name = "data"
            
            # Check args
            for i, arg in enumerate(args):
                if isinstance(arg, (pd.DataFrame, pd.Series)):
                    data = arg
                    data_name = f"argument {i}"
                    break
            
            # Check kwargs
            if data is None:
                for key, value in kwargs.items():
                    if isinstance(value, (pd.DataFrame, pd.Series)):
                        data = value
                        data_name = key
                        break
            
            if data is None:
                raise ValueError(
                    f"[DATA VALIDATION] Function '{func.__name__}' must receive "
                    f"a pandas DataFrame or Series."
                )
            
            # Validate data
            _validate_data_requirements(
                data=data,
                func_name=func.__name__,
                data_name=data_name,
                start_year=start_year,
                min_bars=min_bars
            )
            
            # Execute function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def _validate_data_requirements(
    data: Union[pd.DataFrame, pd.Series],
    func_name: str,
    data_name: str,
    start_year: int,
    min_bars: Optional[int]
):
    """Internal validation logic"""
    
    # Check if index is datetime
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError(
            f"[DATA VALIDATION] {func_name}: {data_name} must have DatetimeIndex"
        )
    
    # Check start date
    earliest = data.index.min()
    required = dt.datetime(start_year, 1, 1)
    
    if earliest > required:
        raise ValueError(
            f"[DATA INTEGRITY VIOLATION]\n"
            f"Function: {func_name}\n"
            f"Dataset starts: {earliest.date()}\n"
            f"Required start: {required.date()}\n"
            f"Missing: {(earliest - required).days} days\n"
            f"Action: Load more historical data"
        )
    
    # Check minimum bars
    if min_bars and len(data) < min_bars:
        raise ValueError(
            f"[DATA INTEGRITY VIOLATION]\n"
            f"Function: {func_name}\n"
            f"Dataset has: {len(data)} bars\n"
            f"Required: {min_bars} bars\n"
            f"Missing: {min_bars - len(data)} bars\n"
            f"Action: Load more historical data"
        )


def validate_data_quality(data: pd.Series, symbol: str = "UNKNOWN") -> tuple:
    """
    Validate data quality and return (is_valid, issues).
    
    Args:
        data: Price series to validate
        symbol: Symbol name for logging
        
    Returns:
        (is_valid: bool, issues: list)
    """
    issues = []
    
    # Check for NaN
    if data.isna().any():
        nan_count = data.isna().sum()
        issues.append(f"Contains {nan_count} NaN values")
    
    # Check for extreme outliers (>10 sigma)
    returns = data.pct_change().dropna()
    if len(returns) > 0:
        mean_ret = returns.mean()
        std_ret = returns.std()
        outliers = returns[abs(returns - mean_ret) > 10 * std_ret]
        if len(outliers) > 0:
            issues.append(f"Contains {len(outliers)} extreme outliers (>10σ)")
    
    # Check for duplicates
    if data.index.duplicated().any():
        dup_count = data.index.duplicated().sum()
        issues.append(f"Contains {dup_count} duplicate timestamps")
    
    # Check monotonic ordering
    if not data.index.is_monotonic_increasing:
        issues.append("Timestamps are not in ascending order")
    
    # Check for gaps
    if len(data) > 1:
        expected_freq = pd.infer_freq(data.index[:10])
        if expected_freq:
            full_range = pd.date_range(start=data.index[0], end=data.index[-1], freq=expected_freq)
            missing = len(full_range) - len(data)
            if missing > len(data) * 0.05:  # >5% missing
                issues.append(f"Missing ~{missing} expected data points")
    
    is_valid = len(issues) == 0
    return is_valid, issues

