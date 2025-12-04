"""
Reconciliation for Meridian v2.1.2

Ensure position consistency in paper trading.
"""

from typing import Dict, Tuple, List


def reconcile_positions(
    broker_positions: Dict,
    expected_positions: Dict[str, float],
    tolerance: float = 0.01
) -> Tuple[bool, List[str]]:
    """
    Reconcile positions between broker and expected.
    
    Args:
        broker_positions: Broker portfolio dictionary
        expected_positions: Expected positions {symbol: qty}
        tolerance: Tolerance for drift (1% default)
    
    Returns:
        (is_reconciled, issues)
    """
    issues = []
    
    broker_pos = broker_positions.get('positions', {})
    
    # Check all expected positions
    for symbol, expected_qty in expected_positions.items():
        if symbol in broker_pos:
            actual_qty = broker_pos[symbol]['qty']
        else:
            actual_qty = 0.0
        
        # Check drift
        if expected_qty != 0:
            drift_pct = abs(actual_qty - expected_qty) / abs(expected_qty)
            if drift_pct > tolerance:
                issues.append(
                    f"{symbol}: Expected {expected_qty}, got {actual_qty} "
                    f"(drift: {drift_pct:.2%})"
                )
        elif actual_qty != 0:
            issues.append(f"{symbol}: Expected 0, got {actual_qty}")
    
    # Check for unexpected positions
    for symbol in broker_pos:
        if symbol not in expected_positions:
            actual_qty = broker_pos[symbol]['qty']
            if actual_qty != 0:
                issues.append(f"{symbol}: Unexpected position of {actual_qty}")
    
    return (len(issues) == 0, issues)


def check_position_drift(
    current_positions: Dict[str, float],
    target_positions: Dict[str, float],
    max_drift_pct: float = 0.05
) -> Tuple[bool, Dict[str, float]]:
    """
    Check for position drift.
    
    Args:
        current_positions: Current positions
        target_positions: Target positions
        max_drift_pct: Maximum allowed drift
    
    Returns:
        (has_drift, drift_by_symbol)
    """
    drift_by_symbol = {}
    has_drift = False
    
    all_symbols = set(current_positions.keys()) | set(target_positions.keys())
    
    for symbol in all_symbols:
        current = current_positions.get(symbol, 0.0)
        target = target_positions.get(symbol, 0.0)
        
        if target != 0:
            drift_pct = abs(current - target) / abs(target)
            drift_by_symbol[symbol] = drift_pct
            
            if drift_pct > max_drift_pct:
                has_drift = True
        elif current != 0:
            drift_by_symbol[symbol] = 1.0  # 100% drift
            has_drift = True
    
    return (has_drift, drift_by_symbol)


