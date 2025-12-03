"""
OpenBB Cache Layer for Meridian v2.1.2

Local JSON/Parquet caching with expiry logic.
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Any, Dict


class OpenBBCache:
    """
    Caching layer for OpenBB data.
    
    Supports:
    - Local JSON/Parquet storage
    - Expiry logic
    - Synthetic data hooks
    """
    
    def __init__(self, cache_path: str = "cache/openbb/", expiry_days: int = 1):
        """
        Initialize cache.
        
        Args:
            cache_path: Path to cache directory
            expiry_days: Days until cache expires
        """
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.expiry_days = expiry_days
    
    def get(self, key: str) -> Optional[pd.DataFrame]:
        """
        Get cached data.
        
        Args:
            key: Cache key
        
        Returns:
            DataFrame if found and not expired, None otherwise
        """
        cache_file = self.cache_path / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            # Load JSON with metadata
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check expiry
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(days=self.expiry_days):
                return None
            
            # Reconstruct DataFrame
            df = pd.DataFrame(cache_data['data'])
            
            # Check if first column looks like a date index
            if len(df.columns) > 0:
                first_col = df.columns[0]
                if first_col == 'index' or pd.api.types.is_string_dtype(df[first_col]):
                    try:
                        df.index = pd.to_datetime(df[first_col])
                        df = df.drop(columns=[first_col])
                    except:
                        pass
            
            return df
        except (json.JSONDecodeError, KeyError):
            # If cache is corrupted, return None
            return None
    
    def set(self, key: str, data: pd.DataFrame) -> None:
        """
        Save data to cache.
        
        Args:
            key: Cache key
            data: DataFrame to cache
        """
        cache_file = self.cache_path / f"{key}.json"
        
        # Prepare data for JSON (convert DataFrame to JSON-serializable format)
        df_reset = data.reset_index(drop=False)
        
        # Convert any datetime columns to ISO strings, replace NaN with None
        data_dict = {}
        for col in df_reset.columns:
            if pd.api.types.is_datetime64_any_dtype(df_reset[col]):
                data_dict[col] = df_reset[col].astype(str).tolist()
            else:
                # Replace NaN with None (JSON null)
                col_data = df_reset[col].where(pd.notnull(df_reset[col]), None).tolist()
                data_dict[col] = col_data
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'rows': len(data),
            'columns': list(data.columns),
            'data': data_dict
        }
        
        # Save to JSON
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache.
        
        Args:
            key: Specific key to clear, or None to clear all
        """
        if key:
            cache_file = self.cache_path / f"{key}.json"
            cache_file.unlink(missing_ok=True)
        else:
            for file in self.cache_path.glob("*"):
                file.unlink()


def get_cached_data(key: str, cache_path: str = "cache/openbb/") -> Optional[pd.DataFrame]:
    """
    Simple function to get cached data.
    
    Args:
        key: Cache key
        cache_path: Cache directory
    
    Returns:
        Cached DataFrame or None
    """
    cache = OpenBBCache(cache_path)
    return cache.get(key)


def save_cached_data(key: str, data: pd.DataFrame, cache_path: str = "cache/openbb/") -> None:
    """
    Simple function to save cached data.
    
    Args:
        key: Cache key
        data: DataFrame to cache
        cache_path: Cache directory
    """
    cache = OpenBBCache(cache_path)
    cache.set(key, data)

