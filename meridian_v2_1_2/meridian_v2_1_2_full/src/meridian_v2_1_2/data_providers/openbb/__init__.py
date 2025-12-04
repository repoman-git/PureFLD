"""
OpenBB Data Integration for Meridian v2.1.2

Phase 22: Offline-first architecture with synthetic data fallbacks.
No external API calls yet - full scaffolding only.
"""

from .openbb_connector import OpenBBConnector
from .openbb_cache import OpenBBCache, get_cached_data, save_cached_data
from .data_loader_prices import load_prices, generate_synthetic_prices
from .data_loader_cot import load_cot_data, generate_synthetic_cot
from .data_loader_macro import load_macro_data, generate_synthetic_macro
from .data_loader_yields import load_real_yields, generate_synthetic_yields

__all__ = [
    'OpenBBConnector',
    'OpenBBCache',
    'get_cached_data',
    'save_cached_data',
    'load_prices',
    'generate_synthetic_prices',
    'load_cot_data',
    'generate_synthetic_cot',
    'load_macro_data',
    'generate_synthetic_macro',
    'load_real_yields',
    'generate_synthetic_yields',
]


