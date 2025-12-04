"""
Environment Variable Loader for Meridian v2.1.2

Secure offline key loading with masking.
NO validation - just loads from .env if present.
"""

import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv


# Expected keys (not required, just tracked)
EXPECTED_KEYS = [
    'OPENBB_API_KEY',
    'ALPACA_API_KEY',
    'ALPACA_SECRET_KEY',
    'FRED_API_KEY',
    'NASDAQ_API_KEY',
]


class EnvLoader:
    """
    Secure environment variable loader.
    
    Features:
    - Loads from .env file if present
    - Never prints or logs keys
    - Provides masked versions for debug
    - Optional - works fine with no keys
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize loader.
        
        Args:
            env_file: Path to .env file (default: .env in workspace root)
        """
        self.env_file = env_file
        self._keys = None
    
    def load(self) -> Dict[str, Optional[str]]:
        """
        Load environment variables.
        
        Returns:
            Dict of key names to values (None if not set)
        """
        # Load .env file if it exists
        if self.env_file:
            env_path = Path(self.env_file)
        else:
            env_path = Path('.env')
        
        if env_path.exists():
            load_dotenv(env_path)
        
        # Load expected keys
        keys = {}
        for key in EXPECTED_KEYS:
            value = os.getenv(key)
            keys[key] = value if value else None
        
        self._keys = keys
        return keys
    
    def masked(self, keys: Optional[Dict[str, Optional[str]]] = None) -> Dict[str, str]:
        """
        Get masked version of keys for safe display.
        
        Args:
            keys: Keys dict (uses cached if None)
        
        Returns:
            Dict with masked values
        """
        if keys is None:
            if self._keys is None:
                self.load()
            keys = self._keys
        
        masked = {}
        for key, value in keys.items():
            if value:
                # Show first 4 chars + ****
                if len(value) > 4:
                    masked[key] = value[:4] + '****'
                else:
                    masked[key] = '****'
            else:
                masked[key] = None
        
        return masked
    
    def get(self, key: str) -> Optional[str]:
        """Get specific key value"""
        if self._keys is None:
            self.load()
        return self._keys.get(key)
    
    def has_key(self, key: str) -> bool:
        """Check if key is set"""
        value = self.get(key)
        return value is not None and len(value) > 0


def load_env_keys(env_file: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Convenience function to load env keys.
    
    Args:
        env_file: Path to .env file
    
    Returns:
        Dict of keys
    """
    loader = EnvLoader(env_file)
    return loader.load()


def mask_keys(keys: Dict[str, Optional[str]]) -> Dict[str, str]:
    """
    Convenience function to mask keys.
    
    Args:
        keys: Keys dict
    
    Returns:
        Masked keys dict
    """
    loader = EnvLoader()
    return loader.masked(keys)


