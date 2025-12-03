"""
Synthetic COT Data Generator for Meridian v2.1.2

Generate realistic COT positioning data.
"""

import numpy as np
import pandas as pd


def generate_synthetic_cot(
    length: int = 2000,
    noise: float = 0.3,
    trendiness: float = 0.2,
    regime_sequence: pd.Series = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic COT (Commitment of Traders) data.
    
    Generates weekly data with:
    - Commercials (hedgers)
    - Non-commercials (speculators)
    - Net positions
    - Trending and mean-reverting behavior
    
    Args:
        length: Number of days
        noise: Noise level
        trendiness: Trend persistence
        regime_sequence: Optional regime sequence
        seed: Random seed
    
    Returns:
        DataFrame with weekly COT data
    """
    np.random.seed(seed)
    
    # Convert to weekly (COT reports on Tuesdays)
    n_weeks = length // 5
    
    # Commercials (tend to be contrarian, mean-reverting)
    comm_long = np.zeros(n_weeks)
    comm_short = np.zeros(n_weeks)
    
    comm_long[0] = 50000
    comm_short[0] = 45000
    
    for i in range(1, n_weeks):
        # Mean reversion
        comm_long[i] = comm_long[i-1] + 0.05 * (50000 - comm_long[i-1]) + np.random.randn() * 1000
        comm_short[i] = comm_short[i-1] + 0.05 * (45000 - comm_short[i-1]) + np.random.randn() * 1000
    
    # Non-commercials (tend to be trend-followers)
    non_comm_long = np.zeros(n_weeks)
    non_comm_short = np.zeros(n_weeks)
    
    non_comm_long[0] = 30000
    non_comm_short[0] = 28000
    
    # Add trend
    trend = trendiness * np.cumsum(np.random.randn(n_weeks))
    
    for i in range(1, n_weeks):
        non_comm_long[i] = 30000 + trend[i] + np.random.randn() * 500
        non_comm_short[i] = 28000 - trend[i] * 0.5 + np.random.randn() * 500
    
    # Add noise
    comm_long += np.random.randn(n_weeks) * noise * 1000
    comm_short += np.random.randn(n_weeks) * noise * 1000
    non_comm_long += np.random.randn(n_weeks) * noise * 500
    non_comm_short += np.random.randn(n_weeks) * noise * 500
    
    # Ensure positive
    comm_long = np.maximum(comm_long, 10000)
    comm_short = np.maximum(comm_short, 10000)
    non_comm_long = np.maximum(non_comm_long, 5000)
    non_comm_short = np.maximum(non_comm_short, 5000)
    
    # Calculate nets
    comm_net = comm_long - comm_short
    non_comm_net = non_comm_long - non_comm_short
    
    # Open interest
    open_interest = comm_long + comm_short + non_comm_long + non_comm_short
    
    # Create DataFrame (weekly, Tuesdays)
    start_date = pd.Timestamp('2020-01-01')
    # Find first Tuesday
    while start_date.dayofweek != 1:  # 1 = Tuesday
        start_date += pd.Timedelta(days=1)
    
    dates = pd.date_range(start_date, periods=n_weeks, freq='W-TUE')
    
    df = pd.DataFrame({
        'commercials_long': comm_long,
        'commercials_short': comm_short,
        'commercials_net': comm_net,
        'non_commercials_long': non_comm_long,
        'non_commercials_short': non_comm_short,
        'non_commercials_net': non_comm_net,
        'open_interest': open_interest
    }, index=dates)
    
    return df

