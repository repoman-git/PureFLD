"""
Broker Base Class

Abstract interface for all broker implementations.

Author: Meridian Team
Date: December 4, 2025
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Order:
    """Order representation"""
    symbol: str
    qty: float
    side: str  # 'buy' or 'sell'
    order_type: str = 'market'
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: str = 'gtc'


@dataclass
class Position:
    """Position representation"""
    symbol: str
    qty: float
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float


@dataclass
class AccountInfo:
    """Account information"""
    equity: float
    cash: float
    buying_power: float
    portfolio_value: float


class BrokerBase(ABC):
    """
    Abstract base class for broker implementations.
    
    All broker clients (Alpaca, IBKR, etc.) must implement this interface.
    """
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to broker API"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Disconnect from broker API"""
        pass
    
    @abstractmethod
    def submit_order(self, order: Order) -> Dict:
        """Submit an order"""
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Position]:
        """Get current positions"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        pass
    
    @abstractmethod
    def is_market_open(self) -> bool:
        """Check if market is open"""
        pass
