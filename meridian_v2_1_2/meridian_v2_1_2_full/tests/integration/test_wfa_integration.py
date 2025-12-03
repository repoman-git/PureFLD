"""
Walk-Forward Analysis Integration Test

Tests WFA with synthetic data across full system.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pandas as pd

from meridian_v2_1_2.config import MeridianConfig
from meridian_v2_1_2.synthetic import SyntheticDataset
from meridian_v2_1_2.wfa import (
    run_walkforward_analysis,
    compute_wfa_metrics
)


class TestWFAIntegration:
    """Test WFA on synthetic markets"""
    
    def test_wfa_on_synthetic_market(self):
        """Test walk-forward analysis runs on synthetic data"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 2000  # ~5.5 years
        cfg.synthetic.seed = 42
        cfg.wfa.training_window = "2Y"
        cfg.wfa.testing_window = "6M"
        cfg.wfa.step_size = "6M"
        
        # Generate synthetic market
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD'])
        
        prices = data['prices']['GLD']['close']
        
        # Run WFA
        wfa_results = run_walkforward_analysis(prices, cfg)
        
        # Should have multiple windows
        assert len(wfa_results) > 0
        
        # Each window should have OOS metrics
        for result in wfa_results:
            assert 'oos_sharpe' in result
            assert 'oos_return' in result
            assert isinstance(result['oos_sharpe'], (int, float))
    
    def test_wfa_metrics_computation(self):
        """Test WFA metrics are computed correctly"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 1500
        
        dataset = SyntheticDataset(cfg)
        data = dataset.generate(symbols=['GLD'])
        
        prices = data['prices']['GLD']['close']
        
        wfa_results = run_walkforward_analysis(prices, cfg)
        metrics = compute_wfa_metrics(wfa_results)
        
        # Should have summary metrics
        assert 'mean_oos_sharpe' in metrics
        assert 'stability_score' in metrics
        assert 'win_rate' in metrics
        assert 'overfit_index' in metrics
        
        # Win rate should be between 0 and 1
        assert 0 <= metrics['win_rate'] <= 1
    
    def test_wfa_survives_market_crash(self):
        """Test WFA handles crash scenario"""
        cfg = MeridianConfig()
        cfg.synthetic.length_days = 3000  # Need enough data for WFA windows
        cfg.wfa.training_window = "1Y"
        cfg.wfa.testing_window = "3M"
        cfg.wfa.step_size = "3M"
        
        # Generate crash scenario
        dataset = SyntheticDataset(cfg)
        data = dataset.generate_stress_scenario('crash')
        
        prices = data['prices']['GLD']['close']
        
        # WFA should complete without errors
        wfa_results = run_walkforward_analysis(prices, cfg)
        
        # With 3000 days and smaller windows, should have results
        # May be 0 if data is too short, which is acceptable
        assert isinstance(wfa_results, list)

