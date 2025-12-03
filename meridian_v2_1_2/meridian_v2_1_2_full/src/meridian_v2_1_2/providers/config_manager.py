"""
Provider Configuration Manager

Load, save, and validate market data provider configurations.
Handles API keys, priorities, and provider settings.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
import shutil
from datetime import datetime


CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "data" / "providers_config.json"


def get_default_provider_config() -> Dict[str, Any]:
    """
    Get default provider configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        'providers': {
            'tiingo': {
                'enabled': False,
                'api_key': '',
                'priority': 1,
                'description': 'Tiingo - High-quality financial data',
                'supported_assets': ['stocks', 'etfs', 'crypto'],
                'rate_limit': 1000  # requests per hour
            },
            'openbb': {
                'enabled': False,
                'api_key': '',
                'priority': 2,
                'description': 'OpenBB - Open-source financial data platform',
                'supported_assets': ['stocks', 'etfs', 'crypto', 'forex', 'futures'],
                'rate_limit': 5000
            },
            'alpaca': {
                'enabled': False,
                'api_key': '',
                'api_secret': '',
                'paper_trading': True,
                'priority': 3,
                'description': 'Alpaca - Commission-free trading API',
                'supported_assets': ['stocks', 'crypto'],
                'rate_limit': 200
            },
            'yahoo_finance': {
                'enabled': True,
                'api_key': '',  # Free, no key needed
                'priority': 4,
                'description': 'Yahoo Finance - Free delayed data',
                'supported_assets': ['stocks', 'etfs', 'indices'],
                'rate_limit': 2000
            },
            'cftc': {
                'enabled': True,
                'api_key': '',  # Free, no key needed
                'priority': 5,
                'description': 'CFTC - Commitment of Traders reports',
                'supported_assets': ['futures', 'commodities'],
                'rate_limit': 100
            },
            'quandl': {
                'enabled': False,
                'api_key': '',
                'priority': 6,
                'description': 'Quandl/Nasdaq Data Link',
                'supported_assets': ['all'],
                'rate_limit': 300
            }
        },
        'settings': {
            'default_provider': 'yahoo_finance',
            'fallback_enabled': True,
            'cache_duration_hours': 24,
            'auto_update': True,
            'update_frequency': 'daily'
        },
        'last_updated': datetime.now().isoformat()
    }


def load_provider_config() -> Dict[str, Any]:
    """
    Load provider configuration from disk.
    
    Returns:
        Configuration dictionary (creates default if doesn't exist)
    """
    try:
        if not CONFIG_PATH.exists():
            # Create default config
            default_config = get_default_provider_config()
            save_provider_config(default_config)
            return default_config
        
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        return config
        
    except Exception as e:
        print(f"Error loading provider config: {e}")
        return get_default_provider_config()


def save_provider_config(config: Dict[str, Any]) -> bool:
    """
    Save provider configuration to disk (atomic write).
    
    Args:
        config: Configuration dictionary
    
    Returns:
        True if successful
    """
    try:
        # Ensure directory exists
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file
        if CONFIG_PATH.exists():
            backup_path = CONFIG_PATH.with_suffix('.json.backup')
            shutil.copy(CONFIG_PATH, backup_path)
        
        # Atomic write: write to temp, then rename
        temp_path = CONFIG_PATH.with_suffix('.json.tmp')
        
        # Update timestamp
        config['last_updated'] = datetime.now().isoformat()
        
        with open(temp_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Atomic rename
        temp_path.replace(CONFIG_PATH)
        
        return True
        
    except Exception as e:
        print(f"Error saving provider config: {e}")
        return False


def validate_provider_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate provider configuration.
    
    Args:
        config: Configuration to validate
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if 'providers' not in config:
        errors.append("Missing 'providers' section")
    
    if 'settings' not in config:
        errors.append("Missing 'settings' section")
    
    # Validate each provider
    if 'providers' in config:
        for provider_name, provider_config in config['providers'].items():
            if 'enabled' not in provider_config:
                errors.append(f"{provider_name}: Missing 'enabled' field")
            
            if 'priority' not in provider_config:
                errors.append(f"{provider_name}: Missing 'priority' field")
    
    return len(errors) == 0, errors


def update_provider_api_key(provider_name: str, api_key: str) -> bool:
    """
    Update API key for specific provider.
    
    Args:
        provider_name: Name of provider
        api_key: New API key
    
    Returns:
        True if successful
    """
    config = load_provider_config()
    
    if provider_name not in config['providers']:
        return False
    
    config['providers'][provider_name]['api_key'] = api_key
    
    return save_provider_config(config)


def get_enabled_providers() -> List[str]:
    """Get list of currently enabled providers"""
    config = load_provider_config()
    
    enabled = []
    for provider_name, provider_config in config['providers'].items():
        if provider_config.get('enabled', False):
            enabled.append(provider_name)
    
    # Sort by priority
    enabled.sort(key=lambda p: config['providers'][p].get('priority', 999))
    
    return enabled

