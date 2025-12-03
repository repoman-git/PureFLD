"""
Test suite for Walk-Forward Analysis Engine

Tests comprehensive OOS validation with EOD integration.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.wfa import (
    split_walkforward_windows,
    parse_period,
    run_walkforward_analysis,
    execute_wfa_window,
    compute_wfa_metrics,
    compute_overfit_index,
    compute_stability_score,
    generate_wfa_report
)
from meridian_v2_1_2.config import MeridianConfig


class TestWFASplitter:
    """Test walk-forward window splitting"""
    
    def test_parse_period_years(self):
        """Test parsing year periods"""
        offset = parse_period("3Y")
        assert offset.years == 3
    
    def test_parse_period_months(self):
        """Test parsing month periods"""
        offset = parse_period("6M")
        assert offset.months == 6
    
    def test_parse_period_days(self):
        """Test parsing day periods"""
        offset = parse_period("30D")
        assert offset.days == 30
    
    def test_split_windows_basic(self):
        """Test basic window splitting"""
        # Create 5-year date range
        dates = pd.date_range("2010-01-01", "2015-01-01", freq="D")
        
        windows = split_walkforward_windows(
            dates,
            training_window="2Y",
            testing_window="6M",
            step_size="6M"
        )
        
        assert len(windows) > 0
        
        # Check first window
        train_dates, test_dates = windows[0]
        assert len(train_dates) > 0
        assert len(test_dates) > 0
        
        # Train should end where test starts
        assert train_dates[-1] < test_dates[0]
    
    def test_windows_non_overlapping_test_periods(self):
        """Test that test periods don't overlap"""
        dates = pd.date_range("2010-01-01", "2015-01-01", freq="D")
        
        windows = split_walkforward_windows(
            dates,
            training_window="2Y",
            testing_window="3M",
            step_size="3M"
        )
        
        if len(windows) > 1:
            for i in range(len(windows) - 1):
                _, test1 = windows[i]
                _, test2 = windows[i+1]
                
                # Test periods should not overlap
                assert test1[-1] <= test2[0]


class TestWFAExecutor:
    """Test WFA execution"""
    
    def test_execute_window_returns_results(self):
        """Test that window execution returns valid results"""
        # Create synthetic data
        dates = pd.date_range("2010-01-01", "2015-01-01", freq="D")
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(len(dates)) * 0.01),
            index=dates
        )
        
        # Split into train/test
        train_dates = dates[:1000]
        test_dates = dates[1000:1250]
        
        cfg = MeridianConfig()
        
        result = execute_wfa_window(
            train_dates,
            test_dates,
            prices,
            cfg
        )
        
        # Check result structure
        assert 'train_start' in result
        assert 'train_end' in result
        assert 'test_start' in result
        assert 'test_end' in result
        assert 'train_sharpe' in result
        assert 'oos_sharpe' in result
        assert 'oos_return' in result
        assert 'oos_pnl' in result
        assert 'oos_signals' in result
    
    def test_oos_metrics_computed(self):
        """Test that OOS metrics are computed"""
        dates = pd.date_range("2010-01-01", "2015-01-01", freq="D")
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(len(dates)) * 0.01),
            index=dates
        )
        
        train_dates = dates[:1000]
        test_dates = dates[1000:1250]
        
        cfg = MeridianConfig()
        
        result = execute_wfa_window(
            train_dates,
            test_dates,
            prices,
            cfg
        )
        
        # OOS Sharpe should be a number
        assert isinstance(result['oos_sharpe'], (int, float))
        assert not np.isnan(result['oos_sharpe'])


class TestWFAMetrics:
    """Test WFA metrics computation"""
    
    def test_overfit_index_normal(self):
        """Test overfit index with reasonable values"""
        train_perf = 1.5
        oos_perf = 1.2
        
        overfit_idx = compute_overfit_index(train_perf, oos_perf)
        
        assert overfit_idx == pytest.approx(1.25, rel=0.01)
    
    def test_overfit_index_high(self):
        """Test overfit index with overfitting"""
        train_perf = 3.0
        oos_perf = 0.5
        
        overfit_idx = compute_overfit_index(train_perf, oos_perf)
        
        assert overfit_idx > 2.0  # Indicates overfitting
    
    def test_overfit_index_negative_oos(self):
        """Test overfit index with negative OOS"""
        train_perf = 2.0
        oos_perf = -0.5
        
        overfit_idx = compute_overfit_index(train_perf, oos_perf)
        
        assert overfit_idx == np.inf
    
    def test_stability_score(self):
        """Test stability score computation"""
        oos_returns = [0.05, 0.04, 0.06, 0.03, 0.05]
        
        stability = compute_stability_score(oos_returns)
        
        # Should be positive for consistent returns
        assert stability > 0
    
    def test_stability_score_volatile(self):
        """Test stability score with volatile returns"""
        oos_returns = [0.10, -0.05, 0.15, -0.10, 0.08]
        
        stability = compute_stability_score(oos_returns)
        
        # Should be lower for volatile returns
        assert isinstance(stability, float)
    
    def test_wfa_metrics_aggregation(self):
        """Test WFA metrics aggregation"""
        # Create mock results
        wfa_results = [
            {
                'oos_sharpe': 1.2,
                'oos_return': 0.05,
                'train_sharpe': 1.5
            },
            {
                'oos_sharpe': 1.0,
                'oos_return': 0.04,
                'train_sharpe': 1.3
            },
            {
                'oos_sharpe': 1.3,
                'oos_return': 0.06,
                'train_sharpe': 1.6
            }
        ]
        
        metrics = compute_wfa_metrics(wfa_results)
        
        assert 'mean_oos_sharpe' in metrics
        assert 'median_oos_sharpe' in metrics
        assert 'stability_score' in metrics
        assert 'num_windows' in metrics
        assert 'win_rate' in metrics
        assert 'overfit_index' in metrics
        
        assert metrics['num_windows'] == 3
        assert metrics['mean_oos_sharpe'] == pytest.approx(1.1667, rel=0.01)
    
    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        wfa_results = [
            {'oos_sharpe': 1.0, 'oos_return': 0.05, 'train_sharpe': 1.2},
            {'oos_sharpe': 0.8, 'oos_return': -0.02, 'train_sharpe': 1.1},
            {'oos_sharpe': 1.1, 'oos_return': 0.03, 'train_sharpe': 1.3},
            {'oos_sharpe': 0.9, 'oos_return': 0.01, 'train_sharpe': 1.0}
        ]
        
        metrics = compute_wfa_metrics(wfa_results)
        
        # 3 out of 4 positive
        assert metrics['win_rate'] == 0.75
        assert metrics['positive_windows'] == 3
        assert metrics['negative_windows'] == 1


class TestWFARunner:
    """Test full WFA runner"""
    
    def test_run_walkforward_analysis(self):
        """Test running full WFA"""
        # Create synthetic price series
        dates = pd.date_range("2010-01-01", "2018-01-01", freq="D")
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(len(dates)) * 0.01),
            index=dates
        )
        
        cfg = MeridianConfig()
        cfg.wfa.training_window = "2Y"
        cfg.wfa.testing_window = "6M"
        cfg.wfa.step_size = "6M"
        
        results = run_walkforward_analysis(prices, cfg)
        
        assert len(results) > 0
        
        # Check each result
        for result in results:
            assert 'oos_sharpe' in result
            assert 'oos_return' in result
            assert 'train_sharpe' in result


class TestWFAReporter:
    """Test WFA reporting"""
    
    def test_generate_report(self, tmp_path):
        """Test report generation"""
        wfa_results = [
            {
                'train_start': pd.Timestamp('2010-01-01'),
                'train_end': pd.Timestamp('2012-01-01'),
                'test_start': pd.Timestamp('2012-01-01'),
                'test_end': pd.Timestamp('2012-07-01'),
                'oos_sharpe': 1.2,
                'oos_return': 0.05,
                'train_sharpe': 1.5
            }
        ]
        
        wfa_metrics = {
            'mean_oos_sharpe': 1.2,
            'stability_score': 2.5,
            'win_rate': 1.0,
            'overfit_index': 1.25,
            'num_windows': 1
        }
        
        report_path = generate_wfa_report(
            wfa_results,
            wfa_metrics,
            report_path=str(tmp_path)
        )
        
        assert report_path.endswith('.md')
        
        # Check file exists
        from pathlib import Path
        assert Path(report_path).exists()


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_wfa_deterministic(self):
        """Test that WFA produces identical results"""
        dates = pd.date_range("2010-01-01", "2015-01-01", freq="D")
        np.random.seed(42)
        prices = pd.Series(
            100 + np.cumsum(np.random.randn(len(dates)) * 0.01),
            index=dates
        )
        
        cfg = MeridianConfig()
        cfg.wfa.training_window = "2Y"
        cfg.wfa.testing_window = "6M"
        cfg.wfa.step_size = "6M"
        
        results1 = run_walkforward_analysis(prices, cfg)
        results2 = run_walkforward_analysis(prices, cfg)
        
        assert len(results1) == len(results2)
        
        for r1, r2 in zip(results1, results2):
            assert r1['oos_sharpe'] == r2['oos_sharpe']
            assert r1['oos_return'] == r2['oos_return']

