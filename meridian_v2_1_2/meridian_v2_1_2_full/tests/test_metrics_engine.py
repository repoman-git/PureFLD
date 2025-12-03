"""
Comprehensive test suite for Metrics Engine in Meridian v2.1.2.

Tests verify performance metrics, trade metrics, and robustness scoring.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.metrics_engine import (
    compute_basic_metrics,
    compute_trade_metrics,
    compute_robustness_score,
    compute_drawdown_series,
    compute_underwater_curve
)


class TestBasicMetrics:
    """Test basic performance metrics computation"""
    
    def test_max_drawdown_correctness(self):
        """
        TEST 1: Max drawdown calculated correctly
        
        Equity: 100 → 110 → 90 → 120
        Peak: 110
        Trough: 90
        Drawdown: (90-110)/110 = -18.18%
        """
        dates = pd.date_range('2020-01-01', periods=4, freq='D')
        equity = pd.Series([100, 110, 90, 120], index=dates)
        
        metrics = compute_basic_metrics(equity, initial_capital=100)
        
        # Max drawdown should be approximately -0.1818
        expected_dd = (90 - 110) / 110
        assert abs(metrics['max_drawdown'] - expected_dd) < 0.001
    
    def test_cagr_on_synthetic_series(self):
        """
        TEST 2: CAGR calculation
        
        100 → 110 → 121 over 2 years = 10% CAGR
        """
        dates = pd.date_range('2020-01-01', periods=505, freq='D')  # ~2 years
        
        # 10% annual growth compounded daily
        daily_return = (1.10 ** (1/252)) - 1
        equity = pd.Series([100 * (1 + daily_return) ** i for i in range(505)], index=dates)
        
        metrics = compute_basic_metrics(equity, initial_capital=100, periods_per_year=252)
        
        # CAGR should be approximately 10%
        assert abs(metrics['cagr'] - 0.10) < 0.01  # Within 1%
    
    def test_sharpe_ratio_reproducibility(self):
        """
        TEST 3: Sharpe ratio is deterministic
        """
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        equity = pd.Series(np.linspace(100, 120, 100), index=dates)
        
        metrics1 = compute_basic_metrics(equity, initial_capital=100)
        metrics2 = compute_basic_metrics(equity, initial_capital=100)
        
        assert metrics1['sharpe_ratio'] == metrics2['sharpe_ratio']
    
    def test_calmar_ratio_calculation(self):
        """
        TEST: Calmar ratio = CAGR / |MaxDD|
        """
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        
        # Create equity with known CAGR and drawdown
        equity = pd.Series([100, 110, 95, 115], index=dates[:4])
        
        metrics = compute_basic_metrics(equity, initial_capital=100, periods_per_year=252)
        
        # Should have positive calmar ratio
        assert metrics['calmar_ratio'] != 0
        
        # Verify calculation
        if metrics['max_drawdown'] < 0:
            expected_calmar = metrics['cagr'] / abs(metrics['max_drawdown'])
            assert abs(metrics['calmar_ratio'] - expected_calmar) < 0.001


class TestTradeMetrics:
    """Test trade-level metrics computation"""
    
    def test_trade_expectancy_math(self):
        """
        TEST 4: Trade expectancy formula
        
        expectancy = win_rate * avg_win + loss_rate * avg_loss
        """
        trades = pd.DataFrame({
            'entry_price': [100, 100, 100, 100],
            'exit_price': [110, 90, 120, 95],
            'pnl': [10, -10, 20, -5],
            'bars': [5, 3, 7, 4]
        })
        
        metrics = compute_trade_metrics(trades)
        
        # Verify expectancy calculation
        win_rate = metrics['win_rate']
        loss_rate = 1 - win_rate
        avg_win = metrics['average_win']
        avg_loss = metrics['average_loss']
        
        expected_expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)
        
        assert abs(metrics['expectancy'] - expected_expectancy) < 0.001
    
    def test_win_rate_calculation(self):
        """
        TEST: Win rate = wins / total_trades
        """
        trades = pd.DataFrame({
            'entry_price': [100, 100, 100, 100],
            'exit_price': [110, 110, 90, 95],
            'pnl': [10, 10, -10, -5],
            'bars': [5, 5, 3, 4]
        })
        
        metrics = compute_trade_metrics(trades)
        
        # 2 wins out of 4 trades = 50%
        assert metrics['win_rate'] == 0.5
        assert metrics['num_wins'] == 2
        assert metrics['num_losses'] == 2
    
    def test_payoff_ratio_calculation(self):
        """
        TEST: Payoff ratio = avg_win / |avg_loss|
        """
        trades = pd.DataFrame({
            'entry_price': [100, 100],
            'exit_price': [120, 90],
            'pnl': [20, -10],
            'bars': [5, 5]
        })
        
        metrics = compute_trade_metrics(trades)
        
        # avg_win = 20, avg_loss = -10
        # payoff = 20 / 10 = 2.0
        assert metrics['payoff_ratio'] == 2.0
    
    def test_hold_period_metrics(self):
        """
        TEST: Hold period statistics
        """
        trades = pd.DataFrame({
            'entry_price': [100, 100, 100],
            'exit_price': [110, 110, 110],
            'pnl': [10, 10, 10],
            'bars': [5, 10, 15]
        })
        
        metrics = compute_trade_metrics(trades)
        
        assert metrics['median_hold_period'] == 10
        assert metrics['mean_hold_period'] == 10


class TestRobustnessScore:
    """Test robustness scoring for parameter sweeps"""
    
    def test_robust_sweep_high_score(self):
        """
        TEST 5: Robust sweep gets high score
        
        Given:
            - 80% profitable
            - Smooth returns
            - Good MAR ratios
        
        Expect:
            - High robustness score (> 0.6)
        """
        # Create synthetic sweep results
        sweep_df = pd.DataFrame({
            'cycle_length': [40] * 10,
            'displacement': list(range(10, 20)),
            'total_return': [0.15, 0.14, 0.16, 0.15, 0.14, 0.15, 0.16, 0.14, -0.02, -0.01],
            'max_drawdown': [-0.08, -0.09, -0.07, -0.08, -0.09, -0.08, -0.07, -0.09, -0.05, -0.04]
        })
        
        robustness = compute_robustness_score(sweep_df)
        
        # Should have high score
        assert robustness['robustness_score'] > 0.6
        assert robustness['pct_profitable'] == 0.8
        assert robustness['num_combinations'] == 10
    
    def test_fragile_sweep_low_score(self):
        """
        TEST: Fragile sweep gets low score
        
        Given:
            - 30% profitable
            - Noisy returns
            - Poor MAR ratios
        
        Expect:
            - Low robustness score (< 0.4)
        """
        sweep_df = pd.DataFrame({
            'cycle_length': [40] * 10,
            'displacement': list(range(10, 20)),
            'total_return': [0.05, -0.10, -0.15, 0.02, -0.08, -0.12, 0.01, -0.05, -0.20, -0.18],
            'max_drawdown': [-0.15, -0.20, -0.25, -0.18, -0.22, -0.24, -0.16, -0.19, -0.30, -0.28]
        })
        
        robustness = compute_robustness_score(sweep_df)
        
        # Should have low score
        assert robustness['robustness_score'] < 0.4
        assert robustness['pct_profitable'] == 0.3
    
    def test_robustness_with_mixed_results(self):
        """
        TEST: Mixed results give moderate score
        """
        sweep_df = pd.DataFrame({
            'cycle_length': [40, 50, 60],
            'displacement': [10, 15, 20],
            'total_return': [0.10, 0.05, -0.02],
            'max_drawdown': [-0.08, -0.10, -0.05]
        })
        
        robustness = compute_robustness_score(sweep_df)
        
        # Should be moderate (2/3 profitable = 66.7%)
        # Score can vary based on volatility, so just check reasonable range
        assert 0.2 < robustness['robustness_score'] < 0.8
        assert abs(robustness['pct_profitable'] - 0.667) < 0.01
        assert abs(robustness['pct_profitable'] - 0.667) < 0.01


class TestDeterminism:
    """Test that all metrics are deterministic"""
    
    def test_basic_metrics_determinism(self):
        """
        TEST 6: Basic metrics are deterministic
        """
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        equity = pd.Series(np.random.RandomState(42).randn(100).cumsum() + 100, index=dates)
        
        metrics1 = compute_basic_metrics(equity, initial_capital=100)
        metrics2 = compute_basic_metrics(equity, initial_capital=100)
        
        # All metrics should be identical
        for key in metrics1.keys():
            assert metrics1[key] == metrics2[key], f"Mismatch in {key}"
    
    def test_trade_metrics_determinism(self):
        """
        TEST: Trade metrics are deterministic
        """
        trades = pd.DataFrame({
            'entry_price': [100, 105, 95],
            'exit_price': [110, 100, 105],
            'pnl': [10, -5, 10],
            'bars': [5, 3, 7]
        })
        
        metrics1 = compute_trade_metrics(trades)
        metrics2 = compute_trade_metrics(trades)
        
        for key in metrics1.keys():
            if metrics1[key] is not None:
                assert metrics1[key] == metrics2[key], f"Mismatch in {key}"
    
    def test_robustness_determinism(self):
        """
        TEST: Robustness scoring is deterministic
        """
        sweep_df = pd.DataFrame({
            'total_return': np.random.RandomState(42).randn(20) * 0.1,
            'max_drawdown': -np.random.RandomState(42).rand(20) * 0.1
        })
        
        robustness1 = compute_robustness_score(sweep_df)
        robustness2 = compute_robustness_score(sweep_df)
        
        assert robustness1['robustness_score'] == robustness2['robustness_score']


class TestDrawdownFunctions:
    """Test drawdown calculation functions"""
    
    def test_drawdown_series_calculation(self):
        """
        TEST: Drawdown series calculated correctly
        """
        dates = pd.date_range('2020-01-01', periods=5, freq='D')
        equity = pd.Series([100, 110, 90, 95, 120], index=dates)
        
        dd = compute_drawdown_series(equity)
        
        # At peak (110), DD = 0
        assert dd.iloc[1] == 0.0
        
        # At trough (90), DD = (90-110)/110
        expected_dd = (90 - 110) / 110
        assert abs(dd.iloc[2] - expected_dd) < 0.001
    
    def test_underwater_curve(self):
        """
        TEST: Underwater curve (drawdown as percentage)
        """
        dates = pd.date_range('2020-01-01', periods=5, freq='D')
        equity = pd.Series([100, 110, 90, 95, 120], index=dates)
        
        underwater = compute_underwater_curve(equity)
        
        # Should be in percentage terms
        assert underwater.iloc[1] == 0.0
        assert underwater.iloc[2] < 0  # Negative percentage


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_equity_curve(self):
        """
        TEST: Empty equity curve returns empty metrics
        """
        equity = pd.Series([], dtype=float)
        metrics = compute_basic_metrics(equity)
        
        assert metrics['final_equity'] == 0.0
        assert metrics['cagr'] == 0.0
    
    def test_single_point_equity(self):
        """
        TEST: Single point equity curve
        """
        dates = pd.date_range('2020-01-01', periods=1, freq='D')
        equity = pd.Series([100], index=dates)
        
        metrics = compute_basic_metrics(equity, initial_capital=100)
        
        # Should handle gracefully
        assert metrics['final_equity'] == 100
    
    def test_empty_trades_dataframe(self):
        """
        TEST: Empty trades DataFrame
        """
        trades = pd.DataFrame()
        metrics = compute_trade_metrics(trades)
        
        assert metrics['number_of_trades'] == 0
        assert metrics['win_rate'] == 0.0
    
    def test_all_winning_trades(self):
        """
        TEST: All trades profitable
        """
        trades = pd.DataFrame({
            'entry_price': [100, 100, 100],
            'exit_price': [110, 120, 115],
            'pnl': [10, 20, 15],
            'bars': [5, 5, 5]
        })
        
        metrics = compute_trade_metrics(trades)
        
        assert metrics['win_rate'] == 1.0
        assert metrics['num_losses'] == 0
        assert metrics['average_loss'] == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

