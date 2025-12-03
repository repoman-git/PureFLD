"""
Synthetic Macro Data Generator for Meridian v2.1.2

Generate synthetic macro indicators for stress testing.
"""

import numpy as np
import pandas as pd


def generate_synthetic_macro(
    length: int = 2000,
    shock_probability: float = 0.02,
    regime_sequence: pd.Series = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic macro indicators.
    
    Includes:
    - CPI (inflation)
    - GDP growth
    - Unemployment
    - Fed Funds Rate
    - 10Y Treasury Yield
    
    Args:
        length: Number of days
        shock_probability: Probability of macro shock
        regime_sequence: Optional regime sequence
        seed: Random seed
    
    Returns:
        DataFrame with macro indicators (monthly frequency)
    """
    np.random.seed(seed)
    
    # Convert to monthly
    n_months = length // 21  # Approximate trading days per month
    
    # CPI (trending upward with shocks)
    cpi = 250 + np.cumsum(np.random.randn(n_months) * 0.5 + 0.3)
    
    # Add inflation shocks
    for i in range(n_months):
        if np.random.rand() < shock_probability:
            cpi[i:] += np.random.choice([5, -3])  # Shock
    
    # GDP growth
    gdp_growth = 2.0 + np.random.randn(n_months) * 0.5
    
    # Unemployment (mean-reverting)
    unemployment = np.zeros(n_months)
    unemployment[0] = 4.0
    
    for i in range(1, n_months):
        unemployment[i] = unemployment[i-1] + 0.1 * (4.5 - unemployment[i-1]) + np.random.randn() * 0.2
        unemployment[i] = np.clip(unemployment[i], 3.0, 10.0)
    
    # Fed Funds Rate (responds to inflation)
    fed_funds = np.zeros(n_months)
    if n_months > 0:
        fed_funds[0] = 2.5
    
    # Only compute gradient if we have enough data
    if n_months >= 2:
        inflation_rate = np.gradient(cpi) / cpi * 100 * 12
    else:
        inflation_rate = np.zeros(n_months)
    
    for i in range(1, n_months):
        # Taylor rule-ish
        target_rate = 2.0 + 0.5 * (inflation_rate[i] - 2.0)
        fed_funds[i] = fed_funds[i-1] + 0.1 * (target_rate - fed_funds[i-1]) + np.random.randn() * 0.1
        fed_funds[i] = np.clip(fed_funds[i], 0.0, 5.0)
    
    # 10Y Treasury
    treasury_10y = fed_funds + 1.0 + np.random.randn(n_months) * 0.3
    treasury_10y = np.clip(treasury_10y, 1.0, 6.0)
    
    # Create DataFrame
    dates = pd.date_range('2020-01-01', periods=n_months, freq='ME')
    
    df = pd.DataFrame({
        'cpi': cpi,
        'gdp_growth': gdp_growth,
        'unemployment': unemployment,
        'fed_funds_rate': fed_funds,
        'treasury_10y': treasury_10y,
        'inflation_yoy': inflation_rate
    }, index=dates)
    
    return df

