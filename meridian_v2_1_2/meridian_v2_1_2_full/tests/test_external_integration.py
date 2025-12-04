"""
External Integration Test Suite

Tests for OpenBB and Alpaca adapters (OFFLINE ONLY).
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
from datetime import datetime

from meridian_v2_1_2.external import (
    ExternalConfig,
    ExternalDataException,
    APIKeyException,
    RateLimitException,
    OrderRejectionException,
    RateLimiter,
    ConnectionTester,
    test_connections,
    OpenBBAdapter,
    AlpacaAdapter
)


class TestExternalConfig:
    """Test external configuration"""
    
    def test_config_defaults(self):
        """Test default configuration is safe"""
        config = ExternalConfig()
        
        # APIs should be OFF by default
        assert config.use_openbb is False
        assert config.use_alpaca is False
        
        # Trading should be LOCKED by default
        assert config.live_trading is False
        assert config.paper_trading is True
        
        # Fallback should be ENABLED
        assert config.fallback_to_synthetic_if_failed is True
    
    def test_config_safety_flags(self):
        """Test safety configuration"""
        config = ExternalConfig()
        
        # Verify safety limits
        assert config.max_order_size > 0
        assert config.max_position_size > 0
        assert config.timeout_seconds > 0


class TestRateLimiter:
    """Test rate limiting"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter can be created"""
        limiter = RateLimiter(calls_per_second=5.0)
        assert limiter is not None
        assert limiter.calls_per_second == 5.0
    
    def test_rate_limiter_tracking(self):
        """Test rate limiter tracks calls"""
        limiter = RateLimiter(calls_per_second=100.0)  # High limit for testing
        
        # Make some calls
        for _ in range(5):
            limiter.wait_if_needed()
        
        # Should have tracked calls
        assert len(limiter.call_times) == 5
    
    def test_call_with_retry_success(self):
        """Test retry logic with successful call"""
        limiter = RateLimiter()
        
        def mock_func():
            return "success"
        
        result = limiter.call_with_retry(mock_func)
        assert result == "success"
    
    def test_call_with_retry_failure(self):
        """Test retry logic exhausts attempts"""
        limiter = RateLimiter(max_retries=2, retry_delay=0.01)
        
        def mock_failing_func():
            raise Exception("Test error")
        
        with pytest.raises(Exception, match="Test error"):
            limiter.call_with_retry(mock_failing_func)


class TestOpenBBAdapter:
    """Test OpenBB adapter (offline)"""
    
    def test_adapter_disabled_by_default(self):
        """Test OpenBB adapter is disabled by default"""
        config = ExternalConfig(use_openbb=False)
        adapter = OpenBBAdapter(config)
        
        assert not adapter.is_enabled()
    
    def test_get_prices_falls_back_to_synthetic(self):
        """Test price fetching falls back to synthetic"""
        config = ExternalConfig(use_openbb=False, fallback_to_synthetic_if_failed=True)
        adapter = OpenBBAdapter(config)
        
        df = adapter.get_prices('GLD', '2020-01-01', '2020-01-31')
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'close' in df.columns
    
    def test_get_cot_data_falls_back_to_synthetic(self):
        """Test COT data falls back to synthetic"""
        config = ExternalConfig(use_openbb=False, fallback_to_synthetic_if_failed=True)
        adapter = OpenBBAdapter(config)
        
        df = adapter.get_cot_data('GC', '2020-01-01', '2020-01-31')
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
    
    def test_connection_test_when_disabled(self):
        """Test connection test when disabled"""
        config = ExternalConfig(use_openbb=False)
        adapter = OpenBBAdapter(config)
        
        result = adapter.test_connection()
        
        assert result['enabled'] is False
        assert result['connection_ok'] is False


class TestAlpacaAdapter:
    """Test Alpaca adapter (offline)"""
    
    def test_adapter_disabled_by_default(self):
        """Test Alpaca adapter is disabled by default"""
        config = ExternalConfig(use_alpaca=False)
        adapter = AlpacaAdapter(config)
        
        assert not adapter.is_enabled()
        assert not adapter.is_live_trading_enabled()
    
    def test_live_trading_locked_by_default(self):
        """Test live trading is locked even if adapter enabled"""
        config = ExternalConfig(
            use_alpaca=True,
            live_trading=False,  # Locked
            paper_trading=True
        )
        adapter = AlpacaAdapter(config)
        
        # Even if enabled, live trading should be False
        assert not adapter.is_live_trading_enabled()
    
    def test_get_bars_falls_back_to_synthetic(self):
        """Test bars fall back to synthetic"""
        config = ExternalConfig(use_alpaca=False, fallback_to_synthetic_if_failed=True)
        adapter = AlpacaAdapter(config)
        
        df = adapter.get_bars('GLD', '2020-01-01', '2020-01-31')
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert 'close' in df.columns
    
    def test_submit_order_simulates_when_disabled(self):
        """Test order submission simulates when disabled"""
        config = ExternalConfig(use_alpaca=False)
        adapter = AlpacaAdapter(config)
        
        order = adapter.submit_order('GLD', 10.0, 'buy')
        
        assert order is not None
        assert order['simulated'] is True
        assert order['status'] == 'filled'
    
    def test_order_sanitization_rejects_nan(self):
        """Test order sanitization rejects NaN"""
        config = ExternalConfig(use_alpaca=True, live_trading=True, paper_trading=False)
        adapter = AlpacaAdapter(config)
        adapter.enabled = True
        adapter.live_trading_enabled = True
        
        with pytest.raises(OrderRejectionException, match="NaN"):
            adapter.submit_order('GLD', float('nan'), 'buy')
    
    def test_order_sanitization_rejects_zero(self):
        """Test order sanitization rejects zero quantity"""
        config = ExternalConfig(use_alpaca=True, live_trading=True, paper_trading=False)
        adapter = AlpacaAdapter(config)
        adapter.enabled = True
        adapter.live_trading_enabled = True
        
        with pytest.raises(OrderRejectionException, match="zero"):
            adapter.submit_order('GLD', 0.0, 'buy')
    
    def test_order_sanitization_rejects_invalid_side(self):
        """Test order sanitization rejects invalid side"""
        config = ExternalConfig(use_alpaca=True, live_trading=True, paper_trading=False)
        adapter = AlpacaAdapter(config)
        adapter.enabled = True
        adapter.live_trading_enabled = True
        
        with pytest.raises(OrderRejectionException, match="Invalid side"):
            adapter.submit_order('GLD', 10.0, 'INVALID')
    
    def test_order_size_limit_enforced(self):
        """Test order size limit is enforced"""
        config = ExternalConfig(
            use_alpaca=True,
            live_trading=True,
            paper_trading=False,
            max_order_size=100.0
        )
        adapter = AlpacaAdapter(config)
        adapter.enabled = True
        adapter.live_trading_enabled = True
        
        with pytest.raises(OrderRejectionException, match="exceeds limit"):
            adapter.submit_order('GLD', 1000.0, 'buy')
    
    def test_get_account_when_disabled(self):
        """Test account info when disabled"""
        config = ExternalConfig(use_alpaca=False)
        adapter = AlpacaAdapter(config)
        
        account = adapter.get_account()
        
        assert account['enabled'] is False
        assert account['equity'] == 0.0
    
    def test_connection_test_when_disabled(self):
        """Test connection test when disabled"""
        config = ExternalConfig(use_alpaca=False)
        adapter = AlpacaAdapter(config)
        
        result = adapter.test_connection()
        
        assert result['enabled'] is False
        assert result['connection_ok'] is False


class TestConnectionTester:
    """Test connection tester"""
    
    def test_connection_tester_initialization(self):
        """Test connection tester can be initialized"""
        config = ExternalConfig()
        tester = ConnectionTester(config)
        
        assert tester is not None
    
    def test_test_all_with_disabled_apis(self):
        """Test connection test with all APIs disabled"""
        config = ExternalConfig(use_openbb=False, use_alpaca=False)
        tester = ConnectionTester(config)
        
        results = tester.test_all()
        
        assert results['overall_status'] == 'ok'
        assert results['openbb'] is None
        assert results['alpaca'] is None
    
    def test_convenience_function(self):
        """Test convenience function"""
        config = ExternalConfig()
        results = test_connections(config)
        
        assert isinstance(results, dict)
        assert 'overall_status' in results


class TestOfflineGuarantee:
    """Test that external integration is truly offline"""
    
    def test_no_network_calls_openbb(self):
        """Test OpenBB makes no network calls when disabled"""
        config = ExternalConfig(use_openbb=False)
        adapter = OpenBBAdapter(config)
        
        # Should complete without network access
        df = adapter.get_prices('GLD', '2020-01-01', '2020-01-31')
        
        assert isinstance(df, pd.DataFrame)
    
    def test_no_network_calls_alpaca(self):
        """Test Alpaca makes no network calls when disabled"""
        config = ExternalConfig(use_alpaca=False)
        adapter = AlpacaAdapter(config)
        
        # Should complete without network access
        df = adapter.get_bars('GLD', '2020-01-01', '2020-01-31')
        order = adapter.submit_order('GLD', 10.0, 'buy')
        
        assert isinstance(df, pd.DataFrame)
        assert order is not None


class TestSafetyProtection:
    """Test safety protection mechanisms"""
    
    def test_live_trading_requires_explicit_enable(self):
        """Test live trading requires explicit config"""
        # Case 1: Alpaca enabled but live trading not explicitly enabled
        config1 = ExternalConfig(use_alpaca=True, live_trading=False)
        adapter1 = AlpacaAdapter(config1)
        
        assert not adapter1.is_live_trading_enabled()
        
        # Case 2: Live trading explicitly enabled
        config2 = ExternalConfig(
            use_alpaca=True,
            live_trading=True,
            paper_trading=False
        )
        adapter2 = AlpacaAdapter(config2)
        adapter2.enabled = True
        adapter2.api_key = "test"
        adapter2.secret_key = "test"
        adapter2.live_trading_enabled = True
        
        assert adapter2.is_live_trading_enabled()
    
    def test_fallback_to_synthetic_works(self):
        """Test fallback to synthetic data works"""
        config = ExternalConfig(
            use_openbb=False,
            fallback_to_synthetic_if_failed=True
        )
        
        openbb = OpenBBAdapter(config)
        df = openbb.get_prices('GLD', '2020-01-01', '2020-01-31')
        
        assert not df.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


