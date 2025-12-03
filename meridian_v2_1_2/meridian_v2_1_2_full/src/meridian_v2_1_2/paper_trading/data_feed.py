"""
Live Data Feed

Pull real-time price data for paper trading simulation.
Uses free-tier providers (Yahoo Finance primary).
Supports up to 20+ years of historical data.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime, timedelta


class LiveDataFeed:
    """
    Live data feed for paper trading.
    
    Supports extensive historical data:
    - Up to 20 years for deep backtesting
    - Multiple timeframes (1d, 1h, 5m, etc.)
    - Free-tier Yahoo Finance data
    
    ⚠️  EDUCATIONAL ONLY - Uses free-tier data sources
    """
    
    def __init__(self, provider: str = 'yahoo'):
        """
        Initialize live data feed.
        
        Args:
            provider: Data provider ('yahoo', 'tiingo', 'alpaca')
        """
        self.provider = provider
        self.cache = {}  # Simple cache to avoid rate limits
        self.last_fetch = {}
    
    def fetch_latest_price(self, symbol: str) -> Optional[float]:
        """
        Fetch latest price for symbol.
        
        Args:
            symbol: Asset symbol (e.g., 'GLD', 'SPY')
        
        Returns:
            Latest price or None if failed
        """
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            
            if not data.empty:
                return float(data['Close'].iloc[-1])
            
            return None
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def fetch_latest_ohlc(
        self,
        symbol: str,
        interval: str = '1d',
        period: str = '5y'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC data with extensive historical support.
        
        Args:
            symbol: Asset symbol
            interval: Interval ('1d', '1h', '5m', etc.)
            period: Period of data to fetch
        
        Available periods:
        - Short-term: '1d', '5d', '1mo', '3mo', '6mo'
        - Medium-term: '1y', '2y', '5y' (default)
        - Long-term: '10y', '20y' (recommended for robust backtesting)
        - All history: 'max' (~21 years for GLD, varies by asset)
        
        Returns:
            DataFrame with OHLCV columns or None if failed
        
        Example:
            >>> feed = LiveDataFeed()
            >>> # Get 20 years of daily data
            >>> df = feed.fetch_latest_ohlc('GLD', period='20y')
            >>> # Get 5 years of hourly data
            >>> df = feed.fetch_latest_ohlc('SPY', interval='1h', period='5y')
        """
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if not data.empty:
                return data
            
            return None
            
        except Exception as e:
            print(f"Error fetching OHLC for {symbol}: {e}")
            return None
    
    def fetch_historical_range(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for specific date range.
        
        Args:
            symbol: Asset symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
        
        Returns:
            DataFrame with OHLCV or None
        
        Example:
            >>> feed = LiveDataFeed()
            >>> # Get data from 2004 to 2024
            >>> df = feed.fetch_historical_range('GLD', '2004-01-01', '2024-12-31')
        """
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if not data.empty:
                return data
            
            return None
            
        except Exception as e:
            print(f"Error fetching historical range for {symbol}: {e}")
            return None
    
    def fetch_batch(self, symbols: List[str]) -> Dict[str, float]:
        """
        Fetch prices for multiple symbols.
        
        Args:
            symbols: List of symbols
        
        Returns:
            Dictionary mapping symbol -> price
        """
        prices = {}
        
        for symbol in symbols:
            price = self.fetch_latest_price(symbol)
            if price:
                prices[symbol] = price
        
        return prices
    
    def get_data_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about available data for symbol.
        
        Args:
            symbol: Asset symbol
        
        Returns:
            Dictionary with data availability info
        """
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            
            # Fetch max available data to see date range
            data = ticker.history(period='max')
            
            if not data.empty:
                start_date = data.index[0]
                end_date = data.index[-1]
                total_days = len(data)
                years = total_days / 252  # Trading days per year
                
                return {
                    'symbol': symbol,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'total_days': total_days,
                    'years': round(years, 1),
                    'available': True
                }
            
            return {'symbol': symbol, 'available': False}
            
        except Exception as e:
            return {'symbol': symbol, 'available': False, 'error': str(e)}


def fetch_latest_price(symbol: str) -> Optional[float]:
    """
    Convenience function to fetch latest price.
    
    ⚠️  EDUCATIONAL ONLY - Uses free delayed data
    
    Args:
        symbol: Asset symbol
    
    Returns:
        Latest price or None
    """
    feed = LiveDataFeed()
    return feed.fetch_latest_price(symbol)
