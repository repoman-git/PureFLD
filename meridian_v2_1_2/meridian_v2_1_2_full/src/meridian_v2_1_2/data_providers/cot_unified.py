"""
Unified COT Data Provider

Intelligent fallback between multiple COT sources:
1. commitmentoftraders.org (FREE, no API key)
2. OpenBB (when API key available)
3. Synthetic (last resort)

Automatically selects best available source.
"""

import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime


class UnifiedCOTProvider:
    """
    Unified COT data provider with automatic fallback.
    
    Priority:
    1. commitmentoftraders.org (free, no key needed)
    2. OpenBB (if API key configured)
    3. Synthetic (fallback)
    """
    
    def __init__(self, prefer_free: bool = True):
        """
        Initialize unified COT provider.
        
        Args:
            prefer_free: Prefer free sources over paid APIs
        """
        self.prefer_free = prefer_free
        self.cot_org_available = True
        self.openbb_available = False
        
        # Try to initialize providers
        try:
            from .cot_org import COTOrgFetcher
            self.cot_org = COTOrgFetcher()
        except Exception as e:
            print(f"COT.org not available: {e}")
            self.cot_org_available = False
            self.cot_org = None
        
        try:
            from ..external.openbb_adapter import OpenBBAdapter
            self.openbb = OpenBBAdapter()
            self.openbb_available = self.openbb.is_enabled()
        except Exception as e:
            print(f"OpenBB not available: {e}")
            self.openbb_available = False
            self.openbb = None
    
    def fetch_cot_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: str = 'auto'
    ) -> pd.DataFrame:
        """
        Fetch COT data with intelligent source selection.
        
        Args:
            symbol: Trading symbol (e.g., 'GLD', 'SPY')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: 'auto', 'cot_org', 'openbb', or 'synthetic'
        
        Returns:
            DataFrame with COT data
        
        Automatic source selection:
        - If source='auto': Tries cot_org first, then openbb, then synthetic
        - If source specified: Uses that source only
        
        Example:
            >>> provider = UnifiedCOTProvider()
            >>> df = provider.fetch_cot_data('GLD', '2010-01-01', '2025-12-31')
            >>> print(f"Source used: {provider.last_source_used}")
        """
        self.last_source_used = None
        self.last_error = None
        
        if source == 'auto':
            # Try sources in priority order
            if self.prefer_free:
                sources_to_try = ['cot_org', 'openbb', 'synthetic']
            else:
                sources_to_try = ['openbb', 'cot_org', 'synthetic']
            
            for src in sources_to_try:
                try:
                    df = self._fetch_from_source(src, symbol, start_date, end_date)
                    if df is not None and not df.empty:
                        self.last_source_used = src
                        return df
                except Exception as e:
                    self.last_error = str(e)
                    continue
            
            # If all fail, fallback to synthetic
            return self._fetch_synthetic(symbol, start_date, end_date)
        
        else:
            # Use specified source
            return self._fetch_from_source(source, symbol, start_date, end_date)
    
    def _fetch_from_source(
        self,
        source: str,
        symbol: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """Fetch from specific source"""
        
        if source == 'cot_org':
            if not self.cot_org_available or self.cot_org is None:
                raise ValueError("COT.org not available")
            
            print(f"Fetching COT data from commitmentoftraders.org...")
            return self.cot_org.fetch_cot_data(symbol, start_date, end_date)
        
        elif source == 'openbb':
            if not self.openbb_available or self.openbb is None:
                raise ValueError("OpenBB not available")
            
            print(f"Fetching COT data from OpenBB...")
            return self.openbb.get_cot_data(symbol, start_date, end_date)
        
        elif source == 'synthetic':
            print(f"Generating synthetic COT data...")
            return self._fetch_synthetic(symbol, start_date, end_date)
        
        else:
            raise ValueError(f"Unknown source: {source}")
    
    def _fetch_synthetic(
        self,
        symbol: str,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> pd.DataFrame:
        """Generate synthetic COT data as last resort"""
        from ..synthetic.synth_cot import generate_synthetic_cot
        
        # Convert dates to date range
        if start_date is None:
            start_date = '2006-01-01'
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        dates = pd.date_range(start_date, end_date, freq='W-TUE')
        
        df = generate_synthetic_cot(
            length=len(dates),
            noise=0.2,
            trendiness=0.15,
            seed=hash(symbol) % (2**32)
        )
        
        # Trim to match date range
        df.index = dates[:len(df)]
        
        self.last_source_used = 'synthetic'
        
        return df
    
    def get_source_status(self) -> Dict[str, Any]:
        """
        Get status of all COT sources.
        
        Returns:
            Dictionary with source availability
        """
        status = {
            'cot_org': {
                'available': self.cot_org_available,
                'description': 'commitmentoftraders.org (FREE)',
                'requires_key': False,
                'priority': 1 if self.prefer_free else 2
            },
            'openbb': {
                'available': self.openbb_available,
                'description': 'OpenBB Platform',
                'requires_key': True,
                'priority': 2 if self.prefer_free else 1
            },
            'synthetic': {
                'available': True,
                'description': 'Synthetic fallback',
                'requires_key': False,
                'priority': 999
            }
        }
        
        return status
    
    def test_sources(self) -> Dict[str, Any]:
        """
        Test all COT sources.
        
        Returns:
            Dictionary with test results
        """
        results = {}
        
        # Test COT.org
        if self.cot_org_available:
            try:
                status = self.cot_org.test_connection()
                results['cot_org'] = {
                    'status': 'ok' if status['accessible'] else 'error',
                    'message': status['message']
                }
            except Exception as e:
                results['cot_org'] = {
                    'status': 'error',
                    'message': str(e)
                }
        else:
            results['cot_org'] = {
                'status': 'unavailable',
                'message': 'Module not loaded'
            }
        
        # Test OpenBB
        if self.openbb_available:
            try:
                status = self.openbb.test_connection()
                results['openbb'] = {
                    'status': 'ok' if status['connection_ok'] else 'error',
                    'message': status.get('error', 'Connection OK')
                }
            except Exception as e:
                results['openbb'] = {
                    'status': 'error',
                    'message': str(e)
                }
        else:
            results['openbb'] = {
                'status': 'unavailable',
                'message': 'No API key or module not loaded'
            }
        
        # Synthetic always works
        results['synthetic'] = {
            'status': 'ok',
            'message': 'Synthetic data always available'
        }
        
        return results


# Convenience function
def fetch_cot_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: str = 'auto',
    prefer_free: bool = True
) -> pd.DataFrame:
    """
    Fetch COT data with automatic source selection.
    
    Args:
        symbol: Trading symbol
        start_date: Start date
        end_date: End date
        source: 'auto', 'cot_org', 'openbb', or 'synthetic'
        prefer_free: Prefer free sources
    
    Returns:
        DataFrame with COT data
    
    Example:
        >>> from meridian_v2_1_2.data_providers import fetch_cot_data
        >>> df = fetch_cot_data('GLD', '2010-01-01', '2025-12-31')
        >>> print(df.head())
    """
    provider = UnifiedCOTProvider(prefer_free=prefer_free)
    return provider.fetch_cot_data(symbol, start_date, end_date, source)


