"""
State Cache for Meridian v2.1.2

Low-latency in-memory cache for streaming data.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from collections import deque


class StateCache:
    """
    In-memory cache for streaming state.
    
    Reduces DB calls and improves dashboard performance.
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize state cache.
        
        Args:
            max_size: Max items per collection
        """
        self.max_size = max_size
        
        # Price data
        self.latest_prices: Dict[str, Dict[str, Any]] = {}
        self.price_history: Dict[str, deque] = {}
        
        # Position data
        self.latest_positions: Dict[str, Dict[str, Any]] = {}
        
        # Order data
        self.latest_orders: Dict[str, Dict[str, Any]] = {}
        
        # Fill data
        self.recent_fills: deque = deque(maxlen=max_size)
        
        # Account data
        self.latest_account: Optional[Dict[str, Any]] = None
        
        # Risk data
        self.latest_risk: Optional[Dict[str, Any]] = None
        
        # Oversight data
        self.latest_oversight: Optional[Dict[str, Any]] = None
        
        # Metadata
        self.last_update: Dict[str, datetime] = {}
    
    def update_price(self, symbol: str, price_data: Dict[str, Any]):
        """
        Update price for symbol.
        
        Args:
            symbol: Symbol
            price_data: Price data dict
        """
        self.latest_prices[symbol] = price_data
        self.last_update[f'price_{symbol}'] = datetime.now()
        
        # Update history
        if symbol not in self.price_history:
            self.price_history[symbol] = deque(maxlen=self.max_size)
        
        self.price_history[symbol].append(price_data)
    
    def get_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get latest price for symbol.
        
        Args:
            symbol: Symbol
        
        Returns:
            Price data or None
        """
        return self.latest_prices.get(symbol)
    
    def update_positions(self, positions: Dict[str, Dict[str, Any]]):
        """
        Update positions.
        
        Args:
            positions: Dict of positions by symbol
        """
        self.latest_positions = positions
        self.last_update['positions'] = datetime.now()
    
    def get_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get latest positions"""
        return self.latest_positions
    
    def update_orders(self, orders: Dict[str, Dict[str, Any]]):
        """
        Update orders.
        
        Args:
            orders: Dict of orders by ID
        """
        self.latest_orders = orders
        self.last_update['orders'] = datetime.now()
    
    def get_orders(self) -> Dict[str, Dict[str, Any]]:
        """Get latest orders"""
        return self.latest_orders
    
    def add_fill(self, fill_data: Dict[str, Any]):
        """
        Add fill to history.
        
        Args:
            fill_data: Fill data dict
        """
        self.recent_fills.append(fill_data)
        self.last_update['fills'] = datetime.now()
    
    def get_fills(self, limit: int = 100) -> list:
        """
        Get recent fills.
        
        Args:
            limit: Max fills to return
        
        Returns:
            List of fills
        """
        fills = list(self.recent_fills)
        return fills[-limit:]
    
    def update_account(self, account_data: Dict[str, Any]):
        """
        Update account data.
        
        Args:
            account_data: Account data dict
        """
        self.latest_account = account_data
        self.last_update['account'] = datetime.now()
    
    def get_account(self) -> Optional[Dict[str, Any]]:
        """Get latest account data"""
        return self.latest_account
    
    def update_risk(self, risk_data: Dict[str, Any]):
        """
        Update risk data.
        
        Args:
            risk_data: Risk data dict
        """
        self.latest_risk = risk_data
        self.last_update['risk'] = datetime.now()
    
    def get_risk(self) -> Optional[Dict[str, Any]]:
        """Get latest risk data"""
        return self.latest_risk
    
    def update_oversight(self, oversight_data: Dict[str, Any]):
        """
        Update oversight data.
        
        Args:
            oversight_data: Oversight data dict
        """
        self.latest_oversight = oversight_data
        self.last_update['oversight'] = datetime.now()
    
    def get_oversight(self) -> Optional[Dict[str, Any]]:
        """Get latest oversight data"""
        return self.latest_oversight
    
    def get_last_update(self, key: str) -> Optional[datetime]:
        """
        Get last update time for key.
        
        Args:
            key: Cache key
        
        Returns:
            Last update datetime or None
        """
        return self.last_update.get(key)
    
    def clear(self):
        """Clear all cache"""
        self.latest_prices = {}
        self.price_history = {}
        self.latest_positions = {}
        self.latest_orders = {}
        self.recent_fills.clear()
        self.latest_account = None
        self.latest_risk = None
        self.latest_oversight = None
        self.last_update = {}

