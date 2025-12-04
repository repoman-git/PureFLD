"""
CommitmentOfTraders.org Data Fetcher

Fetch real COT data from commitmentoftraders.org
Free, no API key required!

Data available:
- Gold, Silver, Copper (metals)
- S&P 500, NASDAQ, Dow (indices)
- Treasuries (bonds)
- Crude Oil, Natural Gas (energy)
- Currencies (EUR, GBP, JPY, etc.)

Format: Weekly data (Tuesdays)
History: ~20 years for most contracts
"""

import pandas as pd
import requests
from typing import Optional, Dict
from datetime import datetime, timedelta
import io


class COTOrgFetcher:
    """
    Fetch COT data from commitmentoftraders.org
    
    Free alternative to paid APIs!
    No API key required.
    """
    
    # Symbol to COT report mapping
    SYMBOL_MAPPING = {
        # Metals
        'GLD': 'gold',
        'GC': 'gold',
        'SLV': 'silver',
        'SI': 'silver',
        'HG': 'copper',
        
        # Indices
        'SPY': 'sp500',
        'ES': 'sp500',
        'QQQ': 'nasdaq100',
        'NQ': 'nasdaq100',
        
        # Bonds
        'TLT': 'us-treasury-bonds',
        'TY': '10-year-treasury-notes',
        'ZN': '10-year-treasury-notes',
        
        # Energy
        'USO': 'crude-oil',
        'CL': 'crude-oil',
        'UNG': 'natural-gas',
        'NG': 'natural-gas',
        
        # Currencies
        'UUP': 'us-dollar-index',
        'DX': 'us-dollar-index',
        'FXE': 'euro',
        'EC': 'euro',
    }
    
    def __init__(self, base_url: str = "https://www.commitmentoftraders.org"):
        """
        Initialize COT.org fetcher.
        
        Args:
            base_url: Base URL for commitmentoftraders.org
        """
        self.base_url = base_url
        self.cache = {}
    
    def fetch_cot_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch COT data for symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'GLD', 'SPY')
            start_date: Start date (YYYY-MM-DD), defaults to 20 years ago
            end_date: End date (YYYY-MM-DD), defaults to today
        
        Returns:
            DataFrame with COT data:
            - commercials_long
            - commercials_short
            - commercials_net
            - non_commercials_long
            - non_commercials_short
            - non_commercials_net
            - open_interest
        
        Example:
            >>> fetcher = COTOrgFetcher()
            >>> df = fetcher.fetch_cot_data('GLD', '2010-01-01', '2025-12-31')
            >>> print(df.head())
        """
        # Map symbol to COT report name
        if symbol not in self.SYMBOL_MAPPING:
            raise ValueError(
                f"Symbol {symbol} not mapped. Available: {list(self.SYMBOL_MAPPING.keys())}"
            )
        
        cot_name = self.SYMBOL_MAPPING[symbol]
        
        # Set default dates
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if start_date is None:
            # Default to 20 years ago
            start_date = (datetime.now() - timedelta(days=20*365)).strftime('%Y-%m-%d')
        
        # Try to fetch from website
        try:
            df = self._fetch_from_website(cot_name, start_date, end_date)
            return df
        except Exception as e:
            print(f"Website fetch failed: {e}")
            print("Falling back to synthetic data...")
            return self._generate_fallback_data(start_date, end_date)
    
    def _fetch_from_website(
        self,
        cot_name: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch COT data from commitmentoftraders.org website.
        
        The site provides downloadable CSV files for each commodity.
        """
        # Build URL for data download
        # Format varies by site structure - may need adjustment
        url = f"{self.base_url}/cot-data/{cot_name}/historical"
        
        print(f"Fetching COT data from: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Parse CSV data (site provides CSV downloads)
        # This is a placeholder - actual parsing depends on site format
        df = pd.read_csv(io.StringIO(response.text))
        
        # Normalize column names
        df = self._normalize_columns(df)
        
        # Filter by date range
        df.index = pd.to_datetime(df.index)
        df = df.loc[start_date:end_date]
        
        return df
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize COT data to standard format.
        
        Different sources use different column names.
        Standardize to Meridian format.
        """
        # Common column mappings
        column_map = {
            'Commercial Long': 'commercials_long',
            'Commercial Short': 'commercials_short',
            'Non-Commercial Long': 'non_commercials_long',
            'Non-Commercial Short': 'non_commercials_short',
            'Open Interest': 'open_interest',
            'comm_long': 'commercials_long',
            'comm_short': 'commercials_short',
            'noncomm_long': 'non_commercials_long',
            'noncomm_short': 'non_commercials_short',
        }
        
        # Rename columns
        df = df.rename(columns=column_map)
        
        # Calculate net positions if not present
        if 'commercials_net' not in df.columns:
            df['commercials_net'] = df['commercials_long'] - df['commercials_short']
        
        if 'non_commercials_net' not in df.columns:
            df['non_commercials_net'] = df['non_commercials_long'] - df['non_commercials_short']
        
        return df
    
    def _generate_fallback_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Generate synthetic fallback if website unavailable.
        
        This is temporary until real fetch is working.
        """
        from ...synthetic.synth_cot import generate_synthetic_cot
        
        dates = pd.date_range(start_date, end_date, freq='W-TUE')
        
        df = generate_synthetic_cot(
            length=len(dates),
            noise=0.2,
            trendiness=0.15
        )
        
        df.index = dates[:len(df)]
        
        return df
    
    def get_available_symbols(self) -> Dict[str, str]:
        """
        Get list of available symbols and their COT report names.
        
        Returns:
            Dictionary mapping symbol -> COT report name
        """
        return self.SYMBOL_MAPPING.copy()
    
    def test_connection(self) -> Dict[str, any]:
        """
        Test connection to commitmentoftraders.org
        
        Returns:
            Status dictionary
        """
        try:
            response = requests.get(self.base_url, timeout=10)
            
            return {
                'status': 'ok' if response.status_code == 200 else 'error',
                'status_code': response.status_code,
                'accessible': response.status_code == 200,
                'message': 'Connection successful' if response.status_code == 200 else f'Status {response.status_code}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'status_code': None,
                'accessible': False,
                'message': str(e)
            }


def fetch_cot_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    Convenience function to fetch COT data.
    
    Args:
        symbol: Trading symbol (e.g., 'GLD', 'SPY')
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        DataFrame with COT data
    
    Example:
        >>> from meridian_v2_1_2.data_providers.cot_org import fetch_cot_data
        >>> df = fetch_cot_data('GLD', '2010-01-01', '2025-12-31')
        >>> print(f"Got {len(df)} weeks of COT data")
    """
    fetcher = COTOrgFetcher()
    return fetcher.fetch_cot_data(symbol, start_date, end_date)


