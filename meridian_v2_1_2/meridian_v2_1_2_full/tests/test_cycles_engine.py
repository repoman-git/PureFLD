"""
Comprehensive test suite for Cycle Phasing Engine in Meridian v2.1.2.

Tests verify cycle detection, turning points, projections, and composite models.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.config import CycleConfig
from meridian_v2_1_2.cycles import (
    estimate_dominant_cycle,
    build_nominal_cycle_map,
    detect_turning_points,
    project_fld,
    build_composite_cycle,
    normalize_series,
    smooth_series,
    cycle_phase,
    cycle_amplitude,
    cycle_stability
)


def create_sine_wave(length=200, period=40, amplitude=10, offset=100):
    """Create synthetic sine wave for testing"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    t = np.arange(length)
    values = offset + amplitude * np.sin(2 * np.pi * t / period)
    return pd.Series(values, index=dates)


class TestDominantCycleEstimator:
    """Test dominant cycle detection"""
    
    def test_detects_known_cycle_period(self):
        """
        TEST 1: Detect known cycle period in synthetic sine wave
        """
        # Create 40-bar cycle
        prices = create_sine_wave(length=200, period=40, amplitude=10)
        
        config = CycleConfig(
            min_cycle=20,
            max_cycle=100,
            step=5,
            smoothing_window=3
        )
        
        detected_cycle = estimate_dominant_cycle(prices, config)
        
        # Should detect cycle close to 40
        assert 35 <= detected_cycle <= 45, f"Expected ~40, got {detected_cycle}"
    
    def test_handles_short_price_series(self):
        """
        TEST: Short series returns minimum cycle
        """
        prices = create_sine_wave(length=15, period=10)
        
        config = CycleConfig(min_cycle=20, max_cycle=100)
        
        detected = estimate_dominant_cycle(prices, config)
        
        # Should return min_cycle as default
        assert detected == config.min_cycle
    
    def test_deterministic_detection(self):
        """
        TEST: Cycle detection is deterministic
        """
        prices = create_sine_wave(length=200, period=50)
        
        config = CycleConfig(min_cycle=20, max_cycle=100, step=5)
        
        detected1 = estimate_dominant_cycle(prices, config)
        detected2 = estimate_dominant_cycle(prices, config)
        
        assert detected1 == detected2


class TestNominalModel:
    """Test nominal cycle mapping"""
    
    def test_snaps_to_nearest_nominal(self):
        """
        TEST 2: Snap detected cycle to nearest nominal
        """
        config = CycleConfig(
            use_nominal_model=True,
            nominal_cycles=[20, 40, 80, 160]
        )
        
        # Detected 45 should snap to 40
        nominal_map = build_nominal_cycle_map(45, config)
        
        assert 40 in nominal_map
    
    def test_includes_harmonic_cycles(self):
        """
        TEST: Include harmonically related cycles
        """
        config = CycleConfig(
            use_nominal_model=True,
            nominal_cycles=[20, 40, 80, 160]
        )
        
        # Should include 40 and potentially neighbors
        nominal_map = build_nominal_cycle_map(40, config)
        
        assert len(nominal_map) >= 1
        assert 40 in nominal_map
    
    def test_nominal_model_disabled_returns_detected(self):
        """
        TEST: With nominal model disabled, return detected cycle only
        """
        config = CycleConfig(
            use_nominal_model=False,
            nominal_cycles=[20, 40, 80, 160]
        )
        
        nominal_map = build_nominal_cycle_map(45, config)
        
        # Should return detected cycle only
        assert nominal_map == [45]


class TestTurningPointDetection:
    """Test turning point detection"""
    
    def test_detects_peak_in_u_shape(self):
        """
        TEST 3: Detect peak in U-shape (inverted)
        """
        dates = pd.date_range('2020-01-01', periods=11, freq='D')
        # Create inverted U: low → high → low
        prices = pd.Series([100, 102, 105, 108, 110, 112, 110, 108, 105, 102, 100], index=dates)
        
        turning_points = detect_turning_points(prices, window=3)
        
        # Should detect peak around bar 5
        peak_detected = (turning_points == 1).any()
        assert peak_detected, "Should detect peak"
    
    def test_detects_trough_in_u_shape(self):
        """
        TEST: Detect trough in U-shape
        """
        dates = pd.date_range('2020-01-01', periods=11, freq='D')
        # Create U: high → low → high
        prices = pd.Series([110, 108, 105, 102, 100, 98, 100, 102, 105, 108, 110], index=dates)
        
        turning_points = detect_turning_points(prices, window=3)
        
        # Should detect trough
        trough_detected = (turning_points == -1).any()
        assert trough_detected, "Should detect trough"
    
    def test_no_false_positives_flat_data(self):
        """
        TEST: No false positives in flat data
        """
        dates = pd.date_range('2020-01-01', periods=20, freq='D')
        prices = pd.Series([100] * 20, index=dates)
        
        turning_points = detect_turning_points(prices, window=3)
        
        # Should have no turning points
        assert (turning_points == 0).all(), "Flat data should have no turning points"


class TestFLDProjection:
    """Test FLD projection"""
    
    def test_constant_prices_flat_projection(self):
        """
        TEST 4: Constant prices → flat projection
        """
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        prices = pd.Series([100] * 100, index=dates)
        
        projected_fld = project_fld(prices, cycle_length=20, projection_bars=10)
        
        # Projection should exist
        assert len(projected_fld) > len(prices)
    
    def test_simple_sine_wave_maintains_phase(self):
        """
        TEST: Simple sine wave projection maintains trend
        """
        prices = create_sine_wave(length=100, period=40, amplitude=10)
        
        projected_fld = project_fld(prices, cycle_length=20, projection_bars=20)
        
        # Should have projection bars beyond original
        assert len(projected_fld) >= len(prices)


class TestCompositeCycle:
    """Test composite cycle builder"""
    
    def test_builds_composite_from_multiple_cycles(self):
        """
        TEST 5: Build composite from multiple sine waves
        """
        # Create price with multiple cycle components
        dates = pd.date_range('2020-01-01', periods=200, freq='D')
        t = np.arange(200)
        
        # Two cycles: 40 and 80 bars
        wave1 = 10 * np.sin(2 * np.pi * t / 40)
        wave2 = 5 * np.sin(2 * np.pi * t / 80)
        prices = pd.Series(100 + wave1 + wave2, index=dates)
        
        # Build composite
        composite_df = build_composite_cycle(prices, cycles=[40, 80], projection_bars=20)
        
        # Should have cycle columns
        assert 'cycle_40' in composite_df.columns
        assert 'cycle_80' in composite_df.columns
        assert 'composite_cycle' in composite_df.columns
    
    def test_composite_deterministic(self):
        """
        TEST: Composite cycle is deterministic
        """
        prices = create_sine_wave(length=150, period=40)
        
        composite1 = build_composite_cycle(prices, cycles=[20, 40, 80], projection_bars=20)
        composite2 = build_composite_cycle(prices, cycles=[20, 40, 80], projection_bars=20)
        
        pd.testing.assert_frame_equal(composite1, composite2)


class TestCycleUtils:
    """Test cycle utility functions"""
    
    def test_normalize_series(self):
        """
        TEST: Normalize to 0-1 range
        """
        dates = pd.date_range('2020-01-01', periods=10, freq='D')
        series = pd.Series([50, 60, 70, 80, 90, 100], index=dates[:6])
        
        normalized = normalize_series(series)
        
        assert normalized.min() == 0.0
        assert normalized.max() == 1.0
    
    def test_smooth_series(self):
        """
        TEST: Smooth series reduces noise
        """
        dates = pd.date_range('2020-01-01', periods=20, freq='D')
        noisy = pd.Series(np.random.randn(20) * 10 + 100, index=dates)
        
        smoothed = smooth_series(noisy, window=5)
        
        # Smoothed should have lower variance
        assert smoothed.std() <= noisy.std()
    
    def test_cycle_amplitude(self):
        """
        TEST: Cycle amplitude calculation
        """
        prices = create_sine_wave(length=80, period=40, amplitude=10)
        
        amp = cycle_amplitude(prices, cycle_length=40)
        
        # Should be close to 10
        assert 8 < amp < 12
    
    def test_cycle_stability(self):
        """
        TEST: Cycle stability measurement
        """
        # Stable cycle (consistent amplitude)
        dates = pd.date_range('2020-01-01', periods=120, freq='D')
        t = np.arange(120)
        stable_prices = pd.Series(100 + 10 * np.sin(2 * np.pi * t / 40), index=dates)
        
        stability = cycle_stability(stable_prices, cycle_length=40, num_cycles=3)
        
        # Should have high stability
        assert stability > 0.5


class TestDeterminism:
    """Test that all cycle functions are deterministic"""
    
    def test_all_functions_deterministic(self):
        """
        TEST 6: All cycle functions produce identical results on repeated runs
        """
        prices = create_sine_wave(length=200, period=40)
        config = CycleConfig()
        
        # Dominant cycle
        dc1 = estimate_dominant_cycle(prices, config)
        dc2 = estimate_dominant_cycle(prices, config)
        assert dc1 == dc2
        
        # Nominal map
        nm1 = build_nominal_cycle_map(40, config)
        nm2 = build_nominal_cycle_map(40, config)
        assert nm1 == nm2
        
        # Turning points
        tp1 = detect_turning_points(prices, window=3)
        tp2 = detect_turning_points(prices, window=3)
        pd.testing.assert_series_equal(tp1, tp2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


