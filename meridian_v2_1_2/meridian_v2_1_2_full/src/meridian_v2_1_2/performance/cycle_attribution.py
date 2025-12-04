"""
Cycle Attribution for Meridian v2.1.2

Attribute PnL to cycle phases and conditions.
"""

import pandas as pd
from typing import Dict


def attribute_to_cycles(
    daily_pnl: pd.Series,
    cycle_phase: pd.Series,
    cycle_amplitude: pd.Series
) -> Dict[str, float]:
    """
    Attribute PnL to cycle conditions.
    
    Breaks down by:
    - Cycle phase (trough, rising, peak, falling)
    - Amplitude (strong vs weak cycles)
    
    Args:
        daily_pnl: Daily PnL series
        cycle_phase: Cycle phase (0-1)
        cycle_amplitude: Cycle amplitude
    
    Returns:
        Dict[str, float]: PnL per cycle condition
    """
    attribution = {}
    
    # Phase-based attribution
    # Trough: 0.0-0.25
    trough_mask = (cycle_phase >= 0.0) & (cycle_phase < 0.25)
    attribution['cycle_trough'] = daily_pnl[trough_mask].sum()
    
    # Rising: 0.25-0.50
    rising_mask = (cycle_phase >= 0.25) & (cycle_phase < 0.50)
    attribution['cycle_rising'] = daily_pnl[rising_mask].sum()
    
    # Peak: 0.50-0.75
    peak_mask = (cycle_phase >= 0.50) & (cycle_phase < 0.75)
    attribution['cycle_peak'] = daily_pnl[peak_mask].sum()
    
    # Falling: 0.75-1.0
    falling_mask = (cycle_phase >= 0.75) & (cycle_phase <= 1.0)
    attribution['cycle_falling'] = daily_pnl[falling_mask].sum()
    
    # Amplitude-based
    median_amp = cycle_amplitude.median()
    strong_cycle = cycle_amplitude > median_amp
    weak_cycle = ~strong_cycle
    
    attribution['strong_cycle'] = daily_pnl[strong_cycle].sum()
    attribution['weak_cycle'] = daily_pnl[weak_cycle].sum()
    
    return attribution


