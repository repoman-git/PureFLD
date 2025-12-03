import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
from datetime import datetime, timedelta
from meridian_v2_1_2.config import MeridianConfig, SeasonalityConfig, StrategyConfig
from meridian_v2_1_2.seasonality import compute_tdom_flags
from meridian_v2_1_2.strategy import FLDStrategy
from meridian_v2_1_2.orchestrator_legacy import run_backtest

def create_test_data(days=20):
    """Create synthetic test data"""
    dates = pd.date_range(start='2020-01-01', periods=days, freq='D')
    prices = pd.Series(range(100, 100 + days), index=dates, name='close')
    fld = pd.Series(range(98, 98 + days), index=dates, name='fld')
    return prices, fld, dates

class TestTDOMFlags:
    """Test the raw compute_tdom_flags function"""
    
    def test_favourable_days_marked_correctly(self):
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        tdom = compute_tdom_flags(dates, favourable_days=[1, 2, 3], unfavourable_days=[])
        
        assert tdom.loc['2020-01-01'] == 1  # Day 1
        assert tdom.loc['2020-01-02'] == 1  # Day 2
        assert tdom.loc['2020-01-03'] == 1  # Day 3
        assert tdom.loc['2020-01-04'] == 0  # Day 4 (neutral)
    
    def test_unfavourable_days_marked_correctly(self):
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        tdom = compute_tdom_flags(dates, favourable_days=[], unfavourable_days=[5, 6])
        
        assert tdom.loc['2020-01-05'] == -1  # Day 5
        assert tdom.loc['2020-01-06'] == -1  # Day 6
        assert tdom.loc['2020-01-07'] == 0   # Day 7 (neutral)
    
    def test_deterministic_output(self):
        dates = pd.date_range('2020-01-01', '2020-01-10', freq='D')
        tdom1 = compute_tdom_flags(dates, [1, 2], [5, 6])
        tdom2 = compute_tdom_flags(dates, [1, 2], [5, 6])
        
        pd.testing.assert_series_equal(tdom1, tdom2)

class TestStrategyTDOMGating:
    """Test TDOM gating in strategy"""
    
    def test_entries_blocked_on_unfavourable_days(self):
        prices, fld, dates = create_test_data(10)
        
        # Create TDOM with day 3 unfavourable
        tdom = pd.Series([1, 1, -1, 0, 0, 0, 0, 0, 0, 0], index=dates)
        
        # Configure strategy to use TDOM
        config = StrategyConfig(use_tdom=True)
        strategy = FLDStrategy(config)
        
        # Manually create crossover on day 3 (unfavourable)
        prices.iloc[2] = fld.iloc[2] + 5  # Force crossover
        
        signals = strategy.generate_signals(prices, fld, tdom_series=tdom)
        
        # Signal on unfavourable day should be blocked
        assert signals.loc[dates[2], 'signal'] == 0
    
    def test_entries_allowed_on_favourable_days(self):
        prices, fld, dates = create_test_data(10)
        
        # All days favourable
        tdom = pd.Series([1] * 10, index=dates)
        
        config = StrategyConfig(use_tdom=True)
        strategy = FLDStrategy(config)
        
        # Create clear crossover
        prices = pd.Series([95, 95, 105, 105, 105], index=dates[:5])
        fld = pd.Series([100, 100, 100, 100, 100], index=dates[:5])
        
        signals = strategy.generate_signals(prices, fld, tdom_series=tdom[:5])
        
        # Should have signal on day 3
        assert signals.loc[dates[2], 'signal'] != 0
    
    def test_neutral_days_allow_entries(self):
        prices, fld, dates = create_test_data(10)
        
        # All days neutral
        tdom = pd.Series([0] * 10, index=dates)
        
        config = StrategyConfig(use_tdom=True)
        strategy = FLDStrategy(config)
        
        prices = pd.Series([95, 95, 105, 105, 105], index=dates[:5])
        fld = pd.Series([100, 100, 100, 100, 100], index=dates[:5])
        
        signals = strategy.generate_signals(prices, fld, tdom_series=tdom[:5])
        
        # Neutral days should not block
        assert signals.loc[dates[2], 'signal'] != 0
    
    def test_missing_tdom_series_no_crash(self):
        prices, fld, dates = create_test_data(5)
        
        config = StrategyConfig(use_tdom=False)
        strategy = FLDStrategy(config)
        
        # Should not crash without TDOM
        signals = strategy.generate_signals(prices, fld, tdom_series=None)
        
        assert len(signals) == len(prices)

class TestOrchestratorIntegration:
    """Test TDOM integration in orchestrator"""
    
    def test_tdom_computed_when_enabled(self):
        prices, _, dates = create_test_data(10)
        
        config = MeridianConfig()
        config.seasonality.use_tdom = True
        config.seasonality.favourable_days = [1, 2, 3]
        config.strategy.use_tdom = True
        
        results = run_backtest(config, prices)
        
        assert results['tdom'] is not None
        assert len(results['tdom']) == len(prices)
        assert results['tdom'].loc[dates[0]] == 1  # Day 1 should be favourable
    
    def test_tdom_not_computed_when_disabled(self):
        prices, _, _ = create_test_data(10)
        
        config = MeridianConfig()
        config.seasonality.use_tdom = False
        
        results = run_backtest(config, prices)
        
        assert results['tdom'] is None
    
    def test_deterministic_results(self):
        prices, _, _ = create_test_data(10)
        
        config = MeridianConfig()
        config.seasonality.use_tdom = True
        
        results1 = run_backtest(config, prices)
        results2 = run_backtest(config, prices)
        
        pd.testing.assert_frame_equal(results1['signals'], results2['signals'])

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

