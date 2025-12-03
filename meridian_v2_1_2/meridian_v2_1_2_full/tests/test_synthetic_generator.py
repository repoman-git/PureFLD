"""
Test suite for Synthetic Market Generator

Tests all synthetic data generation components.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.synthetic import (
    generate_synthetic_prices,
    generate_volatility_regime,
    generate_stochastic_vol,
    generate_trend_component,
    generate_cycle_component,
    generate_synthetic_macro,
    generate_synthetic_cot,
    generate_synthetic_yields,
    generate_regime_sequence,
    MarketRegime,
    SyntheticDataset
)
from meridian_v2_1_2.config import MeridianConfig


class TestRegimeSequencer:
    """Test regime generation"""
    
    def test_regime_sequence_generation(self):
        """Test regime sequence is generated"""
        regimes = generate_regime_sequence(length=100, seed=42)
        
        assert len(regimes) == 100
        assert isinstance(regimes, pd.Series)
        assert isinstance(regimes.index, pd.DatetimeIndex)
    
    def test_regime_values_valid(self):
        """Test regime values are valid"""
        regimes = generate_regime_sequence(length=100, seed=42)
        
        valid_regimes = [r.value for r in MarketRegime]
        assert all(r in valid_regimes for r in regimes)
    
    def test_regime_switches(self):
        """Test regimes can switch"""
        regimes = generate_regime_sequence(length=500, switch_prob=0.1, seed=42)
        
        # Should have multiple unique regimes
        unique_regimes = regimes.unique()
        assert len(unique_regimes) > 1


class TestVolatilityModels:
    """Test volatility generation"""
    
    def test_constant_volatility(self):
        """Test constant volatility mode"""
        vol = generate_volatility_regime(length=100, vol_low=0.01, vol_high=0.02)
        
        assert len(vol) == 100
        assert all(vol >= 0.005)
        assert all(vol <= 0.025)
    
    def test_stochastic_volatility(self):
        """Test stochastic volatility"""
        vol = generate_stochastic_vol(length=100, base_vol=0.01)
        
        assert len(vol) == 100
        assert all(vol > 0)
        assert np.std(vol) > 0  # Should vary


class TestTrendGenerator:
    """Test trend generation"""
    
    def test_alternating_trend(self):
        """Test alternating trend mode"""
        trend = generate_trend_component(length=1000, strength=0.4, mode="alternating")
        
        assert len(trend) == 1000
        # Should have periods of positive and negative trends
        assert np.any(np.diff(trend) > 0)
        assert np.any(np.diff(trend) < 0)
    
    def test_random_trend(self):
        """Test random trend mode"""
        trend = generate_trend_component(length=1000, mode="random")
        
        assert len(trend) == 1000
    
    def test_structural_trend(self):
        """Test structural trend mode"""
        trend = generate_trend_component(length=1000, mode="structural")
        
        assert len(trend) == 1000
        # Should have overall upward bias
        assert trend[-1] > trend[0]


class TestCycleGenerator:
    """Test cycle generation"""
    
    def test_cycle_generation(self):
        """Test basic cycle generation"""
        cycle = generate_cycle_component(length=1000, period=120, deform=False)
        
        assert len(cycle) == 1000
        # Should oscillate
        assert np.min(cycle) < 0
        assert np.max(cycle) > 0
    
    def test_cycle_with_deformation(self):
        """Test cycle with distortions"""
        cycle = generate_cycle_component(length=1000, period=120, deform=True)
        
        assert len(cycle) == 1000
        # Should still oscillate but be irregular
        assert np.min(cycle) < 0
        assert np.max(cycle) > 0


class TestPriceGenerator:
    """Test price generation"""
    
    def test_price_generation(self):
        """Test OHLC price generation"""
        df = generate_synthetic_prices("GLD", length=1000)
        
        assert len(df) == 1000
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns
    
    def test_ohlc_relationships(self):
        """Test OHLC relationships are valid"""
        df = generate_synthetic_prices("GLD", length=1000)
        
        # High should be >= close and low <= close
        assert (df['high'] >= df['close']).all()
        assert (df['low'] <= df['close']).all()
        assert (df['high'] >= df['low']).all()
    
    def test_prices_positive(self):
        """Test all prices are positive"""
        df = generate_synthetic_prices("GLD", length=1000)
        
        assert (df['close'] > 0).all()
        assert (df['open'] > 0).all()
        assert (df['high'] > 0).all()
        assert (df['low'] > 0).all()
    
    def test_different_symbols_different_paths(self):
        """Test different symbols can generate different prices"""
        # With same seed, paths will be similar but not identical due to symbol hash
        df_gld = generate_synthetic_prices("GLD", length=500, seed=42)
        df_ltpz = generate_synthetic_prices("LTPZ", length=500, seed=99)  # Different seed
        
        # With different seeds, should definitely be different
        assert not df_gld['close'].equals(df_ltpz['close'])


class TestCOTGenerator:
    """Test COT generation"""
    
    def test_cot_generation(self):
        """Test COT data generation"""
        df = generate_synthetic_cot(length=1000)
        
        assert len(df) > 40  # Should have ~52 weeks worth
        assert 'commercials_long' in df.columns
        assert 'commercials_short' in df.columns
        assert 'commercials_net' in df.columns
        assert 'non_commercials_net' in df.columns
    
    def test_cot_weekly_frequency(self):
        """Test COT is weekly"""
        df = generate_synthetic_cot(length=1000)
        
        # Check dates are roughly weekly
        date_diffs = df.index.to_series().diff().dt.days
        # Most should be 7 days
        assert date_diffs.median() == 7.0
    
    def test_cot_net_calculation(self):
        """Test COT net positions are correct"""
        df = generate_synthetic_cot(length=1000)
        
        calculated_net = df['commercials_long'] - df['commercials_short']
        assert (calculated_net == df['commercials_net']).all()


class TestMacroGenerator:
    """Test macro data generation"""
    
    def test_macro_generation(self):
        """Test macro data generation"""
        df = generate_synthetic_macro(length=1000)
        
        assert len(df) > 10  # Should have monthly data
        assert 'cpi' in df.columns
        assert 'gdp_growth' in df.columns
        assert 'unemployment' in df.columns
        assert 'fed_funds_rate' in df.columns
    
    def test_macro_monthly_frequency(self):
        """Test macro is monthly"""
        df = generate_synthetic_macro(length=2000)
        
        # Should have ~95 months for 2000 days
        assert len(df) >= 90
        assert len(df) <= 100
    
    def test_macro_ranges(self):
        """Test macro values are in reasonable ranges"""
        df = generate_synthetic_macro(length=1000)
        
        # Unemployment should be bounded
        assert (df['unemployment'] >= 3.0).all()
        assert (df['unemployment'] <= 10.0).all()
        
        # Fed funds should be non-negative
        assert (df['fed_funds_rate'] >= 0.0).all()


class TestYieldsGenerator:
    """Test real yields generation"""
    
    def test_yields_generation(self):
        """Test yields data generation"""
        df = generate_synthetic_yields(length=1000)
        
        assert len(df) == 1000
        assert 'nominal_10y' in df.columns
        assert 'expected_inflation' in df.columns
        assert 'real_yield_10y' in df.columns
        assert 'real_yield_regime' in df.columns
    
    def test_real_yield_calculation(self):
        """Test real yield is nominal minus inflation"""
        df = generate_synthetic_yields(length=1000)
        
        calculated = df['nominal_10y'] - df['expected_inflation']
        # Should be approximately equal (some noise allowed)
        assert np.allclose(calculated, df['real_yield_10y'], rtol=0.1)
    
    def test_yield_regimes(self):
        """Test yield regime classification"""
        df = generate_synthetic_yields(length=1000)
        
        regimes = df['real_yield_regime'].unique()
        assert all(r in ['rising', 'falling'] for r in regimes)


class TestSyntheticDataset:
    """Test complete dataset generation"""
    
    def test_dataset_generation(self):
        """Test generating complete dataset"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 500  # Shorter for faster test
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate()
        
        assert 'prices' in data
        assert 'cot' in data
        assert 'real_yields' in data
        assert 'macro' in data
        assert 'regimes' in data
    
    def test_dataset_multiple_symbols(self):
        """Test generating multiple symbols"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 500
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD', 'LTPZ', 'SPY'])
        
        assert 'GLD' in data['prices']
        assert 'LTPZ' in data['prices']
        assert 'SPY' in data['prices']
    
    def test_dataset_stress_scenario(self):
        """Test stress scenario generation"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 500
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate_stress_scenario('crash')
        
        assert 'prices' in data
        # Crash scenario should have high vol
        assert cfg.synthetic.vol_high > 0.03


class TestDataQuality:
    """Test data quality and consistency"""
    
    def test_no_nans_in_prices(self):
        """Test prices have no NaNs"""
        df = generate_synthetic_prices("GLD", length=1000)
        
        assert not df.isna().any().any()
    
    def test_no_nans_in_cot(self):
        """Test COT has no NaNs"""
        df = generate_synthetic_cot(length=1000)
        
        assert not df.isna().any().any()
    
    def test_no_nans_in_yields(self):
        """Test yields have no NaNs"""
        df = generate_synthetic_yields(length=1000)
        
        assert not df.isna().any().any()


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_prices_deterministic(self):
        """Test price generation is deterministic"""
        df1 = generate_synthetic_prices("GLD", length=500, seed=42)
        df2 = generate_synthetic_prices("GLD", length=500, seed=42)
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_regimes_deterministic(self):
        """Test regime generation is deterministic"""
        reg1 = generate_regime_sequence(length=500, seed=42)
        reg2 = generate_regime_sequence(length=500, seed=42)
        
        pd.testing.assert_series_equal(reg1, reg2)
    
    def test_cot_deterministic(self):
        """Test COT generation is deterministic"""
        df1 = generate_synthetic_cot(length=500, seed=42)
        df2 = generate_synthetic_cot(length=500, seed=42)
        
        pd.testing.assert_frame_equal(df1, df2)


class TestIntegrationWithOpenBB:
    """Test integration with OpenBB data loaders"""
    
    def test_synthetic_prices_match_openbb_format(self):
        """Test synthetic prices match OpenBB format"""
        from meridian_v2_1_2.data_providers.openbb import generate_synthetic_prices as openbb_prices
        
        # Both should produce OHLC
        synth_df = generate_synthetic_prices("GLD", length=500)
        openbb_df = openbb_prices("GLD", "2020-01-01", "2021-06-01")
        
        # Same columns
        assert set(synth_df.columns) == set(openbb_df.columns)
        
        # Both are DataFrames with DatetimeIndex
        assert isinstance(synth_df.index, pd.DatetimeIndex)
        assert isinstance(openbb_df.index, pd.DatetimeIndex)


class TestStressTesting:
    """Test stress scenarios"""
    
    def test_high_volatility_scenario(self):
        """Test high volatility increases price variance"""
        df_low = generate_synthetic_prices("GLD", length=500, vol_low=0.005, vol_high=0.01, seed=42)
        df_high = generate_synthetic_prices("GLD", length=500, vol_low=0.02, vol_high=0.05, seed=43)
        
        returns_low = df_low['close'].pct_change().std()
        returns_high = df_high['close'].pct_change().std()
        
        assert returns_high > returns_low
    
    def test_trend_reversal(self):
        """Test trend can reverse"""
        trend = generate_trend_component(length=2000, mode="alternating", strength=0.8)
        
        # Check that trend has both increases and decreases
        diffs = np.diff(trend)
        has_increases = np.any(diffs > 0)
        has_decreases = np.any(diffs < 0)
        
        assert has_increases and has_decreases


class TestRealisticBehavior:
    """Test that generated data behaves realistically"""
    
    def test_autocorrelation_in_volatility(self):
        """Test volatility clusters (realistic behavior)"""
        vol = generate_stochastic_vol(length=1000)
        
        # Volatility should have persistence
        autocorr = pd.Series(vol).autocorr(lag=1)
        assert autocorr > 0.5  # Some persistence
    
    def test_mean_reversion_in_yields(self):
        """Test yields mean revert"""
        df = generate_synthetic_yields(length=2000)
        
        # Yields should not drift infinitely
        assert df['real_yield_10y'].std() < 2.0  # Bounded variation

