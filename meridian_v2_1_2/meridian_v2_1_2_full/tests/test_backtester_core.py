"""
Comprehensive test suite for Backtester Core in Meridian v2.1.2.

Tests verify that the backtester engine works independently from FLD logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np
from meridian_v2_1_2.backtester import Backtester, BacktestConfig, run_backtest


def create_test_data(length=10):
    """Create synthetic test data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    return dates


class TestFlatPositionsNoPnL:
    """Test that flat positions produce no PnL"""
    
    def test_flat_positions_preserve_capital(self):
        """
        TEST A: Flat positions → no PnL
        
        Given:
            prices = [100, 101, 102, 103]
            positions = [0, 0, 0, 0]
        
        Expect:
            equity = initial_capital (no change)
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 101, 102, 103], index=dates)
        positions = pd.Series([0, 0, 0, 0], index=dates)
        
        config = BacktestConfig(initial_capital=100000.0)
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Equity should remain constant
        assert results['equity'].iloc[0] == 100000.0
        assert results['equity'].iloc[-1] == 100000.0
        assert (results['equity'] == 100000.0).all()
        
        # No trades
        assert len(results['trades']) == 0
        assert results['stats']['total_trades'] == 0


class TestLongPositionPnL:
    """Test long position PnL calculation"""
    
    def test_long_1_contract_correct_pnl(self):
        """
        TEST B: Long 1 contract produces correct PnL
        
        Given:
            Long from 100 → 103 = +3 * contract_size
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 101, 102, 103], index=dates)
        positions = pd.Series([1, 1, 1, 1], index=dates)  # Long entire time
        
        config = BacktestConfig(
            initial_capital=100000.0,
            contract_size=1.0,
            commission=0.0,
            slippage=0.0
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should gain 3 points (103 - 100)
        expected_pnl = 3.0
        assert results['equity'].iloc[-1] == 100000.0 + expected_pnl
        
        # Check per-bar equity
        assert results['equity'].iloc[0] == 100000.0  # Entry
        assert results['equity'].iloc[1] == 100001.0  # +1
        assert results['equity'].iloc[2] == 100002.0  # +1
        assert results['equity'].iloc[3] == 100003.0  # +1
    
    def test_long_with_contract_multiplier(self):
        """
        TEST B2: Long with contract_size multiplier
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 101, 102, 103], index=dates)
        positions = pd.Series([1, 1, 1, 1], index=dates)
        
        config = BacktestConfig(
            initial_capital=100000.0,
            contract_size=50.0,  # Each point worth $50
            commission=0.0,
            slippage=0.0
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should gain 3 points * $50 = $150
        expected_pnl = 3.0 * 50.0
        assert results['equity'].iloc[-1] == 100000.0 + expected_pnl


class TestShortPositionPnL:
    """Test short position PnL calculation"""
    
    def test_short_1_contract_correct_pnl(self):
        """
        TEST C: Short 1 contract produces correct PnL
        
        Given:
            Short from 100 → 98 = +2 * contract_size (profit from price drop)
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 99, 98, 97], index=dates)
        positions = pd.Series([-1, -1, -1, -1], index=dates)  # Short entire time
        
        config = BacktestConfig(
            initial_capital=100000.0,
            contract_size=1.0,
            commission=0.0,
            slippage=0.0
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should gain 3 points from price drop (100 -> 97)
        expected_pnl = 3.0
        assert results['equity'].iloc[-1] == 100000.0 + expected_pnl
        
        # Check per-bar
        assert results['equity'].iloc[0] == 100000.0
        assert results['equity'].iloc[1] == 100001.0  # Price dropped 1
        assert results['equity'].iloc[2] == 100002.0  # Price dropped 1 more
        assert results['equity'].iloc[3] == 100003.0  # Price dropped 1 more


class TestCommissionSlippage:
    """Test commission and slippage application"""
    
    def test_commission_applied_once_per_entry(self):
        """
        TEST D1: Commission + slippage applied exactly once per position change
        
        Case: flat → long (commission once)
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 100, 100, 100], index=dates)  # No price movement
        positions = pd.Series([0, 1, 1, 1], index=dates)  # Enter long at bar 1
        
        config = BacktestConfig(
            initial_capital=100000.0,
            commission=10.0,  # $10 per trade
            slippage=5.0,     # $5 per trade
            contracts=1
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should deduct commission+slippage once at entry
        expected_cost = 10.0 + 5.0
        assert results['equity'].iloc[1] == 100000.0 - expected_cost
        
        # No further costs (no price movement, no position changes)
        assert results['equity'].iloc[2] == 100000.0 - expected_cost
        assert results['equity'].iloc[3] == 100000.0 - expected_cost
    
    def test_commission_twice_on_flip(self):
        """
        TEST D2: long → short (commission twice: exit + entry)
        """
        dates = create_test_data(5)
        prices = pd.Series([100, 100, 100, 100, 100], index=dates)
        positions = pd.Series([0, 1, 1, -1, -1], index=dates)  # Long then flip to short
        
        config = BacktestConfig(
            initial_capital=100000.0,
            commission=10.0,
            slippage=5.0,
            contracts=1
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Bar 1: Enter long → -15
        # Bar 3: Flip to short → -30 total (exit long -15, enter short -15)
        expected_cost_after_flip = (10.0 + 5.0) * 3  # Entry + exit + entry
        assert results['equity'].iloc[3] == 100000.0 - expected_cost_after_flip
    
    def test_commission_once_on_exit(self):
        """
        TEST D3: short → flat (commission once)
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 100, 100, 100], index=dates)
        positions = pd.Series([-1, -1, -1, 0], index=dates)  # Short then exit
        
        config = BacktestConfig(
            initial_capital=100000.0,
            commission=10.0,
            slippage=5.0,
            contracts=1
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Bar 0: Enter short → -15
        # Bar 3: Exit short → -30 total
        expected_cost = (10.0 + 5.0) * 2
        assert results['equity'].iloc[3] == 100000.0 - expected_cost


class TestNoGhostPnL:
    """Test that no PnL occurs when price doesn't move"""
    
    def test_no_ghost_pnl_flat_price(self):
        """
        TEST E: Ensure no "ghost PnL" when price doesn't move
        """
        dates = create_test_data(10)
        prices = pd.Series([100] * 10, index=dates)  # Price constant
        positions = pd.Series([1] * 10, index=dates)  # Long entire time
        
        config = BacktestConfig(
            initial_capital=100000.0,
            commission=0.0,
            slippage=0.0
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Equity should not change (except entry bar)
        for i in range(1, 10):
            assert results['equity'].iloc[i] == 100000.0, f"Bar {i} should have no PnL"


class TestIndexAlignment:
    """Test index alignment validation"""
    
    def test_mismatched_indices_raises_error(self):
        """
        TEST F: Prices and positions must share exact same index
        
        Otherwise: ValueError("Price and position indices do not match")
        """
        dates1 = pd.date_range('2020-01-01', periods=5, freq='D')
        dates2 = pd.date_range('2020-02-01', periods=5, freq='D')  # Different dates
        
        prices = pd.Series([100, 101, 102, 103, 104], index=dates1)
        positions = pd.Series([1, 1, 1, 1, 1], index=dates2)  # Mismatched index
        
        config = BacktestConfig()
        backtester = Backtester(config)
        
        with pytest.raises(ValueError, match="Price and position indices do not match"):
            backtester.run(prices, positions)
    
    def test_matching_indices_no_error(self):
        """
        TEST F2: Matching indices should work without error
        """
        dates = create_test_data(5)
        prices = pd.Series([100, 101, 102, 103, 104], index=dates)
        positions = pd.Series([1, 1, 1, 1, 1], index=dates)
        
        config = BacktestConfig()
        backtester = Backtester(config)
        
        # Should not raise
        results = backtester.run(prices, positions)
        assert len(results['equity']) == len(prices)
    
    def test_empty_series_raises_error(self):
        """
        TEST F3: Empty price series should raise error
        """
        dates = pd.date_range('2020-01-01', periods=0, freq='D')
        prices = pd.Series([], index=dates, dtype=float)
        positions = pd.Series([], index=dates, dtype=int)
        
        config = BacktestConfig()
        backtester = Backtester(config)
        
        with pytest.raises(ValueError, match="Price series is empty"):
            backtester.run(prices, positions)


class TestMultipleContracts:
    """Test backtesting with multiple contracts"""
    
    def test_multiple_contracts_multiplies_pnl(self):
        """
        TEST: 3 contracts should multiply PnL by 3
        """
        dates = create_test_data(4)
        prices = pd.Series([100, 101, 102, 103], index=dates)
        positions = pd.Series([1, 1, 1, 1], index=dates)
        
        config = BacktestConfig(
            initial_capital=100000.0,
            contract_size=1.0,
            contracts=3,  # 3 contracts
            commission=0.0,
            slippage=0.0
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # 3 points * 3 contracts = 9 points total
        expected_pnl = 3.0 * 3
        assert results['equity'].iloc[-1] == 100000.0 + expected_pnl


class TestTradeExtraction:
    """Test trade extraction logic"""
    
    def test_single_long_trade_extracted(self):
        """
        TEST: Single long trade should be extracted with correct PnL
        """
        dates = create_test_data(5)
        prices = pd.Series([100, 101, 102, 103, 104], index=dates)
        positions = pd.Series([0, 1, 1, 1, 0], index=dates)  # Enter bar 1, exit bar 4
        
        config = BacktestConfig(
            initial_capital=100000.0,
            commission=0.0,
            slippage=0.0
        )
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should have 1 trade
        assert len(results['trades']) == 1
        
        trade = results['trades'].iloc[0]
        assert trade['direction'] == 'long'
        assert trade['entry_price'] == 101
        assert trade['exit_price'] == 103  # Exits at previous bar's close
        assert trade['pnl'] > 0
    
    def test_long_short_trades_extracted(self):
        """
        TEST: Multiple trades extracted correctly
        """
        dates = create_test_data(10)
        prices = pd.Series([100, 101, 102, 103, 100, 99, 98, 100, 101, 102], index=dates)
        positions = pd.Series([0, 1, 1, 1, 0, -1, -1, -1, 0, 0], index=dates)
        
        config = BacktestConfig(commission=0.0, slippage=0.0)
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should have 2 trades
        assert len(results['trades']) == 2
        
        # First trade: long
        assert results['trades'].iloc[0]['direction'] == 'long'
        
        # Second trade: short
        assert results['trades'].iloc[1]['direction'] == 'short'


class TestDeterminism:
    """Test deterministic behavior"""
    
    def test_multiple_runs_identical(self):
        """
        TEST: Multiple runs with same inputs produce identical results
        """
        dates = create_test_data(10)
        prices = pd.Series([100, 101, 102, 101, 100, 99, 100, 101, 102, 103], index=dates)
        positions = pd.Series([0, 1, 1, 1, -1, -1, -1, 1, 1, 1], index=dates)
        
        config = BacktestConfig()
        backtester = Backtester(config)
        
        # Run 3 times
        results1 = backtester.run(prices, positions)
        results2 = backtester.run(prices, positions)
        results3 = backtester.run(prices, positions)
        
        # All should be identical
        pd.testing.assert_series_equal(results1['equity'], results2['equity'])
        pd.testing.assert_series_equal(results2['equity'], results3['equity'])
        
        assert results1['stats']['total_pnl'] == results2['stats']['total_pnl']
        assert results2['stats']['total_pnl'] == results3['stats']['total_pnl']


class TestStatistics:
    """Test statistics calculation"""
    
    def test_win_rate_calculation(self):
        """
        TEST: Win rate calculated correctly
        """
        dates = create_test_data(8)
        # Profitable long trade
        prices = pd.Series([100, 101, 102, 103, 103, 102, 101, 100], index=dates)
        positions = pd.Series([0, 1, 1, 1, 0, 0, 0, 0], index=dates)  # One profitable long
        
        config = BacktestConfig(commission=0.0, slippage=0.0)
        backtester = Backtester(config)
        
        results = backtester.run(prices, positions)
        
        # Should have 1 trade that is profitable
        assert results['stats']['total_trades'] >= 1
        assert results['stats']['winning_trades'] >= 1
        assert results['stats']['total_return'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

