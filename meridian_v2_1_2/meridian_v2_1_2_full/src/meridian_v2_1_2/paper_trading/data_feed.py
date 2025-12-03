"""
Live Data Feed

Pull real-time price data for paper trading simulation.
Uses free-tier providers (Yahoo Finance primary).
"""

from typing import Dict, Any, Optional, List
import pandas as pd
from datetime import datetime, timedelta


class LiveDataFeed:
    """
    Live data feed for paper trading.
    
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
        period: str = '2y'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC data.
        
        Args:
            symbol: Asset symbol
            interval: Interval ('1d', '1h', '5m', etc.)
            period: Period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max')
                   Default: '2y' (2 years of data for proper analysis)
        
        Returns:
            DataFrame with OHLCV or None
        
        Available periods:
        - '1d', '5d', '1mo', '3mo', '6mo' - Short-term
        - '1y', '2y', '5y' - Medium-term (recommended for strategies)
        - '10y', 'max' - Long-term (max = all available, ~21 years for GLD)
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

