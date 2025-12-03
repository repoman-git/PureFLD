"""
Nominal Cycle Model for Meridian v2.1.2

Snap detected cycles to nominal Hurst-style cycle hierarchy.
"""

import pandas as pd
from typing import List

from ..config import CycleConfig


def build_nominal_cycle_map(
    dominant_cycle: int,
    config: CycleConfig
) -> List[int]:
    """
    Build nominal cycle map based on dominant cycle.
    
    If use_nominal_model=True:
        Snaps dominant cycle to nearest element in nominal_cycles list
        Returns harmonically related cycles from the nominal list
    
    If use_nominal_model=False:
        Returns only the detected dominant cycle
    
    Args:
        dominant_cycle: Detected dominant cycle length
        config: Cycle configuration
    
    Returns:
        List[int]: Active cycle lengths for analysis
    
    Examples:
        >>> config = CycleConfig(use_nominal_model=True, nominal_cycles=[20, 40, 80, 160])
        >>> build_nominal_cycle_map(45, config)
        [40, 80]  # Snapped to 40, includes next harmonic
    """
    if not config.use_nominal_model or len(config.nominal_cycles) == 0:
        # No nominal model - return detected cycle only
        return [dominant_cycle]
    
    # Find nearest nominal cycle
    nominal_cycles = sorted(config.nominal_cycles)
    
    # Snap to nearest
    nearest = min(nominal_cycles, key=lambda x: abs(x - dominant_cycle))
    
    # Find position in nominal hierarchy
    try:
        idx = nominal_cycles.index(nearest)
    except ValueError:
        return [nearest]
    
    # Include this cycle and potentially next harmonic (2x)
    active_cycles = [nearest]
    
    # Add next cycle up if available
    if idx + 1 < len(nominal_cycles):
        active_cycles.append(nominal_cycles[idx + 1])
    
    # Add previous cycle down if available and not too small
    if idx > 0 and nominal_cycles[idx - 1] >= config.min_cycle:
        active_cycles.insert(0, nominal_cycles[idx - 1])
    
    return sorted(list(set(active_cycles)))

