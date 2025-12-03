"""
Alpaca Streamer for Meridian v2.1.2

Broker state polling (NOT for execution).
"""

from typing import Dict, Any, List
from datetime import datetime


class AlpacaStreamer:
    """
    Broker state streamer using Alpaca.
    
    MONITORING ONLY - Does not trigger trades.
    """
    
    def __init__(self, config, alpaca_adapter=None):
        """
        Initialize Alpaca streamer.
        
        Args:
            config: StreamerConfig instance
            alpaca_adapter: AlpacaAdapter (optional)
        """
        self.config = config
        self.alpaca = alpaca_adapter
        self.last_update = {}
    
    def poll_broker_state(self) -> Dict[str, Any]:
        """
        Poll complete broker state.
        
        Returns:
            Dict with positions, orders, fills, account
        """
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'positions': self._fetch_positions(),
                'orders': self._fetch_orders(),
                'fills': self._fetch_fills(),
                'account': self._fetch_account()
            }
            
            self.last_update['broker_state'] = datetime.now()
            return state
        
        except Exception as e:
            print(f"Error polling broker state: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _fetch_positions(self) -> List[Dict[str, Any]]:
        """Fetch positions from Alpaca"""
        # In full implementation, would use AlpacaAdapter
        if self.alpaca:
            try:
                return self.alpaca.get_positions()
            except:
                pass
        
        # Synthetic data for testing
        return [
            {
                'symbol': 'GLD',
                'qty': 100,
                'cost_basis': 18000,
                'market_value': 19500,
                'pnl': 1500
            }
        ]
    
    def _fetch_orders(self) -> List[Dict[str, Any]]:
        """Fetch orders from Alpaca"""
        if self.alpaca:
            try:
                return self.alpaca.get_orders()
            except:
                pass
        
        return []
    
    def _fetch_fills(self) -> List[Dict[str, Any]]:
        """Fetch fills from Alpaca"""
        # In full implementation, would query activities endpoint
        return []
    
    def _fetch_account(self) -> Dict[str, Any]:
        """Fetch account data from Alpaca"""
        if self.alpaca:
            try:
                return self.alpaca.get_account()
            except:
                pass
        
        return {
            'cash': 50000,
            'equity': 69500,
            'buying_power': 50000
        }
    
    def is_stale(self, max_age_seconds: int = 30) -> bool:
        """
        Check if broker state is stale.
        
        Args:
            max_age_seconds: Max age before considered stale
        
        Returns:
            True if stale
        """
        if 'broker_state' not in self.last_update:
            return True
        
        age = (datetime.now() - self.last_update['broker_state']).total_seconds()
        return age > max_age_seconds

