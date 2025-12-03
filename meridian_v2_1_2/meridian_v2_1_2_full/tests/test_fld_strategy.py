"""
Comprehensive test suite for FLD Strategy behavior in Meridian v2.1.2.

Tests verify FLD crossover detection, signal generation, and position management.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
from meridian_v2_1_2.strategy import FLDStrategy, StrategyConfig
from meridian_v2_1_2.fld_engine import compute_fld


def create_test_data(length=10):
    """Create synthetic test data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return dates


class TestFLDOnlySignals:
    """Test FLD-only signals with no filters enabled"""
    
    def test_single_long_crossing_enters_and_holds(self):
        """
        TEST A1: Single long crossing → should enter and hold
        
        Given:
            - Price crosses above FLD once
            - No filters enabled
        
        Expect:
            - Enter long on crossing
            - Hold long until opposite signal
        """
        dates = create_test_data(10)
        
        # Price crosses above FLD on bar 3
        prices = pd.Series([95, 95, 95, 105, 105, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(use_tdom=False, use_cot=False, allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Should enter long on bar 3
        assert signals.loc[dates[3], 'signal'] == 1, "Should signal long on crossing"
        assert signals.loc[dates[3], 'position'] == 1, "Should go long"
        
        # Should hold long for remaining bars
        for i in range(4, 10):
            assert signals.loc[dates[i], 'position'] == 1, f"Should stay long at bar {i}"
    
    def test_single_short_crossing_enters_and_holds(self):
        """
        TEST A2: Single short crossing → should enter and hold
        """
        dates = create_test_data(10)
        
        # Price crosses below FLD on bar 3
        prices = pd.Series([105, 105, 105, 95, 95, 95, 95, 95, 95, 95], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Should enter short on bar 3
        assert signals.loc[dates[3], 'signal'] == -1, "Should signal short on crossing"
        assert signals.loc[dates[3], 'position'] == -1, "Should go short"
        
        # Should hold short
        for i in range(4, 10):
            assert signals.loc[dates[i], 'position'] == -1, f"Should stay short at bar {i}"
    
    def test_long_short_long_short_sequence(self):
        """
        TEST A3: Long → Short → Long → Short sequence
        
        Verify multiple crossings handled correctly
        """
        dates = create_test_data(16)
        
        # Alternating crossings
        prices = pd.Series([
            95, 95, 105,  # Cross up bar 2
            105, 105, 95,  # Cross down bar 5
            95, 95, 105,  # Cross up bar 8
            105, 105, 95,  # Cross down bar 11
            95, 95, 95, 95
        ], index=dates)
        fld = pd.Series([100] * 16, index=dates)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Bar 2: cross up → long
        assert signals.loc[dates[2], 'signal'] == 1
        assert signals.loc[dates[2], 'position'] == 1
        assert signals.loc[dates[3], 'position'] == 1
        assert signals.loc[dates[4], 'position'] == 1
        
        # Bar 5: cross down → short
        assert signals.loc[dates[5], 'signal'] == -1
        assert signals.loc[dates[5], 'position'] == -1
        assert signals.loc[dates[6], 'position'] == -1
        assert signals.loc[dates[7], 'position'] == -1
        
        # Bar 8: cross up → long
        assert signals.loc[dates[8], 'signal'] == 1
        assert signals.loc[dates[8], 'position'] == 1
        assert signals.loc[dates[9], 'position'] == 1
        assert signals.loc[dates[10], 'position'] == 1
        
        # Bar 11: cross down → short
        assert signals.loc[dates[11], 'signal'] == -1
        assert signals.loc[dates[11], 'position'] == -1
    
    def test_no_duplicate_entries_when_already_long(self):
        """
        TEST A4: No duplicate entries (should not re-enter when already long)
        
        Price stays above FLD → no new signals
        """
        dates = create_test_data(10)
        
        # Price crosses up once, then stays above
        prices = pd.Series([95, 95, 105, 106, 107, 108, 109, 110, 111, 112], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig()
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Only one signal at bar 2
        assert signals.loc[dates[2], 'signal'] == 1
        
        # No additional signals while above
        for i in range(3, 10):
            assert signals.loc[dates[i], 'signal'] == 0, f"Should not signal again at bar {i}"
            assert signals.loc[dates[i], 'position'] == 1, f"Should still be long at bar {i}"
    
    def test_no_phantom_flips_without_crossing(self):
        """
        TEST A5: No phantom flips (should not flip without a crossing)
        """
        dates = create_test_data(10)
        
        # Price stays below FLD entire time
        prices = pd.Series([95, 94, 93, 92, 91, 90, 89, 88, 87, 86], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Should stay flat (no crossings)
        assert (signals['signal'] == 0).all(), "Should have no signals"
        assert (signals['position'] == 0).all(), "Should stay flat"


class TestMixedCrossings:
    """Test FLD with mixed crossings and synthetic datasets"""
    
    def test_fld_ahead_of_price_deterministic_signals(self):
        """
        TEST B1: FLD ahead of price should cause deterministic signals
        """
        dates = create_test_data(15)
        
        # Create trending price
        prices = pd.Series(range(100, 115), index=dates)
        
        # Compute FLD (will be ahead due to displacement)
        fld = compute_fld(prices, cycle_length=3, displacement=2)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        # Run twice - should be identical
        signals1 = strategy.generate_signals(prices, fld)
        signals2 = strategy.generate_signals(prices, fld)
        
        pd.testing.assert_frame_equal(signals1, signals2)
    
    def test_crossings_only_when_price_crosses_fld(self):
        """
        TEST B2: Verify crossings occur only when price crosses FLD line
        """
        dates = create_test_data(10)
        
        # Explicit crossing pattern
        prices = pd.Series([95, 96, 104, 103, 104, 96, 95, 104, 105, 106], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Bar 2: 96→104 crosses up
        assert signals.loc[dates[2], 'signal'] == 1
        
        # Bar 5: 104→96 crosses down
        assert signals.loc[dates[5], 'signal'] == -1
        
        # Bar 7: 95→104 crosses up
        assert signals.loc[dates[7], 'signal'] == 1
        
        # Other bars should have no signals
        non_signal_bars = [0, 1, 3, 4, 6, 8, 9]
        for i in non_signal_bars:
            assert signals.loc[dates[i], 'signal'] == 0, f"Bar {i} should have no signal"
    
    def test_allow_shorts_false_blocks_shorts(self):
        """
        TEST B3: Verify strategy respects allow_shorts config
        """
        dates = create_test_data(10)
        
        # Price crosses down
        prices = pd.Series([105, 105, 95, 95, 95, 95, 95, 95, 95, 95], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(allow_shorts=False)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Short signal should be blocked
        assert signals.loc[dates[2], 'signal'] == 0, "Short signal should be blocked"
        assert (signals['position'] == 0).all(), "Should stay flat (no shorts allowed)"


class TestEntryExitTransitions:
    """Test entry/exit transition behavior"""
    
    def test_flat_to_long_transition(self):
        """
        TEST C1: flat → long transition
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig()
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        assert signals.loc[dates[0], 'position'] == 0, "Start flat"
        assert signals.loc[dates[1], 'position'] == 0, "Stay flat"
        assert signals.loc[dates[2], 'position'] == 1, "Go long"
        assert signals.loc[dates[3], 'position'] == 1, "Stay long"
    
    def test_long_to_flat_to_short_transition(self):
        """
        TEST C2: long → flat → short transition
        
        Note: Strategy goes directly long->short, no flat in between
        """
        dates = create_test_data(8)
        
        prices = pd.Series([95, 95, 105, 105, 105, 95, 95, 95], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Start flat
        assert signals.loc[dates[0], 'position'] == 0
        assert signals.loc[dates[1], 'position'] == 0
        
        # Go long
        assert signals.loc[dates[2], 'position'] == 1
        assert signals.loc[dates[3], 'position'] == 1
        assert signals.loc[dates[4], 'position'] == 1
        
        # Flip to short (direct transition)
        assert signals.loc[dates[5], 'position'] == -1
        assert signals.loc[dates[6], 'position'] == -1
    
    def test_short_to_flat_to_long_transition(self):
        """
        TEST C3: short → flat → long transition
        """
        dates = create_test_data(8)
        
        prices = pd.Series([105, 105, 95, 95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Start flat, go short
        assert signals.loc[dates[2], 'position'] == -1
        
        # Flip to long
        assert signals.loc[dates[5], 'position'] == 1


class TestContractsConfig:
    """Test respect for config.contracts parameter"""
    
    def test_contracts_equals_1_gives_unit_position(self):
        """
        TEST D1: contracts=1 → position should be ±1
        """
        dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(contracts=1)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        assert signals.loc[dates[2], 'position'] == 1
        assert signals.loc[dates[3], 'position'] == 1
    
    def test_contracts_equals_3_gives_triple_position(self):
        """
        TEST D2: contracts=3 → position should be ±3
        """
        dates = create_test_data(8)
        
        prices = pd.Series([95, 95, 105, 105, 105, 95, 95, 95], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig(contracts=3, allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Long position should be exactly +3
        assert signals.loc[dates[2], 'position'] == 3, "Long position should be +3"
        assert signals.loc[dates[3], 'position'] == 3, "Should stay +3"
        
        # Short position should be exactly -3
        assert signals.loc[dates[5], 'position'] == -3, "Short position should be -3"
        assert signals.loc[dates[6], 'position'] == -3, "Should stay -3"
    
    def test_contracts_5_never_other_values(self):
        """
        TEST D3: contracts=5 → position should only be 0, +5, or -5, never other values
        """
        dates = create_test_data(12)
        
        prices = pd.Series([95, 95, 105, 105, 95, 95, 105, 105, 95, 95, 105, 105], index=dates)
        fld = pd.Series([100] * 12, index=dates)
        
        config = StrategyConfig(contracts=5, allow_shorts=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # All positions should be in {0, +5, -5}
        valid_positions = {0, 5, -5}
        for pos in signals['position']:
            assert pos in valid_positions, f"Position {pos} not in valid set {valid_positions}"


class TestMissingFLDValues:
    """Test behavior with missing/NaN FLD values"""
    
    def test_nan_fld_values_no_exceptions(self):
        """
        TEST E1: When FLD has NaN values, strategy should not crash
        """
        dates = create_test_data(10)
        
        prices = pd.Series(range(100, 110), index=dates)
        
        # FLD with NaNs at start (realistic from displacement)
        fld = pd.Series([np.nan, np.nan, 102, 103, 104, 105, 106, 107, 108, 109], index=dates)
        
        config = StrategyConfig()
        strategy = FLDStrategy(config)
        
        # Should not crash
        signals = strategy.generate_signals(prices, fld)
        
        assert len(signals) == len(prices)
    
    def test_no_entries_until_fld_valid(self):
        """
        TEST E2: Should NOT enter until FLD and crossings are valid
        """
        dates = create_test_data(10)
        
        # Price crosses up at bar 3
        prices = pd.Series([95, 95, 95, 105, 105, 105, 105, 105, 105, 105], index=dates)
        
        # FLD has NaN until bar 3
        fld = pd.Series([np.nan, np.nan, np.nan, 100, 100, 100, 100, 100, 100, 100], index=dates)
        
        config = StrategyConfig()
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld)
        
        # Should not enter on bars 0-2 (FLD is NaN)
        assert signals.loc[dates[0], 'position'] == 0
        assert signals.loc[dates[1], 'position'] == 0
        assert signals.loc[dates[2], 'position'] == 0
        
        # Bar 3: FLD is valid, but need to wait for actual crossing
        # Crossing detection needs previous bar's FLD to be valid
    
    def test_displacement_greater_than_cycle_length(self):
        """
        TEST E3: displacement > cycle_length → early bars NaN
        """
        dates = create_test_data(20)
        
        prices = pd.Series(range(100, 120), index=dates)
        
        # Large displacement causes many NaN bars
        fld = compute_fld(prices, cycle_length=3, displacement=10)
        
        config = StrategyConfig()
        strategy = FLDStrategy(config)
        
        # Should not crash
        signals = strategy.generate_signals(prices, fld)
        
        assert len(signals) == len(prices)
        
        # Early bars should stay flat (no valid FLD to cross)
        nan_count = fld.isna().sum()
        assert nan_count > 0, "Should have some NaN FLD values"


class TestDeterminism:
    """Test that strategy behavior is fully deterministic"""
    
    def test_multiple_runs_identical_results(self):
        """
        TEST: Multiple runs with same inputs produce identical signals
        """
        dates = create_test_data(20)
        
        prices = pd.Series([95, 95, 105, 105, 95, 95, 105, 105, 95, 95,
                           105, 105, 95, 95, 105, 105, 95, 95, 105, 105], index=dates)
        fld = pd.Series([100] * 20, index=dates)
        
        config = StrategyConfig(allow_shorts=True, contracts=3)
        strategy = FLDStrategy(config)
        
        # Run 5 times
        results = [strategy.generate_signals(prices, fld) for _ in range(5)]
        
        # All should be identical
        for i in range(1, 5):
            pd.testing.assert_frame_equal(results[0], results[i])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

