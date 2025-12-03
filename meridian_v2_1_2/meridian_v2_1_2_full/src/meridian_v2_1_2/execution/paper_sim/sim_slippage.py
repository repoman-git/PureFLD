"""
Slippage Models for Meridian v2.1.2

Simple slippage calculations for paper trading.
"""


def simple_bps_slippage(price: float, bps: float, side: str) -> float:
    """
    Calculate simple basis point slippage.
    
    Args:
        price: Base price
        bps: Basis points of slippage
        side: "buy" or "sell"
    
    Returns:
        float: Slippage adjusted price
    """
    slip_amount = price * (bps / 10000.0)
    
    if side.lower() == "buy":
        # Buying costs more
        return price + slip_amount
    else:
        # Selling gets less
        return price - slip_amount

