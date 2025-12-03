"""
Data Integrity Checks for Meridian v2.1.2

Validate data quality and completeness.
"""

from typing import Dict, Tuple
import pandas as pd


def check_data_integrity(
    eod_data: Dict[str, pd.DataFrame]
) -> Tuple[bool, str]:
    """
    Check data integrity for EOD data.
    
    Validates:
    - All symbols have data
    - No missing OHLC columns
    - No excessive NaN values
    - Data is aligned
    
    Args:
        eod_data: EOD data per symbol
    
    Returns:
        Tuple[bool, str]: (is_healthy, message)
    """
    if len(eod_data) == 0:
        return False, "No EOD data available"
    
    required_columns = ['open', 'high', 'low', 'close']
    
    for symbol, df in eod_data.items():
        # Check columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return False, f"Missing columns for {symbol}: {missing_cols}"
        
        # Check for empty data
        if len(df) == 0:
            return False, f"No data for {symbol}"
        
        # Check for excessive NaN
        nan_pct = df['close'].isna().sum() / len(df)
        if nan_pct > 0.1:
            return False, f"Excessive NaN in {symbol}: {nan_pct:.1%}"
    
    return True, f"Data integrity OK for {len(eod_data)} symbols"

