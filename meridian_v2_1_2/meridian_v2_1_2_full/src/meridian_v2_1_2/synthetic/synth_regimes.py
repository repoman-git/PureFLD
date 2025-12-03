"""
Synthetic Regime Generator for Meridian v2.1.2

Markov chain regime sequencer for stress testing.
"""

import numpy as np
import pandas as pd
from enum import Enum
from typing import List


class MarketRegime(str, Enum):
    """Market regime types"""
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    HIGH_VOL = "high_vol"
    LOW_VOL = "low_vol"
    RISING_YIELDS = "rising_yields"
    FALLING_YIELDS = "falling_yields"


def generate_regime_sequence(
    length: int,
    switch_prob: float = 0.1,
    seed: int = 42
) -> pd.Series:
    """
    Generate Markov chain regime sequence.
    
    Args:
        length: Number of days
        switch_prob: Probability of regime switch
        seed: Random seed
    
    Returns:
        pd.Series of regime labels
    """
    np.random.seed(seed)
    
    regimes_list = list(MarketRegime)
    current_regime_idx = np.random.choice(len(regimes_list))
    current_regime = regimes_list[current_regime_idx]
    
    sequence = []
    
    for _ in range(length):
        sequence.append(current_regime.value)
        
        # Regime switch?
        if np.random.rand() < switch_prob:
            # Pick new regime (different from current)
            other_indices = [i for i, r in enumerate(regimes_list) if r != current_regime]
            new_idx = np.random.choice(other_indices)
            current_regime = regimes_list[new_idx]
    
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return pd.Series(sequence, index=dates)

