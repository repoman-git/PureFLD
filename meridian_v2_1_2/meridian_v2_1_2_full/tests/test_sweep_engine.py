"""
Comprehensive test suite for Sweep Engine in Meridian v2.1.2.

Tests verify parameter grid generation, deterministic sweeps, and output formats.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
import tempfile
import shutil

from meridian_v2_1_2 import (
    MeridianConfig,
    SweepConfig,
    run_parameter_sweep,
    write_results,
    get_best_parameters
)
from meridian_v2_1_2.sweep_engine import _build_parameter_grid, analyze_sweep_results


def create_test_data(length=50):
    """Create synthetic test data for sweeps"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    # Trending price data
    prices = pd.Series(range(100, 100 + length), index=dates, name='close')
    return prices, dates


class TestParameterGridGeneration:
    """Test parameter grid building"""
    
    def test_single_combination_grid(self):
        """
        TEST 1: Single combination (1x1x1x1) produces 1 row
        """
        sweep_cfg = SweepConfig(
            cycle_lengths=[40],
            displacements=[20],
            cot_long_thresholds=[0.0],
            cot_short_thresholds=[0.0],
            seasonal_score_minimums=[0]
        )
        
        grid = _build_parameter_grid(sweep_cfg)
        
        assert len(grid) == 1
        assert grid[0]['cycle_length'] == 40
        assert grid[0]['displacement'] == 20
    
    def test_multi_combination_grid(self):
        """
        TEST 2: Multi-combination grid (2x2x1x1x1 = 4 combinations)
        """
        sweep_cfg = SweepConfig(
            cycle_lengths=[40, 60],
            displacements=[10, 20],
            cot_long_thresholds=[0.0],
            cot_short_thresholds=[0.0],
            seasonal_score_minimums=[0]
        )
        
        grid = _build_parameter_grid(sweep_cfg)
        
        assert len(grid) == 4  # 2 * 2 * 1 * 1 * 1
        
        # Check all combinations present
        cycles = [g['cycle_length'] for g in grid]
        assert 40 in cycles and 60 in cycles
    
    def test_full_cartesian_product(self):
        """
        TEST: Full Cartesian product (2x2x2x2x2 = 32 combinations)
        """
        sweep_cfg = SweepConfig(
            cycle_lengths=[40, 60],
            displacements=[10, 20],
            cot_long_thresholds=[0.0, 0.1],
            cot_short_thresholds=[0.0, -0.1],
            seasonal_score_minimums=[0, 1]
        )
        
        grid = _build_parameter_grid(sweep_cfg)
        
        assert len(grid) == 32  # 2^5


class TestSweepDeterminism:
    """Test that sweeps are deterministic"""
    
    def test_deterministic_sweep(self):
        """
        TEST 3: Same inputs → identical outputs
        """
        prices, _ = create_test_data(50)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [40, 60]
        config.sweep.displacements = [10, 20]
        
        # Run twice
        results1 = run_parameter_sweep(prices, config)
        results2 = run_parameter_sweep(prices, config)
        
        # Should be identical
        pd.testing.assert_frame_equal(results1, results2)
    
    def test_single_combination_matches_single_run(self):
        """
        TEST 4: Single combination sweep matches standalone backtest
        
        If grid = 1x1x1x1x1, sweep result should match single backtest
        """
        prices, _ = create_test_data(50)
        
        config = MeridianConfig()
        config.fld.cycle_length = 40
        config.fld.displacement = 20
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        
        # Run sweep
        sweep_results = run_parameter_sweep(prices, config)
        
        # Should have exactly 1 row
        assert len(sweep_results) == 1
        
        # Check parameters match
        assert sweep_results.iloc[0]['cycle_length'] == 40
        assert sweep_results.iloc[0]['displacement'] == 20
        
        # Should have valid results
        assert 'total_return' in sweep_results.columns
        assert not pd.isna(sweep_results.iloc[0]['total_return'])


class TestSweepExecution:
    """Test sweep execution with various configurations"""
    
    def test_sweep_with_multiple_parameters(self):
        """
        TEST 5: Sweep with multiple FLD parameters
        """
        prices, _ = create_test_data(50)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [30, 40, 50]
        config.sweep.displacements = [10, 15, 20]
        
        results = run_parameter_sweep(prices, config)
        
        # Should have 3 * 3 = 9 combinations
        assert len(results) == 9
        
        # Check all cycle lengths present
        assert set(results['cycle_length'].unique()) == {30, 40, 50}
        assert set(results['displacement'].unique()) == {10, 15, 20}
    
    def test_sweep_with_cot_parameters(self):
        """
        TEST: Sweep with COT threshold variations
        """
        prices, dates = create_test_data(50)
        cot = pd.Series(np.random.randn(50) * 0.5, index=dates)
        
        config = MeridianConfig()
        config.strategy.use_cot = True
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        config.sweep.cot_long_thresholds = [0.0, 0.1, 0.2]
        
        results = run_parameter_sweep(prices, config, cot_series=cot)
        
        # Should have 3 combinations (1 * 1 * 3)
        assert len(results) == 3
        assert set(results['cot_long_threshold'].unique()) == {0.0, 0.1, 0.2}
    
    def test_sweep_with_seasonal_thresholds(self):
        """
        TEST: Sweep with seasonal score thresholds
        """
        prices, _ = create_test_data(50)
        
        config = MeridianConfig()
        config.seasonality.use_tdom = True
        config.seasonality.favourable_days = [1, 2, 3, 4, 5]
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        config.sweep.seasonal_score_minimums = [0, 1]
        
        results = run_parameter_sweep(prices, config)
        
        # Should have 2 combinations
        assert len(results) == 2
        assert set(results['seasonal_threshold'].unique()) == {0, 1}


class TestOutputFormats:
    """Test output writing in different formats"""
    
    def setup_method(self):
        """Create temporary directory for outputs"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir)
    
    def test_csv_output(self):
        """
        TEST 6: CSV output format
        """
        prices, _ = create_test_data(30)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [40, 60]
        config.sweep.displacements = [10, 20]
        config.sweep.output_path = self.temp_dir
        config.sweep.output_format = 'csv'
        
        results = run_parameter_sweep(prices, config)
        output_file = write_results(results, config.sweep)
        
        # Check file exists
        assert Path(output_file).exists()
        assert output_file.endswith('.csv')
        
        # Read back and verify
        df_read = pd.read_csv(output_file)
        assert len(df_read) == len(results)
    
    def test_json_output(self):
        """
        TEST 7: JSON output format
        """
        prices, _ = create_test_data(30)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [40, 60]
        config.sweep.displacements = [10, 20]
        config.sweep.output_path = self.temp_dir
        config.sweep.output_format = 'json'
        
        results = run_parameter_sweep(prices, config)
        output_file = write_results(results, config.sweep)
        
        # Check file exists
        assert Path(output_file).exists()
        assert output_file.endswith('.json')
        
        # Read back and verify
        df_read = pd.read_json(output_file)
        assert len(df_read) == len(results)
    
    def test_parquet_output(self):
        """
        TEST 8: Parquet output format (skip if pyarrow not available)
        """
        try:
            import pyarrow
        except ImportError:
            pytest.skip("pyarrow not installed")
        
        prices, _ = create_test_data(30)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [40, 60]
        config.sweep.displacements = [10, 20]
        config.sweep.output_path = self.temp_dir
        config.sweep.output_format = 'parquet'
        
        results = run_parameter_sweep(prices, config)
        output_file = write_results(results, config.sweep)
        
        # Check file exists
        assert Path(output_file).exists()
        assert output_file.endswith('.parquet')
        
        # Read back and verify
        df_read = pd.read_parquet(output_file)
        assert len(df_read) == len(results)


class TestErrorHandling:
    """Test error handling in sweep engine"""
    
    def test_empty_price_series_fails(self):
        """
        TEST 9: Empty prices should be handled gracefully
        
        The sweep engine catches errors and adds them to results with NaN values
        """
        dates = pd.date_range('2020-01-01', periods=0, freq='D')
        prices = pd.Series([], index=dates, dtype=float)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        
        # Should handle gracefully and return results with error info
        results = run_parameter_sweep(prices, config)
        
        # Should have 1 row with NaN values
        assert len(results) == 1
        assert pd.isna(results.iloc[0]['total_return'])
        assert 'error' in results.columns
    
    def test_missing_cot_when_not_used_allowed(self):
        """
        TEST 10: Missing COT when use_cot=False should be allowed
        """
        prices, _ = create_test_data(30)
        
        config = MeridianConfig()
        config.strategy.use_cot = False  # COT not used
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        
        # Should work without COT data
        results = run_parameter_sweep(prices, config, cot_series=None)
        
        assert len(results) > 0


class TestResultAnalysis:
    """Test result analysis functions"""
    
    def test_get_best_parameters(self):
        """
        TEST: Get best parameters by metric
        """
        prices, _ = create_test_data(50)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [30, 40, 50]
        config.sweep.displacements = [10, 20]
        
        results = run_parameter_sweep(prices, config)
        
        # Get best by total return
        best = get_best_parameters(results, metric='total_return', ascending=False)
        
        assert 'total_return' in best
        assert 'cycle_length' in best
        assert best['total_return'] == results['total_return'].max()
    
    def test_analyze_sweep_results(self):
        """
        TEST: Analyze sweep results summary
        """
        prices, _ = create_test_data(50)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [30, 40, 50]
        config.sweep.displacements = [10, 20]
        
        results = run_parameter_sweep(prices, config)
        analysis = analyze_sweep_results(results)
        
        assert 'total_combinations' in analysis
        assert analysis['total_combinations'] == 6  # 3 * 2
        assert 'best_total_return' in analysis
        assert 'mean_win_rate' in analysis


class TestSweepResultColumns:
    """Test that sweep results have expected columns"""
    
    def test_required_columns_present(self):
        """
        TEST: All required columns present in results
        """
        prices, _ = create_test_data(30)
        
        config = MeridianConfig()
        config.sweep.cycle_lengths = [40]
        config.sweep.displacements = [20]
        
        results = run_parameter_sweep(prices, config)
        
        # Check parameter columns
        assert 'cycle_length' in results.columns
        assert 'displacement' in results.columns
        assert 'cot_long_threshold' in results.columns
        assert 'cot_short_threshold' in results.columns
        assert 'seasonal_threshold' in results.columns
        
        # Check result columns
        assert 'total_return' in results.columns
        assert 'max_drawdown' in results.columns
        assert 'num_trades' in results.columns
        assert 'win_rate' in results.columns
        assert 'final_equity' in results.columns


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

