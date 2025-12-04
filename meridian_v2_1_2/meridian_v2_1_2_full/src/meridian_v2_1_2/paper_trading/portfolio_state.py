"""
Portfolio State Machine

Tracks simulated portfolio state for paper trading.
Positions, cash, equity, exposure tracking.

⚠️  EDUCATIONAL SIMULATION ONLY
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class Position:
    """Single position in portfolio"""
    symbol: str
    quantity: float
    entry_price: float
    current_price: float
    entry_date: str
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0


class PortfolioState:
    """
    Paper trading portfolio state machine.
    
    Tracks all positions, cash, and portfolio value over time.
    
    ⚠️  SIMULATED PORTFOLIO - NO REAL MONEY
    """
    
    def __init__(self, initial_cash: float = 100000.0):
        """
        Initialize portfolio.
        
        Args:
            initial_cash: Starting cash (default: $100,000)
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.value_history: List[Dict[str, Any]] = []
        
        # Track portfolio value at initialization
        self.value_history.append({
            'timestamp': datetime.now().isoformat(),
            'total_value': initial_cash,
            'cash': initial_cash,
            'positions_value': 0.0
        })
    
    def apply_fill(
        self,
        symbol: str,
        quantity: float,
        fill_price: float,
        side: str  # 'BUY' or 'SELL'
    ) -> bool:
        """
        Apply a simulated fill to portfolio.
        
        Args:
            symbol: Asset symbol
            quantity: Number of shares/contracts (positive)
            fill_price: Fill price
            side: 'BUY' or 'SELL'
        
        Returns:
            True if successful, False if insufficient cash/shares
        """
        cost = quantity * fill_price
        
        if side == 'BUY':
            # Check if enough cash
            if cost > self.cash:
                return False  # Insufficient funds
            
            # Deduct cash
            self.cash -= cost
            
            # Add or update position
            if symbol in self.positions:
                # Average up
                pos = self.positions[symbol]
                total_qty = pos.quantity + quantity
                avg_price = ((pos.quantity * pos.entry_price) + cost) / total_qty
                
                pos.quantity = total_qty
                pos.entry_price = avg_price
                pos.current_price = fill_price
            else:
                # New position
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    entry_price=fill_price,
                    current_price=fill_price,
                    entry_date=datetime.now().isoformat()
                )
        
        elif side == 'SELL':
            # Check if enough shares
            if symbol not in self.positions:
                return False  # No position to sell
            
            pos = self.positions[symbol]
            if quantity > pos.quantity:
                return False  # Insufficient shares
            
            # Add cash
            self.cash += cost
            
            # Reduce or close position
            pos.quantity -= quantity
            
            if pos.quantity <= 0:
                del self.positions[symbol]
        
        return True
    
    def update_valuations(self, latest_prices: Dict[str, float]):
        """
        Update position valuations with latest prices.
        
        Args:
            latest_prices: Dictionary mapping symbol -> current_price
        """
        for symbol, pos in self.positions.items():
            if symbol in latest_prices:
                pos.current_price = latest_prices[symbol]
                
                # Calculate unrealized PnL
                pos.unrealized_pnl = (pos.current_price - pos.entry_price) * pos.quantity
                pos.unrealized_pnl_pct = (pos.current_price / pos.entry_price - 1)
        
        # Record portfolio value
        total_value = self.get_total_value()
        
        self.value_history.append({
            'timestamp': datetime.now().isoformat(),
            'total_value': total_value,
            'cash': self.cash,
            'positions_value': total_value - self.cash
        })
    
    def get_total_value(self) -> float:
        """Get total portfolio value (cash + positions)"""
        positions_value = sum(
            pos.quantity * pos.current_price
            for pos in self.positions.values()
        )
        return self.cash + positions_value
    
    def calculate_exposure(self) -> Dict[str, float]:
        """
        Calculate exposure by asset (as % of portfolio).
        
        Returns:
            Dictionary mapping symbol -> exposure_pct
        """
        total_value = self.get_total_value()
        
        if total_value == 0:
            return {}
        
        exposures = {}
        for symbol, pos in self.positions.items():
            position_value = pos.quantity * pos.current_price
            exposures[symbol] = position_value / total_value
        
        return exposures
    
    def calculate_portfolio_risk(self) -> float:
        """
        Estimate total portfolio risk.
        
        Simple approximation based on position sizes.
        
        Returns:
            Estimated portfolio risk (0-1)
        """
        # Sum of individual position risks (simplified)
        total_risk = sum(
            (pos.quantity * pos.current_price / self.get_total_value()) * 0.02  # 2% risk per position
            for pos in self.positions.values()
        )
        
        return min(1.0, total_risk)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio state to dictionary"""
        return {
            'cash': self.cash,
            'total_value': self.get_total_value(),
            'positions': {
                symbol: asdict(pos)
                for symbol, pos in self.positions.items()
            },
            'exposures': self.calculate_exposure(),
            'portfolio_risk': self.calculate_portfolio_risk(),
            'timestamp': datetime.now().isoformat()
        }


