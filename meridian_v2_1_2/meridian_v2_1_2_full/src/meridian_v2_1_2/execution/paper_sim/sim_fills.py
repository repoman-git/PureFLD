"""
Fill Simulation for Meridian v2.1.2

Generate realistic fills for paper trading.
"""

import pandas as pd
from typing import Optional
from .sim_slippage import simple_bps_slippage


def apply_gap(prev_close: float, next_open: float) -> float:
    """
    Calculate gap between close and next open.
    
    Args:
        prev_close: Previous close price
        next_open: Next open price
    
    Returns:
        float: Gap amount
    """
    return next_open - prev_close


def apply_slippage(
    price: float,
    slippage_bps: float,
    side: str
) -> float:
    """
    Apply slippage to fill price.
    
    Args:
        price: Base price
        slippage_bps: Slippage in basis points
        side: Order side
    
    Returns:
        float: Slippage-adjusted price
    """
    return simple_bps_slippage(price, slippage_bps, side)


def generate_fill(
    order,
    current_price: float,
    next_open: Optional[float] = None,
    slippage_bps: float = 5.0,
    use_gap_model: bool = True
) -> float:
    """
    Generate fill price for order.
    
    EOD Mode:
    - Fill at next day's open
    - Apply overnight gap
    - Apply slippage
    
    Args:
        order: Simulated order
        current_price: Current EOD price
        next_open: Next day's open price
        slippage_bps: Slippage in basis points
        use_gap_model: Whether to use gap model
    
    Returns:
        float: Fill price
    """
    # Start with next open (or current if not available)
    if next_open is not None and use_gap_model:
        base_price = next_open
    else:
        base_price = current_price
    
    # Apply slippage
    fill_price = apply_slippage(base_price, slippage_bps, order.side.value)
    
    return fill_price

