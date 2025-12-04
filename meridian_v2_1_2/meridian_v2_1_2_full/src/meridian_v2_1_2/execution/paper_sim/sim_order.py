"""
Simulated Order for Meridian v2.1.2

Order object for paper trading simulation.
"""

from enum import Enum
from typing import Optional
from datetime import datetime
from dataclasses import dataclass


class OrderStatus(str, Enum):
    """Order status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderSide(str, Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class SimulatedOrder:
    """
    Simulated order object.
    
    Mimics Alpaca order structure.
    """
    order_id: str
    symbol: str
    qty: float
    side: OrderSide
    order_type: str = "market"  # market, limit (simulated as market)
    status: OrderStatus = OrderStatus.PENDING
    
    # Timestamps
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    
    # Fill details
    filled_qty: float = 0.0
    filled_avg_price: Optional[float] = None
    
    # Metadata
    metadata: dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for logging"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'qty': self.qty,
            'side': self.side.value if isinstance(self.side, OrderSide) else self.side,
            'order_type': self.order_type,
            'status': self.status.value if isinstance(self.status, OrderStatus) else self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'filled_at': self.filled_at.isoformat() if self.filled_at else None,
            'filled_qty': self.filled_qty,
            'filled_avg_price': self.filled_avg_price,
            'metadata': self.metadata
        }


