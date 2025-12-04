"""
Simulated Portfolio for Meridian v2.1.2

Tracks positions, cash, PnL for paper trading.
"""

from typing import Dict
from dataclasses import dataclass, field


@dataclass
class Position:
    """Single position"""
    symbol: str
    qty: float
    avg_cost: float
    market_value: float = 0.0
    unrealized_pl: float = 0.0


class SimulatedPortfolio:
    """
    Simulated portfolio tracker.
    
    Mimics Alpaca portfolio state.
    """
    
    def __init__(self, starting_capital: float = 100000.0):
        """
        Initialize portfolio.
        
        Args:
            starting_capital: Starting cash
        """
        self.cash = starting_capital
        self.starting_capital = starting_capital
        self.positions: Dict[str, Position] = {}
        self.realized_pl = 0.0
    
    def get_position(self, symbol: str) -> Position:
        """Get position for symbol"""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol, qty=0.0, avg_cost=0.0)
        return self.positions[symbol]
    
    def update_position(
        self,
        symbol: str,
        qty_change: float,
        price: float
    ) -> None:
        """
        Update position after fill.
        
        Args:
            symbol: Symbol
            qty_change: Change in quantity (+ for buy, - for sell)
            price: Fill price
        """
        pos = self.get_position(symbol)
        
        # Calculate cost/proceeds
        cost = abs(qty_change) * price
        
        if qty_change > 0:
            # Buy
            if pos.qty >= 0:
                # Adding to long
                total_cost = pos.avg_cost * pos.qty + cost
                pos.qty += qty_change
                pos.avg_cost = total_cost / pos.qty if pos.qty > 0 else 0.0
            else:
                # Covering short
                if abs(qty_change) > abs(pos.qty):
                    # Cover and go long
                    cover_qty = abs(pos.qty)
                    cover_pl = cover_qty * (pos.avg_cost - price)
                    self.realized_pl += cover_pl
                    self.cash += cover_pl
                    
                    remaining = qty_change - cover_qty
                    pos.qty = remaining
                    pos.avg_cost = price
                else:
                    # Partial cover
                    cover_pl = abs(qty_change) * (pos.avg_cost - price)
                    self.realized_pl += cover_pl
                    self.cash += cover_pl
                    pos.qty += qty_change
            
            self.cash -= cost
        
        else:
            # Sell
            if pos.qty > 0:
                # Selling long
                if abs(qty_change) <= pos.qty:
                    # Partial or full sell
                    sell_pl = abs(qty_change) * (price - pos.avg_cost)
                    self.realized_pl += sell_pl
                    self.cash += sell_pl + abs(qty_change) * pos.avg_cost
                    pos.qty += qty_change
                else:
                    # Sell long and go short
                    sell_pl = pos.qty * (price - pos.avg_cost)
                    self.realized_pl += sell_pl
                    self.cash += sell_pl + pos.qty * pos.avg_cost
                    
                    remaining = qty_change + pos.qty
                    pos.qty = remaining
                    pos.avg_cost = price
            else:
                # Adding to short
                if pos.qty < 0:
                    total_cost = pos.avg_cost * abs(pos.qty) + cost
                    pos.qty += qty_change
                    pos.avg_cost = total_cost / abs(pos.qty) if pos.qty != 0 else 0.0
                else:
                    pos.qty = qty_change
                    pos.avg_cost = price
            
            self.cash += cost
    
    def update_market_values(self, prices: Dict[str, float]) -> None:
        """
        Update market values and unrealized PnL.
        
        Args:
            prices: Current prices per symbol
        """
        for symbol, pos in self.positions.items():
            if symbol in prices:
                current_price = prices[symbol]
                pos.market_value = pos.qty * current_price
                
                if pos.qty > 0:
                    pos.unrealized_pl = pos.qty * (current_price - pos.avg_cost)
                elif pos.qty < 0:
                    pos.unrealized_pl = abs(pos.qty) * (pos.avg_cost - current_price)
                else:
                    pos.unrealized_pl = 0.0
    
    def get_total_equity(self) -> float:
        """Get total equity (cash + positions)"""
        position_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + position_value
    
    def get_total_unrealized_pl(self) -> float:
        """Get total unrealized PnL"""
        return sum(pos.unrealized_pl for pos in self.positions.values())
    
    def get_exposure(self) -> Dict[str, float]:
        """Get exposure metrics"""
        total_equity = self.get_total_equity()
        
        gross_exposure = sum(abs(pos.market_value) for pos in self.positions.values())
        net_exposure = sum(pos.market_value for pos in self.positions.values())
        
        return {
            'gross': gross_exposure,
            'net': net_exposure,
            'gross_pct': gross_exposure / total_equity if total_equity > 0 else 0.0,
            'net_pct': net_exposure / total_equity if total_equity > 0 else 0.0
        }
    
    def to_dict(self) -> dict:
        """Export portfolio state"""
        return {
            'cash': self.cash,
            'equity': self.get_total_equity(),
            'realized_pl': self.realized_pl,
            'unrealized_pl': self.get_total_unrealized_pl(),
            'positions': {
                symbol: {
                    'qty': pos.qty,
                    'avg_cost': pos.avg_cost,
                    'market_value': pos.market_value,
                    'unrealized_pl': pos.unrealized_pl
                }
                for symbol, pos in self.positions.items() if pos.qty != 0
            },
            'exposure': self.get_exposure()
        }


