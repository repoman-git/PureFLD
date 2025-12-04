"""
Reconciliation Checks for Meridian v2.1.2

Compare local model vs broker positions.
"""

from typing import Dict, Tuple


def check_reconciliation(
    local_positions: Dict[str, float],
    broker_positions: Dict[str, float],
    max_drift_pct: float = 0.05
) -> Tuple[bool, str]:
    """
    Check reconciliation between local and broker positions.
    
    Args:
        local_positions: Local position model
        broker_positions: Actual broker positions
        max_drift_pct: Maximum allowed drift
    
    Returns:
        Tuple[bool, str]: (is_reconciled, message)
    """
    all_symbols = set(list(local_positions.keys()) + list(broker_positions.keys()))
    
    drifts = {}
    
    for symbol in all_symbols:
        local = local_positions.get(symbol, 0.0)
        broker = broker_positions.get(symbol, 0.0)
        
        # Calculate drift
        if local != 0:
            drift = abs(broker - local) / abs(local)
        elif broker != 0:
            drift = 1.0  # 100% drift if local expects 0 but broker has position
        else:
            drift = 0.0
        
        if drift > max_drift_pct:
            drifts[symbol] = drift
    
    if len(drifts) > 0:
        drift_str = ', '.join([f"{sym}: {d:.1%}" for sym, d in drifts.items()])
        return False, f"Position drift detected: {drift_str}"
    
    return True, "Positions reconciled"


