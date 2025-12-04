"""
Cycle-Based Position Sizing for Meridian v2.1.2

Adjust position sizes based on cycle amplitude and score.
"""

import pandas as pd

from .risk_config import RiskConfig


def apply_cycle_sizing(
    base_size: pd.Series,
    cycle_amplitude: pd.Series,
    cycle_score: pd.Series,
    config: RiskConfig
) -> pd.Series:
    """
    Apply cycle-based adjustments to position sizes.
    
    Adjustments:
    1. Amplitude effect: size *= (1 + amplitude × multiplier)
    2. Score effect: size *= (1 + score × multiplier)
    
    Args:
        base_size: Base position sizes
        cycle_amplitude: Cycle amplitude series (normalized)
        cycle_score: Cycle score series (-1 to +1)
        config: Risk configuration
    
    Returns:
        pd.Series: Cycle-adjusted position sizes
    """
    adjusted = base_size.copy()
    
    # Amplitude adjustment
    # Normalize amplitude to reasonable range (0-1)
    max_amp = cycle_amplitude.max() if cycle_amplitude.max() > 0 else 1.0
    normalized_amp = (cycle_amplitude / max_amp).clip(0, 1)
    
    amplitude_factor = 1.0 + normalized_amp * config.cycle_amplitude_multiplier
    adjusted *= amplitude_factor
    
    # Score adjustment
    # Score is already -1 to +1
    score_factor = 1.0 + cycle_score * config.cycle_score_multiplier
    adjusted *= score_factor
    
    # Ensure non-negative
    adjusted = adjusted.clip(lower=0.01)
    
    adjusted.name = 'cycle_adjusted_size'
    return adjusted


