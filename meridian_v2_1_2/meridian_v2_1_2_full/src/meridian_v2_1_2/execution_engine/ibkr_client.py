"""
IBKR Client

Interactive Brokers implementation using ib_insync.

Author: Meridian Team
Date: December 4, 2025
"""

from typing import List, Dict
from .broker_base import BrokerBase, Order, Position, AccountInfo

try:
    from ib_insync import IB, Stock, MarketOrder, LimitOrder
    IBKR_AVAILABLE = True
except ImportError:
    IBKR_AVAILABLE = False
    print("⚠️ ib_insync not installed. Install with: pip install ib_insync")


class IBKRClient(BrokerBase):
    """
    Interactive Brokers client.
    
    Requires IB Gateway or TWS running.
    
    Example:
        >>> client = IBKRClient(host='127.0.0.1', port=7497)
        >>> client.connect()
        >>> order = Order(symbol='SPY', qty=10, side='buy')
        >>> result = client.submit_order(order)
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 1):
        """
        Initialize IBKR client.
        
        Args:
            host: IB Gateway host
            port: IB Gateway port (7497 for TWS paper, 7496 for TWS live, 4001/4002 for Gateway)
            client_id: Unique client ID
        """
        if not IBKR_AVAILABLE:
            raise ImportError("ib_insync not installed")
        
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to IB Gateway/TWS"""
        try:
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ IBKR connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from IBKR"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
    
    def submit_order(self, order: Order) -> Dict:
        """Submit order to IBKR"""
        if not self.connected:
            raise RuntimeError("Not connected to IBKR")
        
        try:
            # Create contract
            contract = Stock(order.symbol, 'SMART', 'USD')
            
            # Create order
            if order.order_type == 'market':
                ib_order = MarketOrder(
                    'BUY' if order.side == 'buy' else 'SELL',
                    order.qty
                )
            elif order.order_type == 'limit':
                ib_order = LimitOrder(
                    'BUY' if order.side == 'buy' else 'SELL',
                    order.qty,
                    order.limit_price
                )
            else:
                return {'error': f'Unsupported order type: {order.order_type}'}
            
            # Place order
            trade = self.ib.placeOrder(contract, ib_order)
            
            return {
                'order_id': trade.order.orderId,
                'status': trade.orderStatus.status,
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side
            }
        except Exception as e:
            return {'error': str(e), 'status': 'failed'}
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel specific order"""
        try:
            self.ib.cancelOrder(order_id)
            return True
        except:
            return False
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            for order in self.ib.openOrders():
                self.ib.cancelOrder(order)
            return True
        except:
            return False
    
    def get_positions(self) -> List[Position]:
        """Get current positions"""
        if not self.connected:
            return []
        
        positions = []
        try:
            ib_positions = self.ib.positions()
            for pos in ib_positions:
                positions.append(Position(
                    symbol=pos.contract.symbol,
                    qty=float(pos.position),
                    avg_entry_price=float(pos.avgCost),
                    current_price=float(pos.marketPrice) if pos.marketPrice else 0,
                    market_value=float(pos.marketValue) if pos.marketValue else 0,
                    unrealized_pnl=float(pos.unrealizedPNL) if pos.unrealizedPNL else 0
                ))
        except Exception as e:
            print(f"⚠️ Error fetching positions: {e}")
        
        return positions
    
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        if not self.connected:
            raise RuntimeError("Not connected")
        
        summary = self.ib.accountSummary()
        
        # Extract key values
        equity = next((float(s.value) for s in summary if s.tag == 'NetLiquidation'), 0)
        cash = next((float(s.value) for s in summary if s.tag == 'TotalCashValue'), 0)
        buying_power = next((float(s.value) for s in summary if s.tag == 'BuyingPower'), 0)
        
        return AccountInfo(
            equity=equity,
            cash=cash,
            buying_power=buying_power,
            portfolio_value=equity
        )
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        try:
            trades = self.ib.trades()
            for trade in trades:
                if str(trade.order.orderId) == str(order_id):
                    return {
                        'order_id': trade.order.orderId,
                        'status': trade.orderStatus.status,
                        'filled_qty': trade.orderStatus.filled,
                        'avg_fill_price': trade.orderStatus.avgFillPrice
                    }
            return {'error': 'Order not found'}
        except Exception as e:
            return {'error': str(e)}
    
    def is_market_open(self) -> bool:
        """Check if market is open"""
        # IBKR doesn't have a simple market open check
        # This is a simplified implementation
        import datetime
        now = datetime.datetime.now()
        # Simple US market hours check (9:30 AM - 4:00 PM ET)
        return 9 <= now.hour < 16
