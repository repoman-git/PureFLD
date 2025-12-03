"""
Parameter Sweep Engine Test Suite

Tests for parameter sweep and optimization system.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd
import numpy as np

from meridian_v2_1_2.research.param_sweep import (
    SweepConfig,
    SweepGrid,
    SweepRunner,
    SweepResults,
    SweepVisualizer
)
from meridian_v2_1_2.research.param_sweep.sweep_config import SweepMode


class TestSweepConfig:
    """Test sweep configuration"""
    
    def test_config_defaults(self):
        """Test default configuration"""
        config = SweepConfig()
        
        assert config.mode == SweepMode.GRID
        assert len(config.fld_offsets) > 0
        assert config.primary_metric == "sharpe_ratio"
    
    def test_config_customization(self):
        """Test custom configuration"""
        config = SweepConfig(
            mode=SweepMode.RANDOM,
            fld_offsets=[5, 10],
            random_samples=25
        )
        
        assert config.mode == SweepMode.RANDOM
        assert config.fld_offsets == [5, 10]
        assert config.random_samples == 25


class TestSweepGrid:
    """Test sweep grid generator"""
    
    def test_grid_initialization(self):
        """Test grid can be initialized"""
        config = SweepConfig()
        grid = SweepGrid(config)
        
        assert grid is not None
    
    def test_grid_generation(self):
        """Test grid generation"""
        config = SweepConfig(
            fld_offsets=[5, 10],
            fld_smoothing=[3, 5],
            cot_thresholds=[0.0],
            cot_lookback=[100],
            tdom_filter_enabled=[True],
            tdom_threshold=[0.5],
            slippage_bps=[4.0]
        )
        
        grid = SweepGrid(config)
        combinations = grid.generate()
        
        # Should have 2*2*1*1*1*1*1 = 4 combinations
        assert len(combinations) == 4
        
        # Check first combination structure
        assert 'fld_offset' in combinations[0]
        assert 'fld_smoothing' in combinations[0]
    
    def test_random_generation(self):
        """Test random search generation"""
        config = SweepConfig(
            mode=SweepMode.RANDOM,
            random_samples=10,
            random_seed=42
        )
        
        grid = SweepGrid(config)
        combinations = grid.generate()
        
        assert len(combinations) == 10
    
    def test_max_combinations_limit(self):
        """Test max combinations constraint"""
        config = SweepConfig(
            fld_offsets=list(range(10)),
            fld_smoothing=list(range(10)),
            max_combinations=50
        )
        
        grid = SweepGrid(config)
        combinations = grid.generate()
        
        assert len(combinations) <= 50


class TestSweepResults:
    """Test sweep results handler"""
    
    def test_results_initialization(self):
        """Test results initialization"""
        config = SweepConfig()
        results = SweepResults(config)
        
        assert results is not None
        assert len(results.results) == 0
    
    def test_add_result(self):
        """Test adding results"""
        config = SweepConfig()
        results = SweepResults(config)
        
        params = {'fld_offset': 10, 'cot_threshold': 0.0}
        metrics = {'sharpe_ratio': 1.5, 'total_return': 0.25}
        
        results.add_result(params, metrics)
        
        assert len(results.results) == 1
        assert results.results[0]['fld_offset'] == 10
        assert results.results[0]['sharpe_ratio'] == 1.5
    
    def test_get_dataframe(self):
        """Test DataFrame conversion"""
        config = SweepConfig()
        results = SweepResults(config)
        
        results.add_result(
            {'fld_offset': 10},
            {'sharpe_ratio': 1.5}
        )
        results.add_result(
            {'fld_offset': 15},
            {'sharpe_ratio': 1.8}
        )
        
        df = results.get_dataframe()
        
        assert len(df) == 2
        assert 'fld_offset' in df.columns
        assert 'sharpe_ratio' in df.columns
    
    def test_rank_by_metric(self):
        """Test ranking"""
        config = SweepConfig()
        results = SweepResults(config)
        
        results.add_result({'fld_offset': 10}, {'sharpe_ratio': 1.5})
        results.add_result({'fld_offset': 15}, {'sharpe_ratio': 1.8})
        results.add_result({'fld_offset': 5}, {'sharpe_ratio': 1.2})
        
        ranked = results.rank_by_metric('sharpe_ratio', ascending=False)
        
        assert ranked.iloc[0]['sharpe_ratio'] == 1.8
        assert ranked.iloc[-1]['sharpe_ratio'] == 1.2
    
    def test_get_best_params(self):
        """Test getting best parameters"""
        config = SweepConfig()
        results = SweepResults(config)
        
        results.add_result({'fld_offset': 10}, {'sharpe_ratio': 1.5})
        results.add_result({'fld_offset': 15}, {'sharpe_ratio': 1.8})
        
        best = results.get_best_params('sharpe_ratio')
        
        assert best['fld_offset'] == 15
        assert best['sharpe_ratio'] == 1.8


class TestSweepRunner:
    """Test sweep runner"""
    
    def test_runner_initialization(self):
        """Test runner can be initialized"""
        config = SweepConfig()
        runner = SweepRunner(config)
        
        assert runner is not None
    
    def test_runner_with_synthetic_data(self):
        """Test running sweep with synthetic data"""
        # Create simple synthetic data
        dates = pd.date_range('2020-01-01', periods=100)
        prices = pd.DataFrame({
            'close': 100 + np.cumsum(np.random.randn(100) * 0.5)
        }, index=dates)
        
        cot = pd.Series(np.random.randn(100), index=dates)
        seasonal = pd.Series(0.5, index=dates)
        
        # Small sweep for testing
        config = SweepConfig(
            fld_offsets=[5, 10],
            fld_smoothing=[3],
            cot_thresholds=[0.0],
            cot_lookback=[50],
            tdom_filter_enabled=[False],
            tdom_threshold=[0.5],
            slippage_bps=[2.0]
        )
        
        runner = SweepRunner(config)
        results = runner.run(prices, cot, seasonal, initial_capital=100000)
        
        # Should have results
        assert len(results.results) >= 1
        
        # Check result structure
        df = results.get_dataframe()
        assert 'sharpe_ratio' in df.columns
        assert 'total_return' in df.columns


class TestSweepVisualizer:
    """Test sweep visualizations"""
    
    def test_visualizer_initialization(self):
        """Test visualizer initialization"""
        config = SweepConfig()
        results = SweepResults(config)
        results.add_result({'fld_offset': 10}, {'sharpe_ratio': 1.5})
        
        viz = SweepVisualizer(results)
        
        assert viz is not None
        assert len(viz.df) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

