"""
Simulated Broker for Meridian v2.1.2

In-memory broker that mimics Alpaca REST API.
"""

from typing import List, Dict, Optional
from datetime import datetime
import uuid

from .sim_order import SimulatedOrder, OrderStatus, OrderSide
from .sim_portfolio import SimulatedPortfolio
from .sim_fills import generate_fill


class SimulatedBroker:
    """
    Simulated broker - Alpaca twin.
    
    Manages:
    - Order submission
    - Fill generation
    - Portfolio state
    - Position tracking
    """
    
    def __init__(self, starting_capital: float = 100000.0, config=None):
        """
        Initialize broker.
        
        Args:
            starting_capital: Starting cash
            config: Paper sim configuration
        """
        self.portfolio = SimulatedPortfolio(starting_capital)
        self.orders: Dict[str, SimulatedOrder] = {}
        self.fills: List[dict] = []
        self.config = config
    
    def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = "market"
    ) -> SimulatedOrder:
        """
        Submit order.
        
        Args:
            symbol: Symbol
            qty: Quantity
            side: "buy" or "sell"
            order_type: Order type
        
        Returns:
            SimulatedOrder
        """
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Create order
        order = SimulatedOrder(
            order_id=order_id,
            symbol=symbol,
            qty=abs(qty),
            side=OrderSide(side.lower()),
            order_type=order_type,
            status=OrderStatus.SUBMITTED,
            submitted_at=datetime.now()
        )
        
        # Store
        self.orders[order_id] = order
        
        return order
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel order.
        
        Args:
            order_id: Order ID
        
        Returns:
            bool: Success
        """
        if order_id in self.orders:
            order = self.orders[order_id]
            if order.status == OrderStatus.SUBMITTED:
                order.status = OrderStatus.CANCELLED
                return True
        return False
    
    def generate_fills(
        self,
        current_prices: Dict[str, float],
        next_opens: Optional[Dict[str, float]] = None
    ) -> List[dict]:
        """
        Generate fills for pending orders.
        
        Args:
            current_prices: Current EOD prices
            next_opens: Next day open prices
        
        Returns:
            List of fills
        """
        fills = []
        
        for order_id, order in self.orders.items():
            if order.status == OrderStatus.SUBMITTED:
                symbol = order.symbol
                
                if symbol in current_prices:
                    # Generate fill price
                    current_price = current_prices[symbol]
                    next_open = next_opens.get(symbol) if next_opens else None
                    
                    slippage_bps = self.config.paper_sim.slippage_bps if self.config else 5.0
                    use_gap = self.config.paper_sim.gap_model if self.config else True
                    
                    fill_price = generate_fill(
                        order,
                        current_price,
                        next_open,
                        slippage_bps,
                        use_gap
                    )
                    
                    # Update order
                    order.status = OrderStatus.FILLED
                    order.filled_at = datetime.now()
                    order.filled_qty = order.qty
                    order.filled_avg_price = fill_price
                    
                    # Update portfolio
                    qty_change = order.qty if order.side == OrderSide.BUY else -order.qty
                    self.portfolio.update_position(symbol, qty_change, fill_price)
                    
                    # Record fill
                    fill = {
                        'order_id': order_id,
                        'symbol': symbol,
                        'qty': order.filled_qty,
                        'price': fill_price,
                        'side': order.side.value,
                        'filled_at': order.filled_at.isoformat()
                    }
                    fills.append(fill)
                    self.fills.append(fill)
        
        return fills
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        return self.portfolio.to_dict()
    
    def get_open_orders(self) -> List[SimulatedOrder]:
        """Get open orders"""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.SUBMITTED
        ]
    
    def get_filled_orders(self) -> List[SimulatedOrder]:
        """Get filled orders"""
        return [
            order for order in self.orders.values()
            if order.status == OrderStatus.FILLED
        ]
    
    def get_fills(self) -> List[dict]:
        """Get all fills"""
        return self.fills
    
    def update_market_values(self, prices: Dict[str, float]) -> None:
        """Update portfolio with current prices"""
        self.portfolio.update_market_values(prices)


