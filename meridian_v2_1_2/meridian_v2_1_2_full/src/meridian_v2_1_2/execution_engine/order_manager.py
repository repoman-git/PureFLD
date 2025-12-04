"""Order Manager - Converts signals to orders"""
import pandas as pd
from typing import List, Dict
from .broker_base import Order

class OrderManager:
    """Converts trading signals and allocations into executable orders"""
    
    def __init__(self, min_order_value: float = 100):
        self.min_order_value = min_order_value
    
    def generate_orders(
        self,
        signals: Dict[str, pd.Series],
        prices: Dict[str, float],
        allocation: Dict[str, float],
        account_value: float
    ) -> List[Order]:
        """Generate orders from signals and allocation"""
        orders = []
        
        for symbol in signals:
            if symbol not in allocation or symbol not in prices:
                continue
            
            sig = signals[symbol].iloc[-1] if isinstance(signals[symbol], pd.Series) else signals[symbol]
            weight = allocation.get(symbol, 0)
            price = prices[symbol]
            
            if weight == 0 or sig == 0:
                continue
            
            # Calculate dollar amount
            dollar_amount = abs(weight) * account_value
            
            if dollar_amount < self.min_order_value:
                continue
            
            # Calculate quantity
            qty = int(dollar_amount / price)
            if qty == 0:
                continue
            
            # Determine side
            side = 'buy' if sig > 0 else 'sell'
            
            orders.append(Order(
                symbol=symbol,
                qty=qty,
                side=side,
                order_type='market'
            ))
        
        return orders
