"""
Comprehensive test suite for TDOY (Trading Day of Year) and Seasonal Matrix in Meridian v2.1.2.

Tests verify TDOY calculation, seasonal score combination, and strategy integration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
from meridian_v2_1_2.seasonality import (
    compute_tdoy_flags,
    compute_tdom_flags,
    combine_seasonal_flags,
    get_seasonal_regime_label
)
from meridian_v2_1_2.strategy import FLDStrategy, StrategyConfig
from meridian_v2_1_2 import MeridianConfig, run_backtest


class TestTDOYComputation:
    """Test TDOY flag computation"""
    
    def test_tdoy_favourable_days_marked_correctly(self):
        """
        TEST 1: TDOY favourable days marked as +1
        """
        # Jan 1-5 (days 1-5 of year)
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        tdoy = compute_tdoy_flags(dates, favourable=[1, 2, 3], unfavourable=[])
        
        assert tdoy.loc['2020-01-01'] == 1  # Day 1 of year
        assert tdoy.loc['2020-01-02'] == 1  # Day 2 of year
        assert tdoy.loc['2020-01-03'] == 1  # Day 3 of year
        assert tdoy.loc['2020-01-04'] == 0  # Day 4 (neutral)
    
    def test_tdoy_unfavourable_days_marked_correctly(self):
        """
        TEST: TDOY unfavourable days marked as -1
        """
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        tdoy = compute_tdoy_flags(dates, favourable=[], unfavourable=[5, 6, 7])
        
        assert tdoy.loc['2020-01-05'] == -1  # Day 5 of year
        assert tdoy.loc['2020-01-06'] == -1  # Day 6 of year
        assert tdoy.loc['2020-01-07'] == -1  # Day 7 of year
        assert tdoy.loc['2020-01-08'] == 0   # Day 8 (neutral)
    
    def test_tdoy_boundary_values(self):
        """
        TEST 2: TDOY boundary values (1 and 365/366)
        """
        # Test day 1 (Jan 1)
        dates_start = pd.date_range('2020-01-01', '2020-01-03', freq='D')
        tdoy_start = compute_tdoy_flags(dates_start, favourable=[1], unfavourable=[])
        assert tdoy_start.loc['2020-01-01'] == 1
        
        # Test day 366 (leap year, Dec 31)
        dates_end = pd.date_range('2020-12-30', '2021-01-02', freq='D')
        tdoy_end = compute_tdoy_flags(dates_end, favourable=[366], unfavourable=[])
        assert tdoy_end.loc['2020-12-31'] == 1  # Day 366 in leap year
    
    def test_tdoy_mid_year_days(self):
        """
        TEST: TDOY works for mid-year days
        """
        # July 4th is approximately day 186
        dates = pd.date_range('2020-07-01', '2020-07-10', freq='D')
        tdoy = compute_tdoy_flags(dates, favourable=[186], unfavourable=[])
        
        # July 4, 2020 is day 186
        assert tdoy.loc['2020-07-04'] == 1


class TestSeasonalMatrix:
    """Test TDOM + TDOY combined scoring"""
    
    def test_tdom_plus1_tdoy_minus1_equals_0(self):
        """
        TEST 3a: tdom=+1, tdoy=-1 → combined score = 0
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        
        tdom = pd.Series([1, 1, 1, 1, 1], index=dates)
        tdoy = pd.Series([-1, -1, -1, -1, -1], index=dates)
        
        score = combine_seasonal_flags(tdom, tdoy)
        
        assert (score == 0).all(), "tdom+1 + tdoy-1 should equal 0"
    
    def test_tdom_minus1_tdoy_minus1_equals_minus2(self):
        """
        TEST 3b: tdom=-1, tdoy=-1 → combined score = -2 (strong unfavourable)
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        
        tdom = pd.Series([-1, -1, -1, -1, -1], index=dates)
        tdoy = pd.Series([-1, -1, -1, -1, -1], index=dates)
        
        score = combine_seasonal_flags(tdom, tdoy)
        
        assert (score == -2).all(), "Both negative should give -2"
    
    def test_tdom_plus1_tdoy_plus1_equals_plus2(self):
        """
        TEST 3c: tdom=+1, tdoy=+1 → combined score = +2 (strong favourable)
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        
        tdom = pd.Series([1, 1, 1, 1, 1], index=dates)
        tdoy = pd.Series([1, 1, 1, 1, 1], index=dates)
        
        score = combine_seasonal_flags(tdom, tdoy)
        
        assert (score == 2).all(), "Both positive should give +2"
    
    def test_tdom_0_tdoy_plus1_equals_plus1(self):
        """
        TEST 3d: tdom=0, tdoy=+1 → combined score = +1 (mild favourable)
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        
        tdom = pd.Series([0, 0, 0, 0, 0], index=dates)
        tdoy = pd.Series([1, 1, 1, 1, 1], index=dates)
        
        score = combine_seasonal_flags(tdom, tdoy)
        
        assert (score == 1).all(), "Neutral + positive should give +1"
    
    def test_mixed_seasonal_scores(self):
        """
        TEST: Mixed seasonal scores over time
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        
        tdom = pd.Series([1, 0, -1, 1, 0], index=dates)
        tdoy = pd.Series([1, 1, -1, 0, -1], index=dates)
        
        score = combine_seasonal_flags(tdom, tdoy)
        
        assert score.iloc[0] == 2   # 1 + 1
        assert score.iloc[1] == 1   # 0 + 1
        assert score.iloc[2] == -2  # -1 + -1
        assert score.iloc[3] == 1   # 1 + 0
        assert score.iloc[4] == -1  # 0 + -1
    
    def test_tdom_only_returns_tdom(self):
        """
        TEST: If only TDOM provided, return TDOM
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        tdom = pd.Series([1, 0, -1, 1, 0], index=dates)
        
        score = combine_seasonal_flags(tdom=tdom, tdoy=None)
        
        pd.testing.assert_series_equal(score, tdom)
    
    def test_tdoy_only_returns_tdoy(self):
        """
        TEST: If only TDOY provided, return TDOY
        """
        dates = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        tdoy = pd.Series([1, 0, -1, 1, 0], index=dates)
        
        score = combine_seasonal_flags(tdom=None, tdoy=tdoy)
        
        pd.testing.assert_series_equal(score, tdoy)
    
    def test_both_none_raises_error(self):
        """
        TEST: Both None should raise ValueError
        """
        with pytest.raises(ValueError, match="At least one"):
            combine_seasonal_flags(tdom=None, tdoy=None)
    
    def test_mismatched_indices_raises_error(self):
        """
        TEST: Mismatched indices should raise ValueError
        """
        dates1 = pd.date_range('2020-01-01', '2020-01-05', freq='D')
        dates2 = pd.date_range('2020-02-01', '2020-02-05', freq='D')
        
        tdom = pd.Series([1, 0, -1, 1, 0], index=dates1)
        tdoy = pd.Series([1, 0, -1, 1, 0], index=dates2)
        
        with pytest.raises(ValueError, match="indices must match"):
            combine_seasonal_flags(tdom, tdoy)


class TestSeasonalRegimeLabels:
    """Test seasonal regime labeling"""
    
    def test_regime_labels(self):
        """
        TEST: Regime labels are correct
        """
        assert get_seasonal_regime_label(2) == "Strong Favourable"
        assert get_seasonal_regime_label(1) == "Mild Favourable"
        assert get_seasonal_regime_label(0) == "Neutral"
        assert get_seasonal_regime_label(-1) == "Mild Unfavourable"
        assert get_seasonal_regime_label(-2) == "Strong Unfavourable"


class TestStrategySeasonalGating:
    """Test strategy gating based on combined seasonal score"""
    
    def test_strategy_blocks_negative_seasonal_score(self):
        """
        TEST 4: Strategy blocks entries when seasonal_score < 0
        """
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        
        # Price crosses up on bar 3
        prices = pd.Series([95, 95, 95, 105, 105, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # Seasonal score negative on bar 3
        seasonal_score = pd.Series([0, 0, 0, -1, 0, 0, 0, 0, 0, 0], index=dates)
        
        config = StrategyConfig(use_tdom=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, seasonal_score=seasonal_score)
        
        # Entry should be blocked on bar 3
        assert signals.loc[dates[3], 'signal'] == 0, "Should block entry with negative score"
        assert signals.loc[dates[3], 'position'] == 0, "Should stay flat"
    
    def test_strategy_allows_zero_seasonal_score(self):
        """
        TEST: Strategy allows entries when seasonal_score >= 0
        """
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        
        prices = pd.Series([95, 95, 95, 105, 105, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # Seasonal score = 0 (neutral)
        seasonal_score = pd.Series([0] * 10, index=dates)
        
        config = StrategyConfig(use_tdom=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, seasonal_score=seasonal_score)
        
        # Entry should be allowed
        assert signals.loc[dates[3], 'signal'] == 1, "Should allow entry with neutral score"
        assert signals.loc[dates[3], 'position'] == 1, "Should go long"
    
    def test_strategy_allows_positive_seasonal_score(self):
        """
        TEST: Strategy allows entries when seasonal_score > 0
        """
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        
        prices = pd.Series([95, 95, 95, 105, 105, 105, 105, 105, 105, 105], index=dates)
        fld = pd.Series([100] * 10, index=dates)
        
        # Seasonal score = +2 (strong favourable)
        seasonal_score = pd.Series([2] * 10, index=dates)
        
        config = StrategyConfig(use_tdom=True)
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, seasonal_score=seasonal_score)
        
        # Entry should be allowed
        assert signals.loc[dates[3], 'signal'] == 1
        assert signals.loc[dates[3], 'position'] == 1


class TestIntegrationWithFLDAndCOT:
    """Test seasonal matrix integration with FLD and COT"""
    
    def test_fld_cot_seasonal_full_pipeline(self):
        """
        TEST 5: FLD + COT + Seasonal (full pipeline)
        
        Construct scenario with:
        - 12 bars
        - COT alternating above/below threshold
        - Seasonal alternating favourable/unfavourable
        
        Only trades allowed when both gates open
        """
        dates = pd.date_range('2020-01-01', periods=12, freq='D')
        
        # Alternating crossovers
        prices = pd.Series([95, 95, 105, 105, 95, 95, 105, 105, 95, 95, 105, 105], index=dates)
        fld = pd.Series([100] * 12, index=dates)
        
        # COT: alternating good/bad
        cot = pd.Series([0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, -0.5], index=dates)
        
        # Seasonal: alternating favourable/unfavourable
        seasonal = pd.Series([1, 1, -1, -1, 1, 1, -1, -1, 1, 1, -1, -1], index=dates)
        
        config = StrategyConfig(
            use_tdom=True,
            use_cot=True,
            cot_long_threshold=0.0,
            allow_shorts=True
        )
        strategy = FLDStrategy(config)
        
        signals = strategy.generate_signals(prices, fld, cot_series=cot, seasonal_score=seasonal)
        
        # Bar 2: Cross up, but COT bad AND seasonal bad → blocked
        assert signals.loc[dates[2], 'signal'] == 0
        
        # Bar 6: Cross up, COT bad, seasonal bad → blocked
        assert signals.loc[dates[6], 'signal'] == 0
        
        # Bar 10: Cross up, COT bad, seasonal bad → blocked
        assert signals.loc[dates[10], 'signal'] == 0


class TestOrchestratorIntegration:
    """Test orchestrator integration with TDOY"""
    
    def test_orchestrator_computes_tdoy_when_enabled(self):
        """
        TEST: Orchestrator computes TDOY when enabled
        """
        dates = pd.date_range('2020-01-01', periods=10, freq='D')
        prices = pd.Series(range(100, 110), index=dates)
        
        config = MeridianConfig()
        config.seasonality.use_tdoy = True
        config.seasonality.tdoy_favourable = [1, 2, 3]
        
        results = run_backtest(config, prices)
        
        assert results['tdoy'] is not None, "TDOY should be computed"
        assert len(results['tdoy']) == len(prices)
        assert results['tdoy'].loc[dates[0]] == 1  # Jan 1 is day 1
    
    def test_orchestrator_combines_tdom_and_tdoy(self):
        """
        TEST: Orchestrator combines TDOM and TDOY into seasonal_score
        """
        dates = pd.date_range('2020-01-01', periods=10, freq='D')
        prices = pd.Series(range(100, 110), index=dates)
        
        config = MeridianConfig()
        config.seasonality.use_tdom = True
        config.seasonality.favourable_days = [1, 2, 3]
        config.seasonality.use_tdoy = True
        config.seasonality.tdoy_favourable = [1, 2, 3]
        
        results = run_backtest(config, prices)
        
        assert results['seasonal_score'] is not None
        # Jan 1 is day 1 of month AND day 1 of year → both +1 → score = +2
        assert results['seasonal_score'].loc[dates[0]] == 2


class TestDeterminism:
    """Test deterministic behavior of TDOY and seasonal matrix"""
    
    def test_tdoy_deterministic(self):
        """
        TEST 6: TDOY computation is deterministic
        """
        dates = pd.date_range('2020-01-01', periods=20, freq='D')
        
        tdoy1 = compute_tdoy_flags(dates, favourable=[1, 5, 10], unfavourable=[15, 20])
        tdoy2 = compute_tdoy_flags(dates, favourable=[1, 5, 10], unfavourable=[15, 20])
        
        pd.testing.assert_series_equal(tdoy1, tdoy2)
    
    def test_seasonal_matrix_deterministic(self):
        """
        TEST: Seasonal matrix combination is deterministic
        """
        dates = pd.date_range('2020-01-01', periods=20, freq='D')
        
        tdom = compute_tdom_flags(dates, [1, 2, 3], [15, 16])
        tdoy = compute_tdoy_flags(dates, [1, 5, 10], [20, 25])
        
        score1 = combine_seasonal_flags(tdom, tdoy)
        score2 = combine_seasonal_flags(tdom, tdoy)
        
        pd.testing.assert_series_equal(score1, score2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

