"""
Alpaca Client

Alpaca broker implementation for paper and live trading.

Author: Meridian Team
Date: December 4, 2025
"""

from typing import List, Dict
from .broker_base import BrokerBase, Order, Position, AccountInfo

try:
    import alpaca_trade_api as tradeapi
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("⚠️ alpaca-trade-api not installed. Install with: pip install alpaca-trade-api")


class AlpacaClient(BrokerBase):
    """
    Alpaca broker client.
    
    Supports both paper and live trading.
    
    Paper Trading (FREE):
        endpoint = "https://paper-api.alpaca.markets"
    
    Live Trading:
        endpoint = "https://api.alpaca.markets"
    
    Example:
        >>> client = AlpacaClient(
        ...     api_key="YOUR_KEY",
        ...     secret_key="YOUR_SECRET",
        ...     endpoint="https://paper-api.alpaca.markets"
        ... )
        >>> 
        >>> # Place order
        >>> order = Order(symbol='SPY', qty=10, side='buy')
        >>> result = client.submit_order(order)
    """
    
    def __init__(self, api_key: str, secret_key: str, endpoint: str):
        """
        Initialize Alpaca client.
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            endpoint: Paper or live endpoint
        """
        if not ALPACA_AVAILABLE:
            raise ImportError("alpaca-trade-api not installed")
        
        self.api_key = api_key
        self.secret_key = secret_key
        self.endpoint = endpoint
        self.api = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Alpaca API"""
        try:
            self.api = tradeapi.REST(
                self.api_key,
                self.secret_key,
                self.endpoint,
                api_version='v2'
            )
            # Test connection
            self.api.get_account()
            self.connected = True
            return True
        except Exception as e:
            print(f"❌ Alpaca connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Alpaca"""
        self.connected = False
        self.api = None
    
    def submit_order(self, order: Order) -> Dict:
        """Submit order to Alpaca"""
        if not self.connected:
            raise RuntimeError("Not connected to Alpaca")
        
        try:
            result = self.api.submit_order(
                symbol=order.symbol,
                qty=order.qty,
                side=order.side,
                type=order.order_type,
                time_in_force=order.time_in_force,
                limit_price=order.limit_price,
                stop_price=order.stop_price
            )
            return {
                'order_id': result.id,
                'status': result.status,
                'symbol': result.symbol,
                'qty': result.qty,
                'side': result.side
            }
        except Exception as e:
            return {'error': str(e), 'status': 'failed'}
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel specific order"""
        try:
            self.api.cancel_order(order_id)
            return True
        except:
            return False
    
    def cancel_all_orders(self) -> bool:
        """Cancel all open orders"""
        try:
            self.api.cancel_all_orders()
            return True
        except:
            return False
    
    def get_positions(self) -> List[Position]:
        """Get current positions"""
        if not self.connected:
            return []
        
        positions = []
        try:
            alpaca_positions = self.api.list_positions()
            for pos in alpaca_positions:
                positions.append(Position(
                    symbol=pos.symbol,
                    qty=float(pos.qty),
                    avg_entry_price=float(pos.avg_entry_price),
                    current_price=float(pos.current_price),
                    market_value=float(pos.market_value),
                    unrealized_pnl=float(pos.unrealized_pl)
                ))
        except Exception as e:
            print(f"⚠️ Error fetching positions: {e}")
        
        return positions
    
    def get_account_info(self) -> AccountInfo:
        """Get account information"""
        if not self.connected:
            raise RuntimeError("Not connected")
        
        account = self.api.get_account()
        return AccountInfo(
            equity=float(account.equity),
            cash=float(account.cash),
            buying_power=float(account.buying_power),
            portfolio_value=float(account.portfolio_value)
        )
    
    def get_order_status(self, order_id: str) -> Dict:
        """Get order status"""
        try:
            order = self.api.get_order(order_id)
            return {
                'order_id': order.id,
                'status': order.status,
                'filled_qty': order.filled_qty,
                'filled_avg_price': order.filled_avg_price
            }
        except Exception as e:
            return {'error': str(e)}
    
    def is_market_open(self) -> bool:
        """Check if market is open"""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except:
            return False
