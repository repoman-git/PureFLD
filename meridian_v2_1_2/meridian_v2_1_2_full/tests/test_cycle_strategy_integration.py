"""
Comprehensive test suite for Cycle-Aware Strategy Integration in Meridian v2.1.2.

Tests verify cycle-based filtering, phase gating, and multi-factor integration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.strategy import FLDStrategy, StrategyConfig
from meridian_v2_1_2.config import CycleStrategyConfig
from meridian_v2_1_2.cycles import compute_cycle_phase_normalized, compute_cycle_score


def create_test_data(length=20):
    """Create synthetic test data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return dates


class TestPhaseRangeFiltering:
    """Test phase range filtering"""
    
    def test_phase_range_allows_signals_in_window(self):
        """
        TEST 1: Phase range filtering - signals allowed in phase window
        
        Only allow phase 0.0-0.33 (trough zone)
        """
        dates = create_test_data(10)
        
        # Price crosses up
        prices = pd.Series([95, 95, 105, 105, 105, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # Cycle phase: in allowed range on bar 2
        cycle_phase = pd.Series([0.1, 0.1, 0.2, 0.5, 0.7, 0.8, 0.9, 0.1, 0.2, 0.3], index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.allowed_phase_ranges = [(0.0, 0.33)]
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, cycle_phase=cycle_phase)
        
        # Bar 2: phase=0.2 (in range) → should allow
        assert signals.loc[dates[2], 'signal'] == 1
    
    def test_phase_range_blocks_signals_outside_window(self):
        """
        TEST: Signals blocked outside phase window
        """
        dates = create_test_data(10)
        
        prices = pd.Series([95, 95, 95, 95, 95, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # Phase at bar 5 is 0.5 (peak, outside allowed range)
        cycle_phase = pd.Series([0.1] * 5 + [0.5] * 5, index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.allowed_phase_ranges = [(0.0, 0.33)]
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, cycle_phase=cycle_phase)
        
        # Bar 5: phase=0.5 (outside range) → should block
        assert signals.loc[dates[5], 'signal'] == 0


class TestAmplitudeFiltering:
    """Test amplitude-based filtering"""
    
    def test_amplitude_above_threshold_allows(self):
        """
        TEST 2: Amplitude > threshold → allow
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 5, index=dates)
        
        # Sufficient amplitude
        cycle_amplitude = pd.Series([15.0] * 5, index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.min_cycle_amplitude = 10.0
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, cycle_amplitude=cycle_amplitude)
        
        # Should allow (amplitude 15 > 10)
        assert signals.loc[dates[2], 'signal'] == 1
    
    def test_amplitude_below_threshold_blocks(self):
        """
        TEST: Amplitude < threshold → block
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 5, index=dates)
        
        # Insufficient amplitude
        cycle_amplitude = pd.Series([5.0] * 5, index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.min_cycle_amplitude = 10.0
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, cycle_amplitude=cycle_amplitude)
        
        # Should block (amplitude 5 < 10)
        assert signals.loc[dates[2], 'signal'] == 0


class TestTurningPointAlignment:
    """Test turning point alignment requirement"""
    
    def test_turning_point_aligned_allows(self):
        """
        TEST 3: Turning point within window → allow
        """
        dates = create_test_data(10)
        
        prices = pd.Series([95, 95, 95, 105, 105, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # Turning point on bar 2 (within 3 bars of signal on bar 3)
        turning_points = pd.Series([0, 0, -1, 0, 0, 0, 0, 0, 0, 0], index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.require_turning_point_alignment = True
        config.cycle_strategy.max_bars_from_turning_point = 3
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, turning_points=turning_points)
        
        # Should allow (turning point on bar 2, signal on bar 3)
        assert signals.loc[dates[3], 'signal'] == 1
    
    def test_no_turning_point_blocks(self):
        """
        TEST: No turning point nearby → block
        """
        dates = create_test_data(10)
        
        prices = pd.Series([95, 95, 95, 95, 95, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # No turning points
        turning_points = pd.Series([0] * 10, index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.require_turning_point_alignment = True
        config.cycle_strategy.max_bars_from_turning_point = 3
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, turning_points=turning_points)
        
        # Should block (no turning points)
        assert signals.loc[dates[5], 'signal'] == 0


class TestCycleScoreThreshold:
    """Test cycle score threshold filtering"""
    
    def test_high_score_allows(self):
        """
        TEST 4: High cycle score → allow
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 5, index=dates)
        
        # High cycle score
        cycle_score = pd.Series([0.8] * 5, index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.min_cycle_score = 0.5
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, cycle_score=cycle_score)
        
        # Should allow (0.8 > 0.5)
        assert signals.loc[dates[2], 'signal'] == 1
    
    def test_low_score_blocks(self):
        """
        TEST: Low cycle score → block
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 5, index=dates)
        
        # Low cycle score
        cycle_score = pd.Series([0.2] * 5, index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.min_cycle_score = 0.5
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(prices, fld, cycle_score=cycle_score)
        
        # Should block (0.2 < 0.5)
        assert signals.loc[dates[2], 'signal'] == 0


class TestMultiFactorIntegration:
    """Test combined cycle + COT + seasonal + FLD filtering"""
    
    def test_all_filters_must_pass(self):
        """
        TEST 6: All filters must pass (AND logic)
        
        Given:
            - FLD crossover: Yes
            - COT: Block
            - Seasonal: Allow
            - Cycle: Allow
        
        Expected: Entry blocked (COT blocks)
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 5, index=dates)
        
        # COT blocks (negative, threshold 0)
        cot = pd.Series([-0.5] * 5, index=dates)
        
        # Seasonal allows
        seasonal = pd.Series([1] * 5, index=dates)
        
        # Cycle allows
        cycle_score = pd.Series([0.8] * 5, index=dates)
        
        config = StrategyConfig()
        config.use_cot = True
        config.cot_long_threshold = 0.0
        config.use_tdom = True
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.min_cycle_score = 0.5
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(
            prices, fld,
            cot_series=cot,
            seasonal_score=seasonal,
            cycle_score=cycle_score
        )
        
        # Should be blocked by COT despite cycle and seasonal allowing
        assert signals.loc[dates[2], 'signal'] == 0
    
    def test_all_filters_pass_allows_entry(self):
        """
        TEST: All filters pass → entry allowed
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 5, index=dates)
        
        # All filters allow
        cot = pd.Series([0.5] * 5, index=dates)
        seasonal = pd.Series([1] * 5, index=dates)
        cycle_score = pd.Series([0.8] * 5, index=dates)
        
        config = StrategyConfig()
        config.use_cot = True
        config.cot_long_threshold = 0.0
        config.use_tdom = True
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.min_cycle_score = 0.5
        
        strategy = FLDStrategy(config)
        signals = strategy.generate_signals(
            prices, fld,
            cot_series=cot,
            seasonal_score=seasonal,
            cycle_score=cycle_score
        )
        
        # Should allow (all filters pass)
        assert signals.loc[dates[2], 'signal'] == 1


class TestDeterminism:
    """Test that cycle-aware strategy is deterministic"""
    
    def test_cycle_filtering_deterministic(self):
        """
        TEST 7: Two runs → identical signals
        """
        dates = create_test_data(20)
        
        prices = pd.Series([95, 95, 105, 105, 95, 95, 105, 105] * 2 + [95, 95, 105, 105], index=dates)
        fld = pd.Series([100] * 20, index=dates)
        
        cycle_phase = pd.Series(np.linspace(0, 1, 20), index=dates)
        cycle_score = pd.Series(np.sin(np.linspace(0, 2*np.pi, 20)), index=dates)
        
        config = StrategyConfig()
        config.cycle_strategy.enable_cycle_filters = True
        config.cycle_strategy.allowed_phase_ranges = [(0.0, 0.5)]
        config.cycle_strategy.min_cycle_score = 0.0
        
        strategy = FLDStrategy(config)
        
        signals1 = strategy.generate_signals(prices, fld, cycle_phase=cycle_phase, cycle_score=cycle_score)
        signals2 = strategy.generate_signals(prices, fld, cycle_phase=cycle_phase, cycle_score=cycle_score)
        
        pd.testing.assert_frame_equal(signals1, signals2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

