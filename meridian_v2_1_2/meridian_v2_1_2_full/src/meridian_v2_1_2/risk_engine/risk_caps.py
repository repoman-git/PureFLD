"""
Risk Caps and Limits for Meridian v2.1.2

Apply hard limits to position sizes for risk management.
"""

import pandas as pd

from .risk_config import RiskConfig


def apply_risk_caps(
    sizes: pd.Series,
    config: RiskConfig
) -> pd.Series:
    """
    Apply hard risk caps to position sizes.
    
    Enforces:
    1. Maximum position limit
    2. Minimum position threshold
    3. No negative sizes
    
    Args:
        sizes: Position sizes
        config: Risk configuration
    
    Returns:
        pd.Series: Capped position sizes
    """
    capped = sizes.copy()
    
    # Apply maximum cap
    capped = capped.clip(upper=config.max_position)
    
    # Apply minimum threshold (for non-zero positions)
    # If size is very small but non-zero, bring up to minimum
    small_but_nonzero = (capped > 0) & (capped < config.min_position)
    capped[small_but_nonzero] = config.min_position
    
    # Ensure non-negative
    capped = capped.clip(lower=0)
    
    capped.name = 'capped_size'
    return capped

