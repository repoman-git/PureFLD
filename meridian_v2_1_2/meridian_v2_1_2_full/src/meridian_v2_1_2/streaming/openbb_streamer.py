"""
OpenBB Streamer for Meridian v2.1.2

Market data polling (NOT for execution).
"""

from typing import Dict, Any, List
from datetime import datetime


class OpenBBStreamer:
    """
    Market data streamer using OpenBB.
    
    MONITORING ONLY - Does not trigger trades.
    """
    
    def __init__(self, config, openbb_adapter=None):
        """
        Initialize OpenBB streamer.
        
        Args:
            config: StreamerConfig instance
            openbb_adapter: OpenBBAdapter (optional)
        """
        self.config = config
        self.openbb = openbb_adapter
        self.last_update = {}
    
    def poll_prices(self) -> List[Dict[str, Any]]:
        """
        Poll latest prices for configured symbols.
        
        Returns:
            List of price dicts
        """
        prices = []
        
        for symbol in self.config.openbb_symbols:
            try:
                price_data = self._fetch_symbol_data(symbol)
                if price_data:
                    prices.append(price_data)
                    self.last_update[symbol] = datetime.now()
            
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
        
        return prices
    
    def _fetch_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch data for single symbol.
        
        Args:
            symbol: Symbol to fetch
        
        Returns:
            Price data dict
        """
        # In full implementation, would use OpenBB adapter
        # For now, return synthetic data
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'price': 195.50 if symbol == 'GLD' else 25.30,
            'open': 195.00 if symbol == 'GLD' else 25.20,
            'high': 196.00 if symbol == 'GLD' else 25.40,
            'low': 194.80 if symbol == 'GLD' else 25.10,
            'close': 195.50 if symbol == 'GLD' else 25.30,
            'volume': 1000000
        }
    
    def is_stale(self, symbol: str, max_age_seconds: int = 60) -> bool:
        """
        Check if data is stale.
        
        Args:
            symbol: Symbol to check
            max_age_seconds: Max age before considered stale
        
        Returns:
            True if stale
        """
        if symbol not in self.last_update:
            return True
        
        age = (datetime.now() - self.last_update[symbol]).total_seconds()
        return age > max_age_seconds


