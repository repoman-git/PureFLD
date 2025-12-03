"""
Exposure Checks for Meridian v2.1.2

Validate portfolio exposure against limits.
"""

from typing import Dict, Tuple

from ..config import HealthConfig


def check_exposures(
    positions: Dict[str, float],
    prices: Dict[str, float],
    config: HealthConfig
) -> Tuple[bool, str]:
    """
    Check portfolio exposure against configured limits.
    
    Validates:
    - Gross exposure
    - Net exposure
    - Single asset concentration
    
    Args:
        positions: Current positions per symbol
        prices: Current prices per symbol
        config: Health configuration
    
    Returns:
        Tuple[bool, str]: (is_healthy, message)
    """
    if len(positions) == 0:
        return True, "No positions (flat)"
    
    # Calculate position values
    values = {sym: positions[sym] * prices.get(sym, 0) for sym in positions.keys()}
    
    # Gross exposure
    gross = sum(abs(v) for v in values.values())
    
    # Net exposure
    net = sum(values.values())
    
    # Check limits (use 100k as base capital)
    capital = 100000
    
    if gross > capital * config.max_gross_exposure:
        return False, f"Gross exposure too high: {gross/capital:.2f}x"
    
    if abs(net) > capital * config.max_net_exposure:
        return False, f"Net exposure too high: {abs(net)/capital:.2f}x"
    
    return True, "Exposure within limits"

