"""
Operational Failure Modes for Meridian v2.1.2

System failure simulations.
"""

import numpy as np
from typing import List, Dict, Any


def duplicate_orders(
    orders: List[Dict[str, Any]],
    duplication_rate: float = 0.1
) -> List[Dict[str, Any]]:
    """
    Duplicate some orders (OMS bug simulation).
    
    Args:
        orders: List of orders
        duplication_rate: Fraction to duplicate
    
    Returns:
        Orders with duplicates
    """
    if not orders:
        return orders
    
    num_duplicates = max(1, int(len(orders) * duplication_rate))
    
    for _ in range(num_duplicates):
        if orders:
            order_to_dup = np.random.choice(orders)
            orders.append(order_to_dup.copy())
    
    return orders


def multiple_fills(
    fills: List[Dict[str, Any]],
    multi_fill_rate: float = 0.05
) -> List[Dict[str, Any]]:
    """
    Create multiple fills for same order.
    
    Args:
        fills: List of fills
        multi_fill_rate: Fraction with multiple fills
    
    Returns:
        Fills with multiples
    """
    if not fills:
        return fills
    
    num_multi = max(1, int(len(fills) * multi_fill_rate))
    
    for _ in range(num_multi):
        if fills:
            fill_to_dup = np.random.choice(fills)
            dup_fill = fill_to_dup.copy()
            # Modify qty slightly
            if 'qty' in dup_fill:
                dup_fill['qty'] *= 0.5
            fills.append(dup_fill)
    
    return fills


def extreme_slippage(
    fill_price: float,
    slippage_pct: float = 0.05
) -> float:
    """
    Apply extreme slippage.
    
    Args:
        fill_price: Expected fill price
        slippage_pct: Slippage percentage
    
    Returns:
        Price with extreme slippage
    """
    direction = np.random.choice([-1, 1])
    return fill_price * (1 + direction * slippage_pct)


def drift_explosion(
    expected_position: float,
    actual_position: float,
    drift_factor: float = 0.2
) -> float:
    """
    Simulate position drift explosion.
    
    Args:
        expected_position: Target position
        actual_position: Current position
        drift_factor: Drift magnitude
    
    Returns:
        Drifted position
    """
    drift = expected_position * drift_factor * np.random.randn()
    return actual_position + drift


def nav_failure(
    positions: Dict[str, float],
    prices: Dict[str, float],
    failure_type: str = "zero"
) -> float:
    """
    Simulate NAV calculation failure.
    
    Args:
        positions: Symbol -> qty
        prices: Symbol -> price
        failure_type: Type of failure
    
    Returns:
        Corrupted NAV
    """
    if failure_type == "zero":
        return 0.0
    elif failure_type == "negative":
        return -100000.0
    elif failure_type == "infinite":
        return np.inf
    elif failure_type == "nan":
        return np.nan
    else:
        # Incorrect calculation
        nav = sum(positions.get(s, 0) * prices.get(s, 0) for s in positions.keys())
        return nav * np.random.uniform(0.5, 1.5)


def attribution_breakdown(
    strategy_pnl: Dict[str, float],
    corruption_severity: float = 0.3
) -> Dict[str, float]:
    """
    Corrupt attribution (PnL doesn't sum correctly).
    
    Args:
        strategy_pnl: Strategy -> PnL
        corruption_severity: Corruption level
    
    Returns:
        Corrupted attribution
    """
    corrupted = strategy_pnl.copy()
    
    # Add random noise to attribution
    for strategy in corrupted:
        noise = corrupted[strategy] * corruption_severity * np.random.randn()
        corrupted[strategy] += noise
    
    return corrupted

