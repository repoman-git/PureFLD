"""Position Manager - Track open positions"""
from typing import List, Dict
from .broker_base import Position

class PositionManager:
    """Manages and tracks open positions"""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
    
    def update(self, broker_positions: List[Position]):
        """Update positions from broker"""
        self.positions = {pos.symbol: pos for pos in broker_positions}
    
    def get_position(self, symbol: str) -> Position:
        """Get position for symbol"""
        return self.positions.get(symbol)
    
    def has_position(self, symbol: str) -> bool:
        """Check if position exists"""
        return symbol in self.positions and self.positions[symbol].qty != 0
    
    def net_exposure(self) -> float:
        """Calculate total net exposure"""
        return sum(pos.qty for pos in self.positions.values())
    
    def gross_exposure(self) -> float:
        """Calculate total gross exposure"""
        return sum(abs(pos.qty) for pos in self.positions.values())
    
    def total_market_value(self) -> float:
        """Calculate total market value"""
        return sum(pos.market_value for pos in self.positions.values())
    
    def total_unrealized_pnl(self) -> float:
        """Calculate total unrealized P&L"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
