"""
ETF Data Loader

Load OHLCV data for ETFs from configured providers.
Provider priority: Tiingo → OpenBB → Yahoo Finance (fallback).
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from .config_manager import load_provider_config, get_enabled_providers


class ETFDataLoader:
    """
    ETF data loader with automatic provider routing.
    
    Tries providers in priority order until successful.
    """
    
    def __init__(self):
        """Initialize with provider configuration"""
        self.config = load_provider_config()
        self.enabled_providers = get_enabled_providers()
    
    def load_etf(
        self,
        symbol: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
        provider: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load OHLCV data for an ETF.
        
        Provider priority:
        1. Tiingo (if API key present)
        2. OpenBB (if configured)
        3. Yahoo Finance (free fallback)
        
        Args:
            symbol: ETF ticker (e.g., 'GLD', 'SLV', 'SPY', 'TLT')
            start: Start date (YYYY-MM-DD), defaults to 3 years ago
            end: End date (YYYY-MM-DD), defaults to today
            provider: Force specific provider (optional)
        
        Returns:
            DataFrame with columns: ['open', 'high', 'low', 'close', 'volume']
        
        Example:
            >>> loader = ETFDataLoader()
            >>> df = loader.load_etf('GLD', start='2020-01-01', end='2023-12-31')
            >>> print(df.head())
        
        Raises:
            RuntimeError: If all providers fail
        """
        
        # Set default dates
        if end is None:
            end = datetime.now().strftime('%Y-%m-%d')
        if start is None:
            start = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
        
        # Clean symbol
        symbol = symbol.upper().strip()
        
        print(f"Loading ETF: {symbol} ({start} to {end})")
        
        # If specific provider requested
        if provider:
            return self._load_from_provider(provider, symbol, start, end)
        
        # Try providers in priority order
        fallback_enabled = self.config.get('settings', {}).get('fallback_enabled', True)
        
        errors = []
        
        for provider_name in self.enabled_providers:
            try:
                print(f"  Trying {provider_name}...")
                df = self._load_from_provider(provider_name, symbol, start, end)
                
                if df is not None and len(df) > 0:
                    print(f"  ✅ Success with {provider_name}")
                    return df
                
            except Exception as e:
                errors.append(f"{provider_name}: {str(e)}")
                print(f"  ❌ {provider_name} failed: {e}")
                
                if not fallback_enabled:
                    break
        
        # All providers failed
        raise RuntimeError(
            f"Failed to load ETF {symbol} from all providers.\n"
            + "\n".join(errors)
        )
    
    def _load_from_provider(
        self,
        provider_name: str,
        symbol: str,
        start: str,
        end: str
    ) -> Optional[pd.DataFrame]:
        """Load from specific provider"""
        
        if provider_name == 'yahoo_finance':
            return self._load_yahoo(symbol, start, end)
        
        elif provider_name == 'tiingo':
            return self._load_tiingo(symbol, start, end)
        
        elif provider_name == 'openbb':
            return self._load_openbb(symbol, start, end)
        
        elif provider_name == 'alpaca':
            return self._load_alpaca(symbol, start, end)
        
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def _load_yahoo(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Load from Yahoo Finance"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start, end=end)
            
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")
            
            # Standardize column names
            df = df.rename(columns={
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Keep only required columns
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            return df
            
        except ImportError:
            raise RuntimeError("yfinance not installed. Install with: pip install yfinance")
    
    def _load_tiingo(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Load from Tiingo (requires API key)"""
        
        api_key = self.config['providers']['tiingo'].get('api_key', '')
        
        if not api_key:
            raise ValueError("Tiingo API key not configured")
        
        # Placeholder for actual Tiingo API call (Phase 8)
        raise NotImplementedError("Tiingo integration pending Phase 8")
    
    def _load_openbb(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Load from OpenBB"""
        
        # Placeholder for actual OpenBB integration (Phase 8)
        raise NotImplementedError("OpenBB integration pending Phase 8")
    
    def _load_alpaca(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """Load from Alpaca"""
        
        # Placeholder for actual Alpaca integration (Phase 8)
        raise NotImplementedError("Alpaca integration pending Phase 8")


# Convenience function
def load_etf(symbol: str, start: str = None, end: str = None, provider: str = None) -> pd.DataFrame:
    """
    Convenience function to load ETF data.
    
    Args:
        symbol: ETF ticker
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        provider: Force specific provider (optional)
    
    Returns:
        DataFrame with OHLCV data
    
    Example:
        >>> df = load_etf('GLD', start='2020-01-01')
        >>> print(df.tail())
    """
    loader = ETFDataLoader()
    return loader.load_etf(symbol, start, end, provider)


# Popular ETF lists for UI
POPULAR_ETFS = {
    'gold': ['GLD', 'IAU', 'SGOL', 'GDX', 'GDXJ'],
    'silver': ['SLV', 'SIVR'],
    'bonds': ['TLT', 'IEF', 'SHY', 'AGG', 'BND', 'LQD'],
    'equity': ['SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI'],
    'sectors': ['XLF', 'XLE', 'XLK', 'XLV', 'XLI', 'XLU', 'XLP'],
    'forex': ['UUP', 'FXE', 'FXY', 'FXB'],
    'volatility': ['VXX', 'VIXY'],
    'commodities': ['USO', 'UNG', 'DBA', 'DBC'],
    'leveraged': ['TQQQ', 'SQQQ', 'UPRO', 'SPXU', 'TZA', 'SOXL']
}


def get_etf_category(symbol: str) -> str:
    """Get category for ETF symbol"""
    symbol = symbol.upper()
    
    for category, symbols in POPULAR_ETFS.items():
        if symbol in symbols:
            return category
    
    return 'other'


def is_leveraged_etf(symbol: str) -> bool:
    """Check if ETF is leveraged (3x, inverse, etc.)"""
    symbol = symbol.upper()
    return symbol in POPULAR_ETFS['leveraged']


