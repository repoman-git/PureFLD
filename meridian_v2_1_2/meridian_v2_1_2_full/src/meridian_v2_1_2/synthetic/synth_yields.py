"""
Synthetic Real Yields Generator for Meridian v2.1.2

Critical for LTPZ inverse-gold logic testing.
"""

import numpy as np
import pandas as pd


def generate_synthetic_yields(
    length: int = 2000,
    amplitude: float = 0.5,
    shock_probability: float = 0.02,
    gold_correlation: float = -0.65,
    regime_sequence: pd.Series = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate synthetic real yields.
    
    Real Yield = Nominal Yield - Expected Inflation
    
    Critical for:
    - LTPZ inverse-gold dynamics
    - Regime classification
    - Gold/LTPZ pair behavior
    
    Args:
        length: Number of days
        amplitude: Yield amplitude
        shock_probability: Probability of yield shock
        gold_correlation: Correlation with gold (negative)
        regime_sequence: Optional regime sequence
        seed: Random seed
    
    Returns:
        DataFrame with real yields data
    """
    np.random.seed(seed)
    
    # 10Y nominal yield (mean-reverting)
    nominal_10y = np.zeros(length)
    nominal_10y[0] = 3.5
    
    for i in range(1, length):
        # Mean reversion to 3.5%
        nominal_10y[i] = nominal_10y[i-1] + 0.01 * (3.5 - nominal_10y[i-1]) + np.random.randn() * 0.02
        nominal_10y[i] = np.clip(nominal_10y[i], 0.5, 5.0)
        
        # Yield shocks
        if np.random.rand() < shock_probability:
            nominal_10y[i:i+20] += np.random.choice([0.5, -0.3])
    
    # Expected inflation (cyclical + trend)
    t = np.arange(length)
    expected_inflation = 2.5 + 0.5 * np.sin(2 * np.pi * t / 365) + np.cumsum(np.random.randn(length) * 0.01)
    expected_inflation = np.clip(expected_inflation, 1.0, 4.0)
    
    # Real yield = nominal - inflation
    real_yield_10y = nominal_10y - expected_inflation
    
    # 5Y real yield (typically lower)
    real_yield_5y = real_yield_10y - 0.3 + np.random.randn(length) * 0.1
    
    # TIPS spread
    tips_spread = real_yield_10y + np.random.randn(length) * 0.05
    
    # Regime classification
    real_yield_regime = np.where(real_yield_10y > 1.0, 'rising', 'falling')
    
    # If regime sequence provided, influence yields
    if regime_sequence is not None:
        for i in range(length):
            regime = regime_sequence.iloc[i]
            
            if 'rising_yields' in regime:
                real_yield_10y[i] += amplitude * 0.1
            elif 'falling_yields' in regime:
                real_yield_10y[i] -= amplitude * 0.1
    
    # Create DataFrame
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    
    df = pd.DataFrame({
        'nominal_10y': nominal_10y,
        'expected_inflation': expected_inflation,
        'real_yield_10y': real_yield_10y,
        'real_yield_5y': real_yield_5y,
        'tips_spread': tips_spread,
        'real_yield_regime': real_yield_regime
    }, index=dates)
    
    return df


