"""
External Data & Execution Integration Layer for Meridian v2.1.2

Safe API adapters with offline fallback.
"""

from .external_config import ExternalConfig
from .external_exceptions import (
    ExternalDataException,
    APIKeyException,
    RateLimitException,
    ConnectionException,
    OrderRejectionException
)
from .rate_limits import RateLimiter
from .connection_tester import ConnectionTester, test_connections
from .openbb_adapter import OpenBBAdapter
from .alpaca_adapter import AlpacaAdapter

__all__ = [
    'ExternalConfig',
    'ExternalDataException',
    'APIKeyException',
    'RateLimitException',
    'ConnectionException',
    'OrderRejectionException',
    'RateLimiter',
    'ConnectionTester',
    'test_connections',
    'OpenBBAdapter',
    'AlpacaAdapter',
]

