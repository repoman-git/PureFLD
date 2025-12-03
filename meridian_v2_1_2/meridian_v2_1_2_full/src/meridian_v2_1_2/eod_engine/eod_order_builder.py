"""
EOD Order Builder for Meridian v2.1.2

Build orders for next trading session based on EOD signals.
"""

import pandas as pd
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class EODOrder:
    """Represents an EOD order for next session"""
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    order_type: str  # 'market', 'limit', 'moo' (market on open)
    limit_price: float = None
    time_in_force: str = 'day'  # 'day' or 'gtc'


def build_eod_orders(
    target_positions: Dict[str, float],
    current_positions: Dict[str, float],
    latest_prices: Dict[str, float]
) -> List[EODOrder]:
    """
    Build orders to transition from current to target positions.
    
    Args:
        target_positions: Desired positions per symbol
        current_positions: Current positions per symbol
        latest_prices: Latest prices per symbol
    
    Returns:
        List[EODOrder]: Orders to execute
    
    Notes:
        - Computes delta = target - current
        - Generates MOO (market on open) orders
        - Clean, simple execution for EOD model
    """
    orders = []
    
    # Get all symbols
    all_symbols = set(list(target_positions.keys()) + list(current_positions.keys()))
    
    for symbol in all_symbols:
        target = target_positions.get(symbol, 0.0)
        current = current_positions.get(symbol, 0.0)
        
        delta = target - current
        
        # Skip if no change needed
        if abs(delta) < 0.01:  # Minimum order size
            continue
        
        # Determine side
        side = 'buy' if delta > 0 else 'sell'
        quantity = abs(delta)
        
        # Build order
        order = EODOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type='moo',  # Market on open - clean for EOD
            time_in_force='day'
        )
        
        orders.append(order)
    
    return orders


def validate_orders(
    orders: List[EODOrder],
    max_orders_per_day: int = 100
) -> bool:
    """
    Validate orders before submission.
    
    Args:
        orders: List of orders
        max_orders_per_day: Maximum allowed orders
    
    Returns:
        bool: True if valid
    
    Raises:
        ValueError: If validation fails
    """
    if len(orders) > max_orders_per_day:
        raise ValueError(f"Too many orders: {len(orders)} > {max_orders_per_day}")
    
    for order in orders:
        if order.quantity <= 0:
            raise ValueError(f"Invalid quantity for {order.symbol}: {order.quantity}")
        
        if order.side not in ['buy', 'sell']:
            raise ValueError(f"Invalid side for {order.symbol}: {order.side}")
    
    return True

