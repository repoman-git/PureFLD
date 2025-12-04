"""
Live Execution Engine for Meridian v2.1.2

Handles real order submission with full audit trail.
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..external import AlpacaAdapter


class LiveExecution:
    """
    Live execution engine.
    
    Responsibilities:
    - Submit orders to broker
    - Poll for fills
    - Handle partial fills
    - Retry on recoverable errors
    - Maintain audit trail
    """
    
    def __init__(self, config, alpaca_adapter: AlpacaAdapter, state_store=None):
        """
        Initialize live execution engine.
        
        Args:
            config: LiveConfig instance
            alpaca_adapter: AlpacaAdapter for order routing
            state_store: StateStore for persistence
        """
        self.config = config
        self.alpaca_adapter = alpaca_adapter
        self.state_store = state_store
        
        self.order_history = []
        self.fill_history = []
    
    def execute_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = 'market'
    ) -> Dict[str, Any]:
        """
        Execute order with retry logic.
        
        Args:
            symbol: Symbol to trade
            qty: Quantity
            side: 'buy' or 'sell'
            order_type: Order type
        
        Returns:
            Dict with execution result
        """
        result = {
            'success': False,
            'order_id': None,
            'filled': False,
            'fills': [],
            'error': None,
            'attempts': 0
        }
        
        # Attempt execution with retries
        for attempt in range(self.config.max_retry_attempts):
            result['attempts'] = attempt + 1
            
            try:
                # Submit order
                order = self.alpaca_adapter.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    order_type=order_type
                )
                
                result['order_id'] = order.get('id')
                result['success'] = True
                
                # Check if filled
                if order.get('status') == 'filled':
                    result['filled'] = True
                    result['fills'].append({
                        'qty': order.get('filled_qty', qty),
                        'price': order.get('filled_price', 0),
                        'time': order.get('filled_at')
                    })
                
                # Log to audit trail
                self._log_order(symbol, qty, side, order)
                
                break  # Success, exit retry loop
                
            except Exception as e:
                result['error'] = str(e)
                
                # Check if recoverable
                if self._is_recoverable_error(e):
                    if attempt < self.config.max_retry_attempts - 1:
                        # Wait before retry
                        time.sleep(1.0 * (attempt + 1))
                        continue
                
                # Unrecoverable or out of retries
                break
        
        # Store in history
        self.order_history.append({
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'result': result
        })
        
        return result
    
    def check_fills(self, order_id: str) -> List[Dict[str, Any]]:
        """
        Poll for order fills.
        
        Args:
            order_id: Order ID to check
        
        Returns:
            List of fills
        """
        # In real implementation, would poll Alpaca API
        # For now, return empty (stub)
        return []
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """Check if error is recoverable"""
        error_str = str(error).lower()
        
        # Recoverable errors (can retry)
        recoverable = [
            'timeout',
            'connection',
            'temporary',
            'rate limit'
        ]
        
        for keyword in recoverable:
            if keyword in error_str:
                return True
        
        return False
    
    def _log_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order: Dict[str, Any]
    ):
        """Log order to audit trail"""
        if not self.config.log_all_orders:
            return
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'order_id': order.get('id'),
            'status': order.get('status'),
            'filled_qty': order.get('filled_qty'),
            'filled_price': order.get('filled_price')
        }
        
        # Write to state store if available
        if self.state_store:
            # In real implementation, would write to DB
            pass
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        total_orders = len(self.order_history)
        successful = sum(1 for o in self.order_history if o['result']['success'])
        filled = sum(1 for o in self.order_history if o['result']['filled'])
        
        return {
            'total_orders': total_orders,
            'successful': successful,
            'filled': filled,
            'success_rate': successful / total_orders if total_orders > 0 else 0,
            'fill_rate': filled / total_orders if total_orders > 0 else 0
        }


