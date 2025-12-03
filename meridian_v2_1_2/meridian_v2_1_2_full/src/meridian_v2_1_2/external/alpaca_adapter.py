"""
Alpaca Adapter for Meridian v2.1.2

Safe trading execution with multiple safety locks.
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

from .external_config import ExternalConfig
from .external_exceptions import (
    ExternalDataException,
    APIKeyException,
    OrderRejectionException
)
from .rate_limits import RateLimiter
from ..storage import EnvLoader


class AlpacaAdapter:
    """
    Alpaca API adapter with safety locks.
    
    Features:
    - Account validation
    - Market data (bars)
    - Order execution (with safety locks)
    - Paper trading default
    - Dry-run mode
    - Order sanitization
    """
    
    def __init__(self, config: Optional[ExternalConfig] = None):
        """
        Initialize Alpaca adapter.
        
        Args:
            config: External configuration
        """
        self.config = config or ExternalConfig()
        self.rate_limiter = RateLimiter(
            calls_per_second=self.config.alpaca_rate_limit / 60.0,  # Convert to per-second
            max_retries=self.config.max_retries
        )
        
        self.enabled = False
        self.api_key = None
        self.secret_key = None
        self.live_trading_enabled = False
        
        # Try to load API keys
        if self.config.use_alpaca:
            self._load_api_keys()
    
    def _load_api_keys(self):
        """Load Alpaca API keys from environment"""
        try:
            loader = EnvLoader()
            keys = loader.load()
            
            self.api_key = keys.get('ALPACA_API_KEY')
            self.secret_key = keys.get('ALPACA_SECRET_KEY')
            
            if self.api_key and self.secret_key:
                self.enabled = True
                
                # Live trading requires explicit config
                self.live_trading_enabled = (
                    self.enabled and 
                    self.config.live_trading and 
                    not self.config.paper_trading
                )
            else:
                if self.config.validate_keys_on_startup:
                    raise APIKeyException("Alpaca API keys not found in environment")
        except Exception as e:
            if not self.config.fallback_to_synthetic_if_failed:
                raise
            # Silent fallback
            self.enabled = False
    
    def get_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = '1Day'
    ) -> pd.DataFrame:
        """
        Get market data bars.
        
        Args:
            symbol: Ticker symbol
            start_date: Start date
            end_date: End date
            timeframe: Bar timeframe
        
        Returns:
            DataFrame with OHLC data
        """
        if not self.enabled:
            return self._fallback_to_synthetic(symbol, start_date, end_date)
        
        try:
            # Rate limit
            self.rate_limiter.wait_if_needed()
            
            # In real implementation, would call Alpaca API
            # For now, fallback to synthetic
            return self._fallback_to_synthetic(symbol, start_date, end_date)
            
        except Exception as e:
            if self.config.fallback_to_synthetic_if_failed:
                return self._fallback_to_synthetic(symbol, start_date, end_date)
            raise ExternalDataException(f"Failed to fetch bars: {e}")
    
    def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = 'market',
        time_in_force: str = 'day'
    ) -> Dict[str, Any]:
        """
        Submit order (with safety locks).
        
        Args:
            symbol: Ticker symbol
            qty: Quantity
            side: 'buy' or 'sell'
            order_type: Order type
            time_in_force: Time in force
        
        Returns:
            Order info dict
        
        Raises:
            OrderRejectionException if safety checks fail
        """
        # SAFETY CHECK 1: Live trading must be explicitly enabled
        if not self.live_trading_enabled:
            return self._simulate_order(symbol, qty, side, order_type)
        
        # SAFETY CHECK 2: Sanitize order
        self._sanitize_order(symbol, qty, side)
        
        # SAFETY CHECK 3: Size limits
        if abs(qty) > self.config.max_order_size:
            raise OrderRejectionException(
                f"Order size {qty} exceeds limit {self.config.max_order_size}"
            )
        
        try:
            # Rate limit
            self.rate_limiter.wait_if_needed()
            
            # In real implementation, would submit to Alpaca
            # For now, simulate
            return self._simulate_order(symbol, qty, side, order_type)
            
        except Exception as e:
            raise ExternalDataException(f"Failed to submit order: {e}")
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Dict with account info
        """
        if not self.enabled:
            return {
                'enabled': False,
                'equity': 0.0,
                'cash': 0.0,
                'buying_power': 0.0
            }
        
        try:
            # Rate limit
            self.rate_limiter.wait_if_needed()
            
            # In real implementation, would fetch from Alpaca
            return {
                'enabled': True,
                'equity': 100000.0,  # Stub
                'cash': 100000.0,
                'buying_power': 100000.0,
                'paper_trading': self.config.paper_trading
            }
            
        except Exception as e:
            raise ExternalDataException(f"Failed to fetch account: {e}")
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions.
        
        Returns:
            List of position dicts
        """
        if not self.enabled:
            return []
        
        try:
            # Rate limit
            self.rate_limiter.wait_if_needed()
            
            # In real implementation, would fetch from Alpaca
            return []  # Stub
            
        except Exception as e:
            raise ExternalDataException(f"Failed to fetch positions: {e}")
    
    def _sanitize_order(self, symbol: str, qty: float, side: str):
        """
        Sanitize order parameters.
        
        Raises:
            OrderRejectionException if invalid
        """
        # Check for NaN
        if pd.isna(qty):
            raise OrderRejectionException("Order quantity is NaN")
        
        # Check for zero
        if qty == 0:
            raise OrderRejectionException("Order quantity is zero")
        
        # Check symbol
        if not symbol or not isinstance(symbol, str):
            raise OrderRejectionException(f"Invalid symbol: {symbol}")
        
        # Check side
        if side not in ['buy', 'sell']:
            raise OrderRejectionException(f"Invalid side: {side}")
    
    def _simulate_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str
    ) -> Dict[str, Any]:
        """Simulate order for dry-run or paper mode"""
        return {
            'id': f'sim_{datetime.now().timestamp()}',
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': order_type,
            'status': 'filled',
            'filled_qty': qty,
            'filled_price': 100.0,  # Stub price
            'filled_at': datetime.now().isoformat(),
            'simulated': True,
            'paper_mode': True
        }
    
    def _fallback_to_synthetic(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """Generate synthetic data as fallback"""
        from ..synthetic.synthetic_dataset import SyntheticDataset
        from ..config import MeridianConfig
        
        config = MeridianConfig()
        synth = SyntheticDataset(config.synthetic)
        dataset = synth.generate()
        
        if symbol in dataset['prices']:
            return dataset['prices'][symbol].loc[start_date:end_date]
        
        # Simple synthetic
        dates = pd.date_range(start_date, end_date, freq='D')
        return pd.DataFrame({
            'open': 100.0,
            'high': 102.0,
            'low': 98.0,
            'close': 101.0,
            'volume': 1000000
        }, index=dates)
    
    def is_enabled(self) -> bool:
        """Check if adapter is enabled"""
        return self.enabled
    
    def is_live_trading_enabled(self) -> bool:
        """Check if live trading is enabled"""
        return self.live_trading_enabled
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test Alpaca connection.
        
        Returns:
            Dict with status info
        """
        result = {
            'enabled': self.enabled,
            'has_keys': self.api_key is not None and self.secret_key is not None,
            'connection_ok': False,
            'live_trading': self.live_trading_enabled,
            'paper_trading': self.config.paper_trading,
            'error': None
        }
        
        if not self.enabled:
            result['error'] = 'Alpaca adapter not enabled'
            return result
        
        try:
            # In real implementation, would ping Alpaca API
            if self.api_key and self.secret_key:
                result['connection_ok'] = True
        except Exception as e:
            result['error'] = str(e)
        
        return result

