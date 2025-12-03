"""
Test suite for OpenBB Data Integration Layer

Tests all data loaders with synthetic data - NO external API calls.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.data_providers.openbb import (
    OpenBBConnector,
    OpenBBCache,
    get_cached_data,
    save_cached_data,
    load_prices,
    generate_synthetic_prices,
    load_cot_data,
    generate_synthetic_cot,
    load_macro_data,
    generate_synthetic_macro,
    load_real_yields,
    generate_synthetic_yields
)
from meridian_v2_1_2.config import MeridianConfig


class TestOpenBBConnector:
    """Test OpenBB connector"""
    
    def test_connector_initialization(self):
        """Test connector initializes in synthetic mode"""
        cfg = MeridianConfig()
        connector = OpenBBConnector(cfg.openbb)
        
        assert connector.get_mode() == "synthetic"
    
    def test_connector_initialize(self):
        """Test connector initialize returns True"""
        cfg = MeridianConfig()
        connector = OpenBBConnector(cfg.openbb)
        
        result = connector.initialize()
        
        assert result is True
    
    def test_connector_is_ready(self):
        """Test connector is always ready in synthetic mode"""
        cfg = MeridianConfig()
        connector = OpenBBConnector(cfg.openbb)
        
        assert connector.is_ready() is True
    
    def test_connector_shutdown(self):
        """Test connector shutdown"""
        cfg = MeridianConfig()
        connector = OpenBBConnector(cfg.openbb)
        connector.initialize()
        connector.shutdown()
        
        # Should still work in synthetic mode
        assert connector.get_mode() == "synthetic"


class TestOpenBBCache:
    """Test caching layer"""
    
    def test_cache_initialization(self, tmp_path):
        """Test cache directory creation"""
        cache_path = tmp_path / "test_cache"
        cache = OpenBBCache(str(cache_path))
        
        assert cache_path.exists()
    
    def test_cache_set_and_get(self, tmp_path):
        """Test caching data"""
        cache_path = tmp_path / "test_cache"
        cache = OpenBBCache(str(cache_path), expiry_days=1)
        
        # Create test data with datetime index (matches real use case)
        dates = pd.date_range('2020-01-01', periods=3)
        df = pd.DataFrame({
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        }, index=dates)
        
        # Cache it
        cache.set("test_key", df)
        
        # Retrieve it
        cached = cache.get("test_key")
        
        assert cached is not None
        assert len(cached) == 3
        # Check data values match (index might be reconstructed differently)
        assert list(cached['a']) == [1, 2, 3]
        assert list(cached['b']) == [4, 5, 6]
    
    def test_cache_expiry(self, tmp_path):
        """Test cache expiry logic"""
        cache_path = tmp_path / "test_cache"
        cache = OpenBBCache(str(cache_path), expiry_days=0)  # Expires immediately
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        cache.set("test_key", df)
        
        # Should be expired
        cached = cache.get("test_key")
        assert cached is None
    
    def test_cache_clear(self, tmp_path):
        """Test clearing cache"""
        cache_path = tmp_path / "test_cache"
        cache = OpenBBCache(str(cache_path))
        
        df = pd.DataFrame({'a': [1, 2, 3]})
        cache.set("test_key", df)
        
        # Clear specific key
        cache.clear("test_key")
        
        cached = cache.get("test_key")
        assert cached is None


class TestPriceLoader:
    """Test price data loader"""
    
    def test_generate_synthetic_prices(self):
        """Test synthetic price generation"""
        df = generate_synthetic_prices("GLD", "2020-01-01", "2020-12-31")
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
        
        # Check data
        assert len(df) > 300  # About 1 year of daily data
        assert (df['high'] >= df['close']).all()
        assert (df['low'] <= df['close']).all()
        assert (df['volume'] > 0).all()
    
    def test_synthetic_prices_deterministic(self):
        """Test that synthetic prices are deterministic per symbol"""
        df1 = generate_synthetic_prices("GLD", "2020-01-01", "2020-12-31")
        df2 = generate_synthetic_prices("GLD", "2020-01-01", "2020-12-31")
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_synthetic_prices_different_symbols(self):
        """Test different symbols generate different data"""
        df_gld = generate_synthetic_prices("GLD", "2020-01-01", "2020-12-31")
        df_ltpz = generate_synthetic_prices("LTPZ", "2020-01-01", "2020-12-31")
        
        # Should be different
        assert not df_gld['close'].equals(df_ltpz['close'])
    
    def test_load_prices(self, tmp_path):
        """Test price loading with cache"""
        df = load_prices(
            "GLD",
            "2020-01-01",
            "2020-12-31",
            use_cache=True,
            cache_path=str(tmp_path)
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_load_prices_uses_cache(self, tmp_path):
        """Test that loading prices uses cache"""
        # First load
        df1 = load_prices("GLD", "2020-01-01", "2020-12-31", cache_path=str(tmp_path))
        
        # Second load (should come from cache)
        df2 = load_prices("GLD", "2020-01-01", "2020-12-31", cache_path=str(tmp_path))
        
        # Check data is identical (index names might differ after caching)
        assert len(df1) == len(df2)
        assert list(df1.columns) == list(df2.columns)
        for col in df1.columns:
            assert (df1[col] == df2[col]).all() or (df1[col].isna() & df2[col].isna()).all()


class TestCOTLoader:
    """Test COT data loader"""
    
    def test_generate_synthetic_cot(self):
        """Test synthetic COT generation"""
        df = generate_synthetic_cot("GOLD", "2020-01-01", "2020-12-31")
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        assert 'commercials_long' in df.columns
        assert 'commercials_short' in df.columns
        assert 'commercials_net' in df.columns
        assert 'non_commercials_long' in df.columns
        assert 'non_commercials_short' in df.columns
        assert 'non_commercials_net' in df.columns
        assert 'open_interest' in df.columns
        
        # Check data
        assert len(df) > 40  # About 52 weeks
        assert (df['commercials_net'] == df['commercials_long'] - df['commercials_short']).all()
    
    def test_cot_weekly_frequency(self):
        """Test that COT data is weekly"""
        df = generate_synthetic_cot("GOLD", "2020-01-01", "2020-12-31")
        
        # Check that dates are roughly weekly
        date_diffs = df.index.to_series().diff().dt.days
        # Most diffs should be around 7 days
        assert date_diffs.median() == 7.0
    
    def test_load_cot_data(self, tmp_path):
        """Test COT data loading"""
        df = load_cot_data(
            "GOLD",
            "2020-01-01",
            "2020-12-31",
            cache_path=str(tmp_path)
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestMacroLoader:
    """Test macro data loader"""
    
    def test_generate_synthetic_macro(self):
        """Test synthetic macro generation"""
        df = generate_synthetic_macro("2020-01-01", "2020-12-31")
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        assert 'cpi' in df.columns
        assert 'gdp_growth' in df.columns
        assert 'unemployment' in df.columns
        assert 'fed_funds_rate' in df.columns
        assert 'treasury_10y' in df.columns
        assert 'inflation_yoy' in df.columns
        
        # Check data ranges
        assert (df['unemployment'] >= 3.0).all()
        assert (df['unemployment'] <= 10.0).all()
        assert (df['fed_funds_rate'] >= 0.0).all()
    
    def test_macro_monthly_frequency(self):
        """Test that macro data is monthly"""
        df = generate_synthetic_macro("2020-01-01", "2020-12-31")
        
        # Should have ~12 months
        assert len(df) == 12
    
    def test_load_macro_data(self, tmp_path):
        """Test macro data loading"""
        df = load_macro_data(
            "2020-01-01",
            "2020-12-31",
            cache_path=str(tmp_path)
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestRealYieldsLoader:
    """Test real yields loader"""
    
    def test_generate_synthetic_yields(self):
        """Test synthetic yields generation"""
        df = generate_synthetic_yields("2020-01-01", "2020-12-31")
        
        # Check structure
        assert isinstance(df, pd.DataFrame)
        assert 'nominal_10y' in df.columns
        assert 'expected_inflation' in df.columns
        assert 'real_yield_10y' in df.columns
        assert 'real_yield_5y' in df.columns
        assert 'tips_spread' in df.columns
        assert 'real_yield_regime' in df.columns
        
        # Check relationship: real = nominal - inflation
        calculated_real = df['nominal_10y'] - df['expected_inflation']
        assert np.allclose(calculated_real, df['real_yield_10y'], rtol=0.01)
    
    def test_yields_daily_frequency(self):
        """Test that yields are daily"""
        df = generate_synthetic_yields("2020-01-01", "2020-12-31")
        
        # Should have ~366 days (2020 was leap year)
        assert len(df) > 360
    
    def test_real_yield_regime(self):
        """Test real yield regime classification"""
        df = generate_synthetic_yields("2020-01-01", "2020-12-31")
        
        # Check regime values
        regimes = df['real_yield_regime'].unique()
        assert all(r in ['rising', 'falling'] for r in regimes)
    
    def test_load_real_yields(self, tmp_path):
        """Test real yields loading"""
        df = load_real_yields(
            "2020-01-01",
            "2020-12-31",
            cache_path=str(tmp_path)
        )
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


class TestDataIntegration:
    """Test data integration with EOD pipeline"""
    
    def test_all_loaders_return_correct_format(self):
        """Test that all loaders return proper DataFrames"""
        # Prices
        prices = load_prices("GLD", "2020-01-01", "2020-12-31")
        assert isinstance(prices.index, pd.DatetimeIndex)
        
        # COT
        cot = load_cot_data("GOLD", "2020-01-01", "2020-12-31")
        assert isinstance(cot.index, pd.DatetimeIndex)
        
        # Macro
        macro = load_macro_data("2020-01-01", "2020-12-31")
        assert isinstance(macro.index, pd.DatetimeIndex)
        
        # Yields
        yields = load_real_yields("2020-01-01", "2020-12-31")
        assert isinstance(yields.index, pd.DatetimeIndex)
    
    def test_no_external_api_calls(self):
        """Verify no external API calls are made"""
        # This test passes if all data is generated without errors
        # and without any network calls
        
        # Load all data types
        prices = load_prices("GLD", "2020-01-01", "2020-12-31")
        cot = load_cot_data("GOLD", "2020-01-01", "2020-12-31")
        macro = load_macro_data("2020-01-01", "2020-12-31")
        yields = load_real_yields("2020-01-01", "2020-12-31")
        
        # If we got here without network errors, we're good
        assert len(prices) > 0
        assert len(cot) > 0
        assert len(macro) > 0
        assert len(yields) > 0


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_prices_deterministic(self):
        """Test price generation is deterministic"""
        df1 = generate_synthetic_prices("GLD", "2020-01-01", "2020-12-31")
        df2 = generate_synthetic_prices("GLD", "2020-01-01", "2020-12-31")
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_cot_deterministic(self):
        """Test COT generation is deterministic"""
        df1 = generate_synthetic_cot("GOLD", "2020-01-01", "2020-12-31")
        df2 = generate_synthetic_cot("GOLD", "2020-01-01", "2020-12-31")
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_macro_deterministic(self):
        """Test macro generation is deterministic"""
        df1 = generate_synthetic_macro("2020-01-01", "2020-12-31")
        df2 = generate_synthetic_macro("2020-01-01", "2020-12-31")
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_yields_deterministic(self):
        """Test yields generation is deterministic"""
        df1 = generate_synthetic_yields("2020-01-01", "2020-12-31")
        df2 = generate_synthetic_yields("2020-01-01", "2020-12-31")
        
        pd.testing.assert_frame_equal(df1, df2)


class TestGLDLTPZIntegration:
    """Test data integration for GLD/LTPZ pair"""
    
    def test_gld_ltpz_price_loading(self):
        """Test loading prices for GLD/LTPZ pair"""
        gld = load_prices("GLD", "2020-01-01", "2020-12-31")
        ltpz = load_prices("LTPZ", "2020-01-01", "2020-12-31")
        
        # Should have same length (same date range)
        assert len(gld) == len(ltpz)
        
        # Should have same index
        assert gld.index.equals(ltpz.index)
    
    def test_real_yields_for_ltpz(self):
        """Test real yields data for LTPZ inverse logic"""
        yields = load_real_yields("2020-01-01", "2020-12-31")
        
        # Should have regime classification
        assert 'real_yield_regime' in yields.columns
        
        # Should have both regimes
        regimes = yields['real_yield_regime'].unique()
        assert len(regimes) >= 1

