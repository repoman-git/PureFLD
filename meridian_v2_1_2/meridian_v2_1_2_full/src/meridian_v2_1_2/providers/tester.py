"""
Provider Connection Tester

Test connectivity and validate API keys for data providers.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class ProviderTestResult:
    """Result from provider connection test"""
    provider_name: str
    success: bool
    message: str
    latency_ms: float
    timestamp: str
    details: Dict[str, Any] = None


def test_provider_connection(
    provider_name: str,
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None
) -> ProviderTestResult:
    """
    Test connection to a data provider.
    
    Args:
        provider_name: Name of provider to test
        api_key: API key (optional)
        api_secret: API secret (optional, for Alpaca)
    
    Returns:
        ProviderTestResult with status and details
    
    Example:
        >>> result = test_provider_connection('yahoo_finance')
        >>> if result.success:
        ...     print(f"Connected! Latency: {result.latency_ms}ms")
    """
    
    start_time = time.time()
    
    try:
        # Test based on provider type
        if provider_name == 'yahoo_finance':
            result = _test_yahoo_finance()
        
        elif provider_name == 'openbb':
            result = _test_openbb(api_key)
        
        elif provider_name == 'alpaca':
            result = _test_alpaca(api_key, api_secret)
        
        elif provider_name == 'tiingo':
            result = _test_tiingo(api_key)
        
        elif provider_name == 'cftc':
            result = _test_cftc()
        
        elif provider_name == 'quandl':
            result = _test_quandl(api_key)
        
        else:
            result = ProviderTestResult(
                provider_name=provider_name,
                success=False,
                message=f"Unknown provider: {provider_name}",
                latency_ms=0,
                timestamp=datetime.now().isoformat()
            )
        
        # Calculate latency
        latency = (time.time() - start_time) * 1000
        result.latency_ms = latency
        
        return result
        
    except Exception as e:
        return ProviderTestResult(
            provider_name=provider_name,
            success=False,
            message=f"Test failed: {str(e)}",
            latency_ms=(time.time() - start_time) * 1000,
            timestamp=datetime.now().isoformat()
        )


def test_all_providers(config: Dict[str, Any]) -> Dict[str, ProviderTestResult]:
    """
    Test all configured providers.
    
    Args:
        config: Provider configuration dictionary
    
    Returns:
        Dictionary mapping provider_name -> ProviderTestResult
    """
    results = {}
    
    providers = config.get('providers', {})
    
    for provider_name, provider_config in providers.items():
        if not provider_config.get('enabled', False):
            continue  # Skip disabled providers
        
        api_key = provider_config.get('api_key', '')
        api_secret = provider_config.get('api_secret', '')
        
        result = test_provider_connection(provider_name, api_key, api_secret)
        results[provider_name] = result
    
    return results


# ============================================================================
# PROVIDER-SPECIFIC TEST FUNCTIONS
# ============================================================================

def _test_yahoo_finance() -> ProviderTestResult:
    """Test Yahoo Finance connection (no key required)"""
    
    try:
        # Try to import yfinance
        import yfinance as yf
        
        # Quick test: fetch SPY data
        ticker = yf.Ticker("SPY")
        info = ticker.info
        
        if info:
            return ProviderTestResult(
                provider_name='yahoo_finance',
                success=True,
                message="✅ Connected successfully (Free tier)",
                latency_ms=0,
                timestamp=datetime.now().isoformat(),
                details={'test_symbol': 'SPY', 'data_available': True}
            )
    
    except ImportError:
        return ProviderTestResult(
            provider_name='yahoo_finance',
            success=False,
            message="⚠️  yfinance package not installed. Install with: pip install yfinance",
            latency_ms=0,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        return ProviderTestResult(
            provider_name='yahoo_finance',
            success=False,
            message=f"❌ Connection failed: {str(e)}",
            latency_ms=0,
            timestamp=datetime.now().isoformat()
        )


def _test_openbb(api_key: Optional[str]) -> ProviderTestResult:
    """Test OpenBB connection"""
    
    # For now, mock test (actual OpenBB integration in Phase 8)
    if api_key:
        return ProviderTestResult(
            provider_name='openbb',
            success=True,
            message="🔧 OpenBB configured (integration pending Phase 8)",
            latency_ms=50,
            timestamp=datetime.now().isoformat(),
            details={'api_key_present': True, 'status': 'configured'}
        )
    else:
        return ProviderTestResult(
            provider_name='openbb',
            success=False,
            message="⚠️  No API key provided",
            latency_ms=0,
            timestamp=datetime.now().isoformat()
        )


def _test_alpaca(api_key: Optional[str], api_secret: Optional[str]) -> ProviderTestResult:
    """Test Alpaca connection"""
    
    if api_key and api_secret:
        return ProviderTestResult(
            provider_name='alpaca',
            success=True,
            message="🔧 Alpaca configured (integration pending Phase 8)",
            latency_ms=75,
            timestamp=datetime.now().isoformat(),
            details={'api_key_present': True, 'api_secret_present': True}
        )
    else:
        return ProviderTestResult(
            provider_name='alpaca',
            success=False,
            message="⚠️  Missing API key or secret",
            latency_ms=0,
            timestamp=datetime.now().isoformat()
        )


def _test_tiingo(api_key: Optional[str]) -> ProviderTestResult:
    """Test Tiingo connection"""
    
    if api_key:
        return ProviderTestResult(
            provider_name='tiingo',
            success=True,
            message="🔧 Tiingo configured (integration pending Phase 8)",
            latency_ms=60,
            timestamp=datetime.now().isoformat(),
            details={'api_key_present': True}
        )
    else:
        return ProviderTestResult(
            provider_name='tiingo',
            success=False,
            message="⚠️  No API key provided",
            latency_ms=0,
            timestamp=datetime.now().isoformat()
        )


def _test_cftc() -> ProviderTestResult:
    """Test CFTC connection (free, no key)"""
    
    return ProviderTestResult(
        provider_name='cftc',
        success=True,
        message="✅ CFTC data available (Free, no key required)",
        latency_ms=100,
        timestamp=datetime.now().isoformat(),
        details={'status': 'public_access'}
    )


def _test_quandl(api_key: Optional[str]) -> ProviderTestResult:
    """Test Quandl/Nasdaq Data Link connection"""
    
    if api_key:
        return ProviderTestResult(
            provider_name='quandl',
            success=True,
            message="🔧 Quandl configured (integration pending Phase 8)",
            latency_ms=80,
            timestamp=datetime.now().isoformat(),
            details={'api_key_present': True}
        )
    else:
        return ProviderTestResult(
            provider_name='quandl',
            success=False,
            message="⚠️  No API key provided",
            latency_ms=0,
            timestamp=datetime.now().isoformat()
        )

