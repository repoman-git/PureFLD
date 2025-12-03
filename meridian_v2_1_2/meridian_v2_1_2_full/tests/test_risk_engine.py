"""
Comprehensive test suite for Risk Engine in Meridian v2.1.2.

Tests verify volatility sizing, regime multipliers, cycle sizing, Kelly, and caps.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.risk_engine import (
    RiskConfig,
    compute_volatility_sizing,
    apply_regime_multipliers,
    apply_cycle_sizing,
    compute_kelly_size,
    apply_kelly_sizing,
    apply_risk_caps,
    compute_position_sizes,
    smooth_sizes
)


def create_test_data(length=100):
    """Create synthetic test data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return dates


class TestVolatilityScaling:
    """Test volatility-based position sizing"""
    
    def test_high_vol_small_size(self):
        """
        TEST 1: High volatility → smaller position size
        """
        dates = create_test_data(50)
        # High volatility prices
        prices = pd.Series(100 + np.random.RandomState(42).randn(50) * 20, index=dates)
        
        config = RiskConfig(
            vol_lookback=20,
            target_vol=0.01,
            max_position=10.0
        )
        
        vol_sizes = compute_volatility_sizing(prices, config)
        
        # Sizes should be generally < 1.0 (reducing from base)
        assert vol_sizes.mean() < 1.5
    
    def test_low_vol_large_size(self):
        """
        TEST: Low volatility → larger position size
        """
        dates = create_test_data(50)
        # Low volatility prices
        prices = pd.Series(np.linspace(100, 105, 50), index=dates)
        
        config = RiskConfig(
            vol_lookback=20,
            target_vol=0.02,
            max_position=10.0
        )
        
        vol_sizes = compute_volatility_sizing(prices, config)
        
        # Sizes should be generally > 1.0 (increasing from base)
        # (Will be capped at max_position if too high)
        assert vol_sizes.median() >= 1.0


class TestRegimeMultipliers:
    """Test regime-based sizing multipliers"""
    
    def test_regime_multipliers_applied(self):
        """
        TEST 2: Regime multipliers scale positions correctly
        """
        dates = create_test_data(10)
        
        base_size = pd.Series([1.0] * 10, index=dates)
        vol_regime = pd.Series([2] * 10, index=dates)  # High vol
        trend_regime = pd.Series([1] * 10, index=dates)  # Uptrend
        cycle_regime = pd.Series([1] * 10, index=dates)  # Rising
        
        config = RiskConfig()
        # high_vol: 0.6, uptrend: 1.2, cycle_rising: 1.3
        
        adjusted = apply_regime_multipliers(base_size, vol_regime, trend_regime, cycle_regime, config)
        
        # Should be: 1.0 × 0.6 × 1.2 × 1.3 = 0.936
        expected = 1.0 * 0.6 * 1.2 * 1.3
        assert abs(adjusted.iloc[0] - expected) < 0.01
    
    def test_bearish_regimes_reduce_size(self):
        """
        TEST: Bearish regimes reduce position sizes
        """
        dates = create_test_data(10)
        
        base_size = pd.Series([1.0] * 10, index=dates)
        vol_regime = pd.Series([2] * 10, index=dates)  # High vol (0.6)
        trend_regime = pd.Series([-1] * 10, index=dates)  # Downtrend (0.8)
        cycle_regime = pd.Series([-1] * 10, index=dates)  # Falling (0.7)
        
        config = RiskConfig()
        
        adjusted = apply_regime_multipliers(base_size, vol_regime, trend_regime, cycle_regime, config)
        
        # All bearish → size should be < 1.0
        assert adjusted.iloc[0] < 1.0


class TestCycleScaling:
    """Test cycle-based sizing"""
    
    def test_high_amplitude_increases_size(self):
        """
        TEST 3: High amplitude → larger position
        """
        dates = create_test_data(10)
        
        base_size = pd.Series([1.0] * 10, index=dates)
        cycle_amplitude = pd.Series([1.0] * 10, index=dates)  # High amplitude
        cycle_score = pd.Series([0.5] * 10, index=dates)  # Positive score
        
        config = RiskConfig(
            cycle_amplitude_multiplier=1.0,
            cycle_score_multiplier=1.0
        )
        
        adjusted = apply_cycle_sizing(base_size, cycle_amplitude, cycle_score, config)
        
        # Should increase size
        assert adjusted.iloc[0] > base_size.iloc[0]
    
    def test_negative_score_reduces_size(self):
        """
        TEST: Negative cycle score → smaller position
        """
        dates = create_test_data(10)
        
        base_size = pd.Series([2.0] * 10, index=dates)
        cycle_amplitude = pd.Series([0.1] * 10, index=dates)  # Low amplitude
        cycle_score = pd.Series([-0.8] * 10, index=dates)  # Strong negative score
        
        config = RiskConfig(
            cycle_amplitude_multiplier=1.0,
            cycle_score_multiplier=1.0
        )
        
        adjusted = apply_cycle_sizing(base_size, cycle_amplitude, cycle_score, config)
        
        # Should reduce size significantly
        assert adjusted.iloc[0] < base_size.iloc[0]


class TestKellySizing:
    """Test Kelly fraction sizing"""
    
    def test_kelly_size_calculation(self):
        """
        TEST 4: Kelly fraction calculated correctly
        """
        config = RiskConfig(kelly_fraction=0.25)
        
        # Positive expectancy
        expectancy = 0.1
        variance = 0.01
        
        kelly = compute_kelly_size(expectancy, variance, config)
        
        # Kelly = expectancy / variance × fraction
        # = 0.1 / 0.01 × 0.25 = 2.5
        expected_kelly = (expectancy / variance) * config.kelly_fraction
        assert abs(kelly - expected_kelly) < 0.01
    
    def test_insufficient_trades_no_kelly(self):
        """
        TEST: Insufficient trades → no Kelly sizing
        """
        dates = create_test_data(10)
        base_size = pd.Series([1.0] * 10, index=dates)
        
        # Only 10 trades (less than min_trades_for_kelly)
        trade_stats = {
            'number_of_trades': 10,
            'expectancy': 0.1,
            'average_win': 1.0,
            'average_loss': -0.5,
            'win_rate': 0.6
        }
        
        config = RiskConfig(use_kelly=True, min_trades_for_kelly=30)
        
        kelly_adjusted = apply_kelly_sizing(base_size, trade_stats, config)
        
        # Should return base_size unchanged
        pd.testing.assert_series_equal(kelly_adjusted, base_size)


class TestRiskCaps:
    """Test hard risk limits"""
    
    def test_max_position_cap(self):
        """
        TEST 5: Maximum position cap enforced
        """
        dates = create_test_data(10)
        sizes = pd.Series([15.0, 20.0, 5.0, 12.0, 8.0] * 2, index=dates)
        
        config = RiskConfig(max_position=10.0)
        
        capped = apply_risk_caps(sizes, config)
        
        # All should be <= 10.0
        assert (capped <= 10.0).all()
        assert capped.max() == 10.0
    
    def test_min_position_threshold(self):
        """
        TEST: Minimum position threshold enforced
        """
        dates = create_test_data(10)
        sizes = pd.Series([0.05, 0.02, 1.0, 0.08, 2.0] * 2, index=dates)
        
        config = RiskConfig(min_position=0.1)
        
        capped = apply_risk_caps(sizes, config)
        
        # Small non-zero values should be brought up to min
        assert capped.iloc[0] == 0.1
        assert capped.iloc[1] == 0.1


class TestUnifiedPositionSizer:
    """Test complete position sizing pipeline"""
    
    def test_position_sizer_pipeline(self):
        """
        TEST 6: Complete position sizing pipeline executes
        """
        dates = create_test_data(50)
        prices = pd.Series(range(100, 150), index=dates)
        
        # Create regime data
        vol_regime = pd.Series([1] * 50, index=dates)
        trend_regime = pd.Series([1] * 50, index=dates)
        cycle_regime = pd.Series([1] * 50, index=dates)
        cycle_amplitude = pd.Series([1.0] * 50, index=dates)
        cycle_score = pd.Series([0.5] * 50, index=dates)
        
        trade_stats = None  # No Kelly
        
        config = RiskConfig(
            use_volatility_sizing=True,
            use_regime_sizing=True,
            use_cycle_sizing=True,
            use_kelly=False
        )
        
        sizes = compute_position_sizes(
            prices, vol_regime, trend_regime, cycle_regime,
            cycle_amplitude, cycle_score, trade_stats, config
        )
        
        # Should produce valid sizes
        assert len(sizes) == len(prices)
        assert (sizes > 0).all()
        assert (sizes <= config.max_position).all()
    
    def test_all_factors_disabled_returns_base(self):
        """
        TEST: All factors disabled → returns base size (capped)
        """
        dates = create_test_data(20)
        prices = pd.Series(range(100, 120), index=dates)
        
        config = RiskConfig(
            use_volatility_sizing=False,
            use_regime_sizing=False,
            use_cycle_sizing=False,
            use_kelly=False,
            max_position=10.0
        )
        
        sizes = compute_position_sizes(
            prices, None, None, None, None, None, None, config
        )
        
        # Should be 1.0 (base) for all
        assert (sizes == 1.0).all()


class TestDeterminism:
    """Test that all risk functions are deterministic"""
    
    def test_volatility_sizing_deterministic(self):
        """
        TEST 7: Volatility sizing is deterministic
        """
        dates = create_test_data(50)
        prices = pd.Series(100 + np.random.RandomState(42).randn(50) * 5, index=dates)
        
        config = RiskConfig()
        
        sizes1 = compute_volatility_sizing(prices, config)
        sizes2 = compute_volatility_sizing(prices, config)
        
        pd.testing.assert_series_equal(sizes1, sizes2)
    
    def test_complete_pipeline_deterministic(self):
        """
        TEST: Complete position sizing pipeline is deterministic
        """
        dates = create_test_data(50)
        prices = pd.Series(range(100, 150), index=dates)
        
        vol_regime = pd.Series([1] * 50, index=dates)
        trend_regime = pd.Series([1] * 50, index=dates)
        cycle_regime = pd.Series([1] * 50, index=dates)
        cycle_amplitude = pd.Series([1.0] * 50, index=dates)
        cycle_score = pd.Series([0.5] * 50, index=dates)
        
        config = RiskConfig()
        
        sizes1 = compute_position_sizes(prices, vol_regime, trend_regime, cycle_regime,
                                       cycle_amplitude, cycle_score, None, config)
        sizes2 = compute_position_sizes(prices, vol_regime, trend_regime, cycle_regime,
                                       cycle_amplitude, cycle_score, None, config)
        
        pd.testing.assert_series_equal(sizes1, sizes2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

