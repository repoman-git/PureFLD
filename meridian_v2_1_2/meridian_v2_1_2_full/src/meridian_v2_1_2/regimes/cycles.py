"""
Cycle Regime Classification for Meridian v2.1.2

Classify cycle regime based on phase and amplitude.
"""

import pandas as pd
import numpy as np

from ..config import RegimeConfig


def classify_cycle_regime(
    cycle_phase: pd.Series,
    cycle_amplitude: pd.Series,
    config: RegimeConfig
) -> pd.Series:
    """
    Classify cycle regime based on phase and amplitude.
    
    Classification rules:
    - If amplitude < threshold → neutral (weak cycle)
    - If phase near trough (0.0-0.33) → rising
    - If phase near peak (0.33-0.66) → neutral
    - If phase near decline (0.66-1.0) → falling
    
    Args:
        cycle_phase: Normalized phase (0.0 to 1.0)
        cycle_amplitude: Cycle amplitude series
        config: Regime configuration
    
    Returns:
        pd.Series: Cycle regime codes
            +1 = cycle rising (bullish)
             0 = cycle neutral
            -1 = cycle falling (bearish)
    
    Notes:
        - Weak amplitude overrides phase classification
        - Based on Hurst cycle theory
        - Deterministic
    """
    if not cycle_phase.index.equals(cycle_amplitude.index):
        raise ValueError("Cycle phase and amplitude indices must match")
    
    regime = pd.Series(0, index=cycle_phase.index)  # Default neutral
    
    # Check amplitude first - weak cycles stay neutral
    weak_cycle = cycle_amplitude < config.amplitude_threshold
    
    # Phase-based classification for strong cycles
    strong_cycle = ~weak_cycle
    
    # Rising phase (trough zone: 0.0-0.33)
    rising_phase = (cycle_phase >= 0.0) & (cycle_phase <= 0.33)
    regime[strong_cycle & rising_phase] = 1
    
    # Falling phase (decline zone: 0.66-1.0)
    falling_phase = (cycle_phase >= 0.66) & (cycle_phase <= 1.0)
    regime[strong_cycle & falling_phase] = -1
    
    # Peak zone (0.33-0.66) stays neutral
    
    regime.name = 'cycle_regime'
    return regime


def get_cycle_regime_label(regime_code: int) -> str:
    """
    Get human-readable label for cycle regime.
    
    Args:
        regime_code: Cycle code (+1/0/-1)
    
    Returns:
        str: Regime label
    """
    labels = {
        1: "Cycle Rising",
        0: "Cycle Neutral",
        -1: "Cycle Falling"
    }
    return labels.get(regime_code, f"Unknown ({regime_code})")

