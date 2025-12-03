"""
Comprehensive test suite for COT (Commitment of Traders) filtering in Meridian v2.1.2.

Tests verify that COT sentiment data correctly gates FLD crossover entries according to threshold rules.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
from meridian_v2_1_2.strategy import FLDStrategy, StrategyConfig


def create_test_data(length=10):
    """Create synthetic test data with consistent index"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    prices = pd.Series(range(100, 100 + length), index=dates, name='price')
    fld = pd.Series(range(98, 98 + length), index=dates, name='fld')
    return prices, fld, dates


class TestCOTFilterBlocking:
    """Test COT filter blocks entries based on threshold rules"""
    
    def test_cot_blocks_long_entry_below_threshold(self):
        """
        TEST 1: COT filter blocks long entries when COT < long_threshold
        
        Given:
            - FLD crossover signal (price crosses above FLD)
            - COT value below long threshold (-0.5 < 0.0)
        
        Expect:
            - Long entry is blocked
            - Position remains 0
            - No exceptions thrown
        """
        prices, fld, dates = create_test_data(5)
        
        # Create clear crossover: price crosses above FLD on bar 2
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT below threshold (negative sentiment)
        cot_series = pd.Series([-0.5, -0.5, -0.5, -0.5, -0.5], index=dates)
        
        # Configure strategy with COT filtering
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,  # Require COT >= 0 for longs
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        # Generate signals
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Verify long entry is blocked
        assert signals.loc[dates[2], 'signal'] == 0, "Long signal should be blocked"
        assert signals.loc[dates[2], 'position'] == 0, "Position should remain flat"
        assert (signals['position'] == 0).all(), "Should stay flat entire time"
    
    def test_cot_allows_long_entry_above_threshold(self):
        """
        TEST 2: COT filter allows long entries when COT >= long_threshold
        
        Given:
            - FLD crossover signal (price crosses above FLD)
            - COT value above long threshold (0.5 >= 0.0)
        
        Expect:
            - Long entry is allowed
            - Position goes to +1
            - Position stays long
        """
        prices, fld, dates = create_test_data(5)
        
        # Create clear crossover on bar 2
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT above threshold (positive sentiment)
        cot_series = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Verify long entry is allowed
        assert signals.loc[dates[2], 'signal'] == 1, "Long signal should fire"
        assert signals.loc[dates[2], 'position'] == 1, "Position should go long"
        assert signals.loc[dates[3], 'position'] == 1, "Position should stay long"
        assert signals.loc[dates[4], 'position'] == 1, "Position should stay long"
    
    def test_cot_blocks_short_entry_above_threshold(self):
        """
        TEST 3: COT filter blocks short entries when COT > short_threshold
        
        Given:
            - FLD crossover signal (price crosses below FLD)
            - COT shows net-long bias (0.5 > 0.0)
        
        Expect:
            - Short entry is blocked
            - Position remains flat (0)
        """
        prices, fld, dates = create_test_data(5)
        
        # Create clear crossover down on bar 2
        prices = pd.Series([105, 105, 95, 95, 95], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT above threshold (net-long bias, should block shorts)
        cot_series = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_short_threshold=0.0,  # Require COT <= 0 for shorts
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Verify short entry is blocked
        assert signals.loc[dates[2], 'signal'] == 0, "Short signal should be blocked"
        assert signals.loc[dates[2], 'position'] == 0, "Position should remain flat"
        assert (signals['position'] == 0).all(), "Should stay flat entire time"
    
    def test_cot_allows_short_entry_below_threshold(self):
        """
        TEST: COT filter allows short entries when COT <= short_threshold
        """
        prices, fld, dates = create_test_data(5)
        
        # Create clear crossover down on bar 2
        prices = pd.Series([105, 105, 95, 95, 95], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT below threshold (net-short bias, should allow shorts)
        cot_series = pd.Series([-0.5, -0.5, -0.5, -0.5, -0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_short_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Verify short entry is allowed
        assert signals.loc[dates[2], 'signal'] == -1, "Short signal should fire"
        assert signals.loc[dates[2], 'position'] == -1, "Position should go short"
        assert signals.loc[dates[3], 'position'] == -1, "Position should stay short"


class TestCOTMissingData:
    """Test behavior when COT data is missing or None"""
    
    def test_missing_cot_no_crash_when_filter_enabled(self):
        """
        TEST 4: Missing COT (None) produces no crash
        
        Given:
            - use_cot_filter = True
            - cot_series = None
        
        Expect:
            - Strategy does not crash
            - Strategy behaves as if filter is off
            - Entries are allowed based on FLD alone
        """
        prices, fld, dates = create_test_data(5)
        
        # Create crossover
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT is None
        cot_series = None
        
        config = StrategyConfig(
            use_cot=True,  # Filter enabled but no data
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        # Should not crash
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Entry should be allowed (filter effectively disabled)
        assert signals.loc[dates[2], 'signal'] == 1, "Long signal should fire when COT is None"
        assert signals.loc[dates[2], 'position'] == 1, "Position should go long"
    
    def test_cot_disabled_allows_all_entries(self):
        """
        TEST: When use_cot=False, all FLD signals should be allowed regardless of COT values
        """
        prices, fld, dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT very negative (would block if enabled)
        cot_series = pd.Series([-999, -999, -999, -999, -999], index=dates)
        
        config = StrategyConfig(
            use_cot=False,  # Filter disabled
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Entry should be allowed despite bad COT
        assert signals.loc[dates[2], 'signal'] == 1, "Signal should fire with COT disabled"
        assert signals.loc[dates[2], 'position'] == 1, "Position should go long"


class TestCOTMultiBarScenarios:
    """Test COT filtering over multiple bars with changing values"""
    
    def test_cot_mixed_signals_over_time(self):
        """
        TEST 5: COT filter with mixed signals over time
        
        Construct multi-bar scenario:
            - Bar 0: Crossover + bad COT → blocked
            - Bar 1: No crossover + good COT → no entry (need both)
            - Bar 2: Crossover + good COT → allowed
            - Bar 3: Crossover + bad COT → blocked
        
        Expect:
            - Positions respect gating per-bar
            - No delayed state bleed
        """
        dates = pd.date_range('2020-01-01', periods=6, freq='D')
        
        # Create multiple crossovers
        prices = pd.Series([95, 105, 105, 95, 95, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100, 100], index=dates)
        
        # COT pattern: bad, bad, good, good, bad, good
        cot_series = pd.Series([-0.5, -0.5, 0.5, 0.5, -0.5, 0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,
            cot_short_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Bar 0: Cross up but bad COT → blocked
        assert signals.loc[dates[0], 'signal'] == 0, "Bar 0: should be blocked by COT"
        
        # Bar 1: No cross, good COT → no signal
        assert signals.loc[dates[1], 'signal'] == 0, "Bar 1: no crossover"
        
        # Bar 2: No cross (already above)
        assert signals.loc[dates[2], 'signal'] == 0, "Bar 2: no crossover"
        
        # Bar 3: Cross down, good COT (but short blocked by good COT)
        assert signals.loc[dates[3], 'signal'] == 0, "Bar 3: short blocked by positive COT"
        
        # Bar 4: No cross (already below)
        assert signals.loc[dates[4], 'signal'] == 0, "Bar 4: no crossover"
        
        # Bar 5: Cross up, good COT → allowed
        assert signals.loc[dates[5], 'signal'] == 1, "Bar 5: should fire with good COT"
        assert signals.loc[dates[5], 'position'] == 1, "Bar 5: should go long"
    
    def test_cot_changing_thresholds(self):
        """
        TEST: Verify threshold logic with different threshold values
        """
        prices, fld, dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # COT = 0.3 (positive but moderate)
        cot_series = pd.Series([0.3, 0.3, 0.3, 0.3, 0.3], index=dates)
        
        # Test 1: Low threshold (0.0) - should allow
        config1 = StrategyConfig(use_cot=True, cot_long_threshold=0.0)
        strategy1 = FLDStrategy(config1)
        signals1 = strategy1.generate_signals(prices, fld, cot_series=cot_series)
        assert signals1.loc[dates[2], 'position'] == 1, "Should allow with threshold=0.0"
        
        # Test 2: High threshold (0.5) - should block
        config2 = StrategyConfig(use_cot=True, cot_long_threshold=0.5)
        strategy2 = FLDStrategy(config2)
        signals2 = strategy2.generate_signals(prices, fld, cot_series=cot_series)
        assert signals2.loc[dates[2], 'position'] == 0, "Should block with threshold=0.5"


class TestCOTAndFLDCombined:
    """Test that COT and FLD crossovers work together with AND logic"""
    
    def test_good_cot_no_crossing_no_entry(self):
        """
        TEST 6a: Strategy respects both COT AND crossings
        
        If FLD produces no crossing, even good COT should not enter
        
        Expect:
            - No entry without crossover, regardless of COT
        """
        prices, fld, dates = create_test_data(5)
        
        # No crossover: prices stay above FLD
        prices = pd.Series([105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # Good COT (would allow if there was a signal)
        cot_series = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # No entry should occur (no crossover)
        assert (signals['signal'] == 0).all(), "No signals without crossover"
        assert (signals['position'] == 0).all(), "Should stay flat"
    
    def test_bad_cot_with_crossing_no_entry(self):
        """
        TEST 6b: If FLD crossing occurs but bad COT → should not enter
        
        Confirms AND-logic, not OR-logic
        """
        prices, fld, dates = create_test_data(5)
        
        # Clear crossover
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        
        # Bad COT (below threshold)
        cot_series = pd.Series([-0.5, -0.5, -0.5, -0.5, -0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Entry should be blocked despite crossover
        assert signals.loc[dates[2], 'signal'] == 0, "Should be blocked by bad COT"
        assert (signals['position'] == 0).all(), "Should stay flat"
    
    def test_good_cot_with_crossing_enters(self):
        """
        TEST 6c: Both crossover AND good COT → entry allowed
        
        This is the only case where entry should occur
        """
        prices, fld, dates = create_test_data(5)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates)
        fld = pd.Series([100, 100, 100, 100, 100], index=dates)
        cot_series = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # Both conditions met → entry allowed
        assert signals.loc[dates[2], 'signal'] == 1, "Should enter with both conditions"
        assert signals.loc[dates[2], 'position'] == 1, "Should go long"


class TestCOTIndexAlignment:
    """Test that COT index must align with price index"""
    
    def test_mismatched_cot_index_raises_error(self):
        """
        TEST 7: Ensure correct alignment of indices
        
        COT index must align 1:1 with price index.
        Mismatched indices should raise ValueError with clear message.
        """
        prices, fld, dates = create_test_data(5)
        
        # Create COT with different index
        wrong_dates = pd.date_range('2020-02-01', periods=5, freq='D')
        cot_series = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], index=wrong_dates)
        
        config = StrategyConfig(use_cot=True, cot_long_threshold=0.0)
        strategy = FLDStrategy(config)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="COT series index does not match price series index"):
            strategy.generate_signals(prices, fld, cot_series=cot_series)
    
    def test_matching_cot_index_no_error(self):
        """
        TEST: Properly aligned COT index should work without errors
        """
        prices, fld, dates = create_test_data(5)
        
        # Create COT with matching index
        cot_series = pd.Series([0.5, 0.5, 0.5, 0.5, 0.5], index=dates)
        
        config = StrategyConfig(use_cot=True, cot_long_threshold=0.0)
        strategy = FLDStrategy(config)
        
        # Should not raise any error
        signals = strategy.generate_signals(prices, fld, cot_series=cot_series)
        assert len(signals) == len(prices), "Should return valid signals"
    
    def test_partial_cot_index_raises_error(self):
        """
        TEST: COT with partial overlap should raise error
        """
        prices, fld, dates = create_test_data(5)
        
        # Create COT with only partial dates
        partial_dates = dates[:3]  # Only first 3 dates
        cot_series = pd.Series([0.5, 0.5, 0.5], index=partial_dates)
        
        config = StrategyConfig(use_cot=True, cot_long_threshold=0.0)
        strategy = FLDStrategy(config)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="COT series index does not match price series index"):
            strategy.generate_signals(prices, fld, cot_series=cot_series)


class TestCOTDeterminism:
    """Test that COT filtering is deterministic"""
    
    def test_cot_filtering_is_deterministic(self):
        """
        TEST: Multiple runs with same inputs produce identical results
        """
        prices, fld, dates = create_test_data(10)
        
        prices = pd.Series([95, 95, 105, 105, 95, 95, 105, 105, 95, 95], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        cot_series = pd.Series([0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5], index=dates)
        
        config = StrategyConfig(
            use_cot=True,
            cot_long_threshold=0.0,
            cot_short_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        # Run multiple times
        signals1 = strategy.generate_signals(prices, fld, cot_series=cot_series)
        signals2 = strategy.generate_signals(prices, fld, cot_series=cot_series)
        signals3 = strategy.generate_signals(prices, fld, cot_series=cot_series)
        
        # All runs should be identical
        pd.testing.assert_frame_equal(signals1, signals2)
        pd.testing.assert_frame_equal(signals2, signals3)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

