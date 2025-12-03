"""
Comprehensive test suite for Portfolio Engine in Meridian v2.1.2.

Tests verify multi-asset allocation, exposure management, and correlation handling.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd
import numpy as np

from meridian_v2_1_2.config import PortfolioConfig
from meridian_v2_1_2.portfolio import (
    allocate_capital,
    compute_portfolio_weights,
    compute_exposures,
    enforce_exposure_limits,
    compute_correlation_matrix,
    manage_correlation_risk,
    compute_portfolio_volatility,
    target_portfolio_volatility,
    combine_positions,
    aggregate_pnl
)


def create_multi_asset_data(symbols=['GC', 'SI', 'CL'], length=100):
    """Create synthetic multi-asset data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    
    prices = {}
    for i, symbol in enumerate(symbols):
        # Each asset has different price level and trend
        prices[symbol] = pd.Series(
            range(100 + i*50, 100 + i*50 + length),
            index=dates
        )
    
    return prices, dates


class TestEqualWeightAllocation:
    """Test equal weight portfolio allocation"""
    
    def test_equal_weight_splits_capital(self):
        """
        TEST 1: Equal weight allocation splits capital equally
        """
        prices, dates = create_multi_asset_data(symbols=['A', 'B', 'C'], length=50)
        
        # Create signals (all long)
        signals = {sym: pd.Series([1] * 50, index=dates) for sym in ['A', 'B', 'C']}
        
        # Base sizes (all 1.0)
        position_sizes = {sym: pd.Series([1.0] * 50, index=dates) for sym in ['A', 'B', 'C']}
        
        config = PortfolioConfig(allocation_method="equal_weight")
        
        allocated = allocate_capital(signals, position_sizes, config)
        
        # Each should get 1/3
        assert abs(allocated['A'].iloc[0] - 0.333) < 0.01
        assert abs(allocated['B'].iloc[0] - 0.333) < 0.01
        assert abs(allocated['C'].iloc[0] - 0.333) < 0.01


class TestExposureManagement:
    """Test exposure calculation and enforcement"""
    
    def test_compute_exposures_correct(self):
        """
        TEST 2: Exposure calculation is correct
        """
        prices, dates = create_multi_asset_data(symbols=['A', 'B'], length=10)
        
        # Long A (1 contract × 100 price = 100)
        # Short B (- 1 contract × 150 price = -150)
        positions = {
            'A': pd.Series([1.0] * 10, index=dates),
            'B': pd.Series([-1.0] * 10, index=dates)
        }
        
        exposures = compute_exposures(positions, prices)
        
        # Gross = |100| + |-150| = 250
        assert abs(exposures['gross_exposure'].iloc[0] - 250) < 1
        
        # Net = 100 + (-150) = -50
        assert abs(exposures['net_exposure'].iloc[0] - (-50)) < 1
    
    def test_exposure_limits_enforced(self):
        """
        TEST 3: Exposure limits scale down positions
        """
        prices, dates = create_multi_asset_data(symbols=['A', 'B'], length=10)
        
        # Large positions that violate limits
        positions = {
            'A': pd.Series([10.0] * 10, index=dates),  # 10 × 100 = 1000
            'B': pd.Series([10.0] * 10, index=dates)   # 10 × 150 = 1500
        }
        
        config = PortfolioConfig(
            starting_capital=100000,
            max_gross_exposure=0.5  # Only allow 50k gross
        )
        
        limited = enforce_exposure_limits(positions, prices, config)
        
        # Gross exposure should be scaled down
        exposures_after = compute_exposures(limited, prices)
        
        # Should be <= 50k
        assert exposures_after['gross_exposure'].iloc[0] <= 50000 * 1.01  # Allow 1% tolerance


class TestCorrelationManagement:
    """Test correlation-aware risk management"""
    
    def test_correlation_matrix_computed(self):
        """
        TEST 4: Correlation matrix computation
        """
        # Create correlated assets
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        
        base = np.random.RandomState(42).randn(100).cumsum() + 100
        
        prices = {
            'A': pd.Series(base, index=dates),
            'B': pd.Series(base * 1.1 + 5, index=dates),  # Highly correlated with A
            'C': pd.Series(np.random.RandomState(43).randn(100).cumsum() + 100, index=dates)  # Independent
        }
        
        corr_matrix = compute_correlation_matrix(prices, lookback=90)
        
        # A and B should be highly correlated
        assert corr_matrix.loc['A', 'B'] > 0.9
    
    def test_high_correlation_reduces_weights(self):
        """
        TEST: High correlation between assets reduces their weights
        """
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        
        # Create highly correlated assets
        base = np.random.RandomState(42).randn(100).cumsum() + 100
        
        prices = {
            'A': pd.Series(base, index=dates),
            'B': pd.Series(base * 1.05, index=dates)  # Almost identical
        }
        
        positions = {
            'A': pd.Series([1.0] * 100, index=dates),
            'B': pd.Series([1.0] * 100, index=dates)
        }
        
        config = PortfolioConfig(
            use_correlation_matrix=True,
            max_correlation=0.75,
            correlation_lookback=90
        )
        
        adjusted = manage_correlation_risk(positions, prices, config)
        
        # Positions should be reduced
        assert adjusted['A'].iloc[-1] < positions['A'].iloc[-1]


class TestPortfolioVolatility:
    """Test portfolio volatility targeting"""
    
    def test_portfolio_vol_computation(self):
        """
        TEST 5: Portfolio volatility computed correctly
        """
        prices, dates = create_multi_asset_data(symbols=['A', 'B'], length=100)
        
        positions = {
            'A': pd.Series([1.0] * 100, index=dates),
            'B': pd.Series([1.0] * 100, index=dates)
        }
        
        port_vol = compute_portfolio_volatility(positions, prices, lookback=20)
        
        # Should have valid volatility
        assert len(port_vol) == len(dates)
        assert port_vol.iloc[-1] >= 0


class TestPortfolioUtils:
    """Test portfolio utility functions"""
    
    def test_combine_positions(self):
        """
        TEST 6: Combine positions from multiple strategies
        """
        dates = pd.date_range('2020-01-01', periods=10, freq='D')
        
        positions_dict = {
            'strategy1': {
                'A': pd.Series([1.0] * 10, index=dates),
                'B': pd.Series([0.5] * 10, index=dates)
            },
            'strategy2': {
                'A': pd.Series([0.5] * 10, index=dates),
                'C': pd.Series([1.0] * 10, index=dates)
            }
        }
        
        combined = combine_positions(positions_dict)
        
        # A should have 1.0 + 0.5 = 1.5
        assert combined['A'].iloc[0] == 1.5
        
        # B should have 0.5
        assert combined['B'].iloc[0] == 0.5
        
        # C should have 1.0
        assert combined['C'].iloc[0] == 1.0
    
    def test_aggregate_pnl(self):
        """
        TEST: Aggregate PnL across assets
        """
        trades_dict = {
            'A': pd.DataFrame({'pnl': [10, 20], 'entry_price': [100, 100]}),
            'B': pd.DataFrame({'pnl': [15, -5], 'entry_price': [150, 150]})
        }
        
        aggregated = aggregate_pnl(trades_dict)
        
        # Should have 4 trades total
        assert len(aggregated) == 4
        
        # Should have symbol column
        assert 'symbol' in aggregated.columns


class TestDeterminism:
    """Test that portfolio functions are deterministic"""
    
    def test_allocation_deterministic(self):
        """
        TEST 7: Portfolio allocation is deterministic
        """
        prices, dates = create_multi_asset_data(length=50)
        
        signals = {sym: pd.Series([1] * 50, index=dates) for sym in prices.keys()}
        position_sizes = {sym: pd.Series([1.0] * 50, index=dates) for sym in prices.keys()}
        
        config = PortfolioConfig(allocation_method="equal_weight")
        
        allocated1 = allocate_capital(signals, position_sizes, config)
        allocated2 = allocate_capital(signals, position_sizes, config)
        
        for symbol in allocated1.keys():
            pd.testing.assert_series_equal(allocated1[symbol], allocated2[symbol])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

