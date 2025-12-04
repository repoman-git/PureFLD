"""
Comprehensive test suite for Regime Classification Engine in Meridian v2.1.2.

Tests verify volatility, trend, and cycle regime detection and composite scoring.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.config import RegimeConfig
from meridian_v2_1_2.regimes import (
    classify_volatility,
    classify_trend,
    classify_cycle_regime,
    compute_composite_regime,
    normalize_regime,
    smooth_regime
)


def create_test_data(length=100):
    """Create synthetic test data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return dates


class TestVolatilityRegime:
    """Test volatility regime classification"""
    
    def test_low_vol_synthetic(self):
        """
        TEST 1: Low volatility series classified correctly
        """
        dates = create_test_data(50)
        # Very stable prices
        prices = pd.Series(np.linspace(100, 101, 50), index=dates)
        
        config = RegimeConfig(
            vol_lookback=20,
            vol_threshold_low=0.01,
            vol_threshold_high=0.03
        )
        
        vol_regime = classify_volatility(prices, config)
        
        # Most should be low vol (0)
        assert (vol_regime == 0).sum() > len(vol_regime) * 0.5
    
    def test_high_vol_synthetic(self):
        """
        TEST: High volatility series classified correctly
        """
        dates = create_test_data(50)
        # Noisy prices
        prices = pd.Series(100 + np.random.RandomState(42).randn(50) * 10, index=dates)
        
        config = RegimeConfig(
            vol_lookback=20,
            vol_threshold_low=0.005,
            vol_threshold_high=0.02
        )
        
        vol_regime = classify_volatility(prices, config)
        
        # Should have some high vol periods (2)
        assert (vol_regime == 2).sum() > 0
    
    def test_medium_vol_default(self):
        """
        TEST: Medium volatility as default
        """
        dates = create_test_data(30)
        prices = pd.Series(range(100, 130), index=dates)
        
        config = RegimeConfig(vol_lookback=20)
        
        vol_regime = classify_volatility(prices, config)
        
        # Should have medium vol periods
        assert (vol_regime == 1).sum() > 0


class TestTrendRegime:
    """Test trend regime classification"""
    
    def test_strong_uptrend(self):
        """
        TEST 2: Strong uptrend classified correctly
        """
        dates = create_test_data(100)
        # Clear uptrend
        prices = pd.Series(range(100, 200), index=dates)
        
        config = RegimeConfig(
            trend_lookback=50,
            trend_threshold=0.1
        )
        
        trend_regime = classify_trend(prices, config)
        
        # Most should be uptrend (+1)
        assert (trend_regime == 1).sum() > len(trend_regime) * 0.5
    
    def test_strong_downtrend(self):
        """
        TEST: Strong downtrend classified correctly
        """
        dates = create_test_data(100)
        # Clear downtrend
        prices = pd.Series(range(200, 100, -1), index=dates)
        
        config = RegimeConfig(
            trend_lookback=50,
            trend_threshold=0.1
        )
        
        trend_regime = classify_trend(prices, config)
        
        # Most should be downtrend (-1)
        assert (trend_regime == -1).sum() > len(trend_regime) * 0.5
    
    def test_chop_regime(self):
        """
        TEST: Choppy market classified as neutral
        """
        dates = create_test_data(50)
        # Oscillating around 100
        prices = pd.Series([100 + 5 * np.sin(i) for i in range(50)], index=dates)
        
        config = RegimeConfig(
            trend_lookback=20,
            trend_threshold=0.5
        )
        
        trend_regime = classify_trend(prices, config)
        
        # Should have chop periods (0)
        assert (trend_regime == 0).sum() > 0


class TestCycleRegime:
    """Test cycle regime classification"""
    
    def test_cycle_rising_phase(self):
        """
        TEST 3: Cycle rising phase classified correctly
        """
        dates = create_test_data(50)
        
        # Phase in trough zone (0.0-0.33)
        cycle_phase = pd.Series([0.1, 0.2, 0.3] * 16 + [0.1, 0.2], index=dates)
        
        # Sufficient amplitude
        cycle_amplitude = pd.Series([1.0] * 50, index=dates)
        
        config = RegimeConfig(amplitude_threshold=0.5)
        
        cycle_regime = classify_cycle_regime(cycle_phase, cycle_amplitude, config)
        
        # All should be rising (+1)
        assert (cycle_regime == 1).sum() == 50
    
    def test_cycle_falling_phase(self):
        """
        TEST: Cycle falling phase classified correctly
        """
        dates = create_test_data(50)
        
        # Phase in decline zone (0.66-1.0)
        cycle_phase = pd.Series([0.7, 0.8, 0.9] * 16 + [0.7, 0.8], index=dates)
        
        # Sufficient amplitude
        cycle_amplitude = pd.Series([1.0] * 50, index=dates)
        
        config = RegimeConfig(amplitude_threshold=0.5)
        
        cycle_regime = classify_cycle_regime(cycle_phase, cycle_amplitude, config)
        
        # All should be falling (-1)
        assert (cycle_regime == -1).sum() == 50
    
    def test_weak_amplitude_neutral(self):
        """
        TEST: Weak amplitude → neutral regardless of phase
        """
        dates = create_test_data(50)
        
        # Any phase
        cycle_phase = pd.Series([0.1] * 50, index=dates)
        
        # Insufficient amplitude
        cycle_amplitude = pd.Series([0.2] * 50, index=dates)
        
        config = RegimeConfig(amplitude_threshold=0.5)
        
        cycle_regime = classify_cycle_regime(cycle_phase, cycle_amplitude, config)
        
        # All should be neutral (0)
        assert (cycle_regime == 0).sum() == 50


class TestCompositeRegime:
    """Test composite regime scoring"""
    
    def test_composite_weighted_score(self):
        """
        TEST 4: Composite regime uses weighted combination
        """
        dates = create_test_data(10)
        
        # All bullish
        vol_regime = pd.Series([2] * 10, index=dates)    # High vol → +1
        trend_regime = pd.Series([1] * 10, index=dates)  # Uptrend → +1
        cycle_regime = pd.Series([1] * 10, index=dates)  # Rising → +1
        
        config = RegimeConfig(smoothing_window=1)
        
        composite = compute_composite_regime(vol_regime, trend_regime, cycle_regime, config)
        
        # Should be positive (all bullish)
        assert (composite > 0).all()
    
    def test_composite_smoothing(self):
        """
        TEST: Composite regime applies smoothing
        """
        dates = create_test_data(20)
        
        # Alternating regimes
        vol_regime = pd.Series([0, 2] * 10, index=dates)
        trend_regime = pd.Series([1, -1] * 10, index=dates)
        cycle_regime = pd.Series([1, -1] * 10, index=dates)
        
        config_no_smooth = RegimeConfig(smoothing_window=1)
        config_smooth = RegimeConfig(smoothing_window=5)
        
        composite_no_smooth = compute_composite_regime(vol_regime, trend_regime, cycle_regime, config_no_smooth)
        composite_smooth = compute_composite_regime(vol_regime, trend_regime, cycle_regime, config_smooth)
        
        # Smoothed should have lower variance
        assert composite_smooth.std() < composite_no_smooth.std()


class TestDeterminism:
    """Test that all regime functions are deterministic"""
    
    def test_volatility_deterministic(self):
        """
        TEST 5: Volatility classification is deterministic
        """
        dates = create_test_data(100)
        prices = pd.Series(100 + np.random.RandomState(42).randn(100) * 5, index=dates)
        
        config = RegimeConfig()
        
        vol1 = classify_volatility(prices, config)
        vol2 = classify_volatility(prices, config)
        
        pd.testing.assert_series_equal(vol1, vol2)
    
    def test_trend_deterministic(self):
        """
        TEST: Trend classification is deterministic
        """
        dates = create_test_data(100)
        prices = pd.Series(range(100, 200), index=dates)
        
        config = RegimeConfig()
        
        trend1 = classify_trend(prices, config)
        trend2 = classify_trend(prices, config)
        
        pd.testing.assert_series_equal(trend1, trend2)
    
    def test_composite_deterministic(self):
        """
        TEST 6: Composite regime is deterministic
        """
        dates = create_test_data(50)
        
        vol_regime = pd.Series([1] * 50, index=dates)
        trend_regime = pd.Series([1] * 50, index=dates)
        cycle_regime = pd.Series([1] * 50, index=dates)
        
        config = RegimeConfig()
        
        composite1 = compute_composite_regime(vol_regime, trend_regime, cycle_regime, config)
        composite2 = compute_composite_regime(vol_regime, trend_regime, cycle_regime, config)
        
        pd.testing.assert_series_equal(composite1, composite2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


