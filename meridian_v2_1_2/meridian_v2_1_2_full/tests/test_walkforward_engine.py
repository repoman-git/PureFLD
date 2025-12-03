"""
Comprehensive test suite for Walk-Forward Engine in Meridian v2.1.2.

Tests verify split generation, parameter selection, and out-of-sample validation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2 import (
    MeridianConfig,
    WalkForwardConfig,
    generate_walkforward_splits,
    walkforward_run,
    analyze_walkforward_results
)
from meridian_v2_1_2.walkforward_engine import _select_best_parameters


def create_test_data(years=10, periods_per_year=252):
    """Create synthetic multi-year test data"""
    total_days = years * periods_per_year
    dates = pd.date_range('2010-01-01', periods=total_days, freq='D')
    # Trending price with some noise
    trend = np.linspace(1000, 1500, total_days)
    noise = np.random.RandomState(42).randn(total_days) * 10
    prices = pd.Series(trend + noise, index=dates, name='close')
    return prices, dates


class TestSplitGeneration:
    """Test walk-forward split generation"""
    
    def test_multiple_splits_created_correctly(self):
        """
        TEST 1: Multiple IS/OS splits created correctly
        """
        _, dates = create_test_data(years=10, periods_per_year=252)
        
        config = WalkForwardConfig(
            in_sample_years=5,
            out_sample_years=1,
            step_years=1,
            min_bars=200
        )
        
        splits = generate_walkforward_splits(dates, config, periods_per_year=252)
        
        # Should have multiple splits
        assert len(splits) > 0
        
        # Each split should have 4 elements
        for split in splits:
            assert len(split) == 4
            train_start, train_end, test_start, test_end = split
            
            # Train should come before test
            assert train_end < test_start
    
    def test_windows_slide_correctly(self):
        """
        TEST 2: Windows slide as expected
        
        With step_years=1, each split should start 1 year after previous
        """
        _, dates = create_test_data(years=10, periods_per_year=252)
        
        config = WalkForwardConfig(
            in_sample_years=5,
            out_sample_years=1,
            step_years=1,
            min_bars=200
        )
        
        splits = generate_walkforward_splits(dates, config, periods_per_year=252)
        
        if len(splits) >= 2:
            # Check first two splits
            train_start_1, _, _, _ = splits[0]
            train_start_2, _, _, _ = splits[1]
            
            # Second train start should be approximately step_years after first
            days_between = (train_start_2 - train_start_1).days
            # Should be around 252 days (1 year), allow some variance
            assert 200 < days_between < 300
    
    def test_final_partial_windows_handled(self):
        """
        TEST 3: Final partial windows handled correctly
        """
        _, dates = create_test_data(years=7, periods_per_year=252)
        
        # With allow_partial=True, should include partial final window
        config_allow = WalkForwardConfig(
            in_sample_years=5,
            out_sample_years=1,
            step_years=1,
            allow_partial_final_window=True
        )
        
        splits_allow = generate_walkforward_splits(dates, config_allow, periods_per_year=252)
        
        # With allow_partial=False, should not include partial final window
        config_reject = WalkForwardConfig(
            in_sample_years=5,
            out_sample_years=1,
            step_years=1,
            allow_partial_final_window=False
        )
        
        splits_reject = generate_walkforward_splits(dates, config_reject, periods_per_year=252)
        
        # Allow should have same or more splits
        assert len(splits_allow) >= len(splits_reject)
    
    def test_insufficient_data_raises_error(self):
        """
        TEST: Insufficient data raises ValueError
        """
        dates = pd.date_range('2020-01-01', periods=100, freq='D')  # Only 100 bars
        
        config = WalkForwardConfig(min_bars=200)
        
        with pytest.raises(ValueError, match="Insufficient data"):
            generate_walkforward_splits(dates, config)


class TestParameterSelection:
    """Test best parameter selection from sweep results"""
    
    def test_highest_mar_selected(self):
        """
        TEST 4: Best parameter selection - highest MAR
        """
        sweep_df = pd.DataFrame({
            'cycle_length': [40, 50, 60],
            'displacement': [10, 20, 30],
            'calmar_ratio': [1.2, 1.8, 1.5],  # Best is row 1
            'cagr': [0.10, 0.12, 0.11],
            'max_drawdown': [-0.08, -0.07, -0.08],
            'total_return': [0.10, 0.12, 0.11],
            'sharpe_ratio': [1.5, 1.8, 1.6],
            'num_trades': [20, 25, 22]
        })
        
        best = _select_best_parameters(sweep_df, optimization_metric='calmar_ratio')
        
        # Should select row with highest calmar
        assert best['cycle_length'] == 50
        assert best['calmar_ratio'] == 1.8
    
    def test_ties_broken_deterministically(self):
        """
        TEST: Ties broken deterministically (first occurrence)
        """
        sweep_df = pd.DataFrame({
            'cycle_length': [40, 50, 60],
            'displacement': [10, 20, 30],
            'calmar_ratio': [1.5, 1.5, 1.5],  # All equal
            'total_return': [0.10, 0.10, 0.10],
            'cagr': [0.10, 0.10, 0.10],
            'max_drawdown': [-0.08, -0.08, -0.08],
            'sharpe_ratio': [1.5, 1.5, 1.5],
            'num_trades': [20, 20, 20]
        })
        
        best1 = _select_best_parameters(sweep_df, optimization_metric='calmar_ratio')
        best2 = _select_best_parameters(sweep_df, optimization_metric='calmar_ratio')
        
        # Should always select same one
        assert best1['cycle_length'] == best2['cycle_length']
    
    def test_nan_values_skipped(self):
        """
        TEST: NaN values in optimization metric are skipped
        """
        sweep_df = pd.DataFrame({
            'cycle_length': [40, 50, 60],
            'displacement': [10, 20, 30],
            'calmar_ratio': [np.nan, 1.8, 1.5],
            'total_return': [0.10, 0.12, 0.11],
            'cagr': [0.10, 0.12, 0.11],
            'max_drawdown': [-0.08, -0.07, -0.08],
            'sharpe_ratio': [1.5, 1.8, 1.6],
            'num_trades': [20, 25, 22]
        })
        
        best = _select_best_parameters(sweep_df, optimization_metric='calmar_ratio')
        
        # Should skip NaN and select 1.8
        assert best['cycle_length'] == 50
        assert best['calmar_ratio'] == 1.8


class TestWalkForwardExecution:
    """Test walk-forward execution"""
    
    def test_walkforward_completes_successfully(self):
        """
        TEST 5: Walk-forward runs successfully on synthetic data
        """
        prices, _ = create_test_data(years=8, periods_per_year=252)
        
        config = MeridianConfig()
        config.walkforward.in_sample_years = 5
        config.walkforward.out_sample_years = 1
        config.walkforward.step_years = 1
        config.sweep.cycle_lengths = [40, 60]
        config.sweep.displacements = [10, 20]
        
        # Run walk-forward
        results = walkforward_run(prices, config)
        
        # Should have results
        assert len(results) > 0
        
        # Check required columns
        required_cols = [
            'train_start', 'train_end', 'test_start', 'test_end',
            'cycle_length', 'displacement',
            'is_cagr', 'is_sharpe', 'is_calmar',
            'os_cagr', 'os_sharpe', 'os_calmar'
        ]
        for col in required_cols:
            assert col in results.columns, f"Missing column: {col}"
    
    def test_walkforward_is_os_metrics_present(self):
        """
        TEST: Walk-forward output contains IS and OS metrics
        """
        prices, _ = create_test_data(years=8, periods_per_year=252)
        
        config = MeridianConfig()
        config.walkforward.in_sample_years = 5
        config.walkforward.out_sample_years = 1
        config.walkforward.step_years = 2  # Larger step for fewer splits
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        
        results = walkforward_run(prices, config)
        
        # Check IS metrics present
        assert 'is_cagr' in results.columns
        assert 'is_sharpe' in results.columns
        assert 'is_return' in results.columns
        
        # Check OS metrics present
        assert 'os_cagr' in results.columns
        assert 'os_sharpe' in results.columns
        assert 'os_return' in results.columns


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_walkforward_deterministic(self):
        """
        TEST 6: Two runs with same data → identical output
        """
        prices, _ = create_test_data(years=8, periods_per_year=252)
        
        config = MeridianConfig()
        config.walkforward.in_sample_years = 5
        config.walkforward.out_sample_years = 1
        config.walkforward.step_years = 2
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        
        results1 = walkforward_run(prices, config)
        results2 = walkforward_run(prices, config)
        
        # Should be identical
        pd.testing.assert_frame_equal(
            results1.drop(columns=['train_start', 'train_end', 'test_start', 'test_end'], errors='ignore'),
            results2.drop(columns=['train_start', 'train_end', 'test_start', 'test_end'], errors='ignore')
        )
    
    def test_split_generation_deterministic(self):
        """
        TEST: Split generation is deterministic
        """
        _, dates = create_test_data(years=10, periods_per_year=252)
        
        config = WalkForwardConfig(
            in_sample_years=5,
            out_sample_years=1,
            step_years=1
        )
        
        splits1 = generate_walkforward_splits(dates, config, periods_per_year=252)
        splits2 = generate_walkforward_splits(dates, config, periods_per_year=252)
        
        assert splits1 == splits2


class TestWalkForwardAnalysis:
    """Test walk-forward result analysis"""
    
    def test_analyze_walkforward_results(self):
        """
        TEST: Walk-forward analysis computes summary stats
        """
        # Create synthetic WF results
        wf_results = pd.DataFrame({
            'split_index': [0, 1, 2],
            'cycle_length': [40, 50, 40],
            'displacement': [20, 20, 20],
            'is_return': [0.15, 0.12, 0.14],
            'is_sharpe': [1.8, 1.6, 1.7],
            'is_calmar': [1.5, 1.3, 1.4],
            'os_return': [0.10, 0.08, 0.12],
            'os_sharpe': [1.5, 1.3, 1.6],
            'os_calmar': [1.2, 1.0, 1.3]
        })
        
        analysis = analyze_walkforward_results(wf_results)
        
        # Check required metrics
        assert 'num_splits' in analysis
        assert analysis['num_splits'] == 3
        
        assert 'avg_os_return' in analysis
        assert 'pct_profitable_os' in analysis
        assert 'is_os_correlation' in analysis


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

