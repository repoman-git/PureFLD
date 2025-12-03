"""
Comprehensive test suite for Mode Routing in Meridian v2.1.2.

Tests verify research, paper, and live mode separation and safety gates.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import pytest
import pandas as pd

from meridian_v2_1_2 import MeridianConfig
from meridian_v2_1_2.modes import (
    ResearchSettings,
    PaperSettings,
    LiveSettings,
    validate_research_mode,
    validate_paper_mode,
    validate_live_mode,
    route_by_mode
)


def create_test_data(length=50):
    """Create synthetic test data"""
    dates = pd.date_range('2020-01-01', periods=length, freq='D')
    prices = pd.Series(range(100, 100 + length), index=dates)
    return prices


class TestModeValidation:
    """Test mode validation"""
    
    def test_valid_modes_accepted(self):
        """
        TEST 1: Valid modes are accepted
        """
        # Research mode
        config_research = MeridianConfig(mode="research")
        assert config_research.mode == "research"
        
        # Paper mode
        config_paper = MeridianConfig(mode="paper")
        assert config_paper.mode == "paper"
        
        # Live mode
        config_live = MeridianConfig(mode="live")
        assert config_live.mode == "live"
    
    def test_invalid_mode_rejected(self):
        """
        TEST: Invalid mode raises error
        """
        with pytest.raises(ValueError, match="mode must be one of"):
            MeridianConfig(mode="invalid")
        
        with pytest.raises(ValueError, match="mode must be one of"):
            MeridianConfig(mode="production")


class TestResearchMode:
    """Test research mode behavior"""
    
    def test_research_mode_allows_sweeps(self):
        """
        TEST 2: Research mode allows sweeps
        """
        config = MeridianConfig(mode="research")
        config.sweep.enable_sweep = True
        
        # Should not raise error
        validate_research_mode(config)
    
    def test_research_mode_allows_walkforward(self):
        """
        TEST: Research mode allows walk-forward
        """
        config = MeridianConfig(mode="research")
        config.walkforward.enable_walkforward = True
        
        # Should not raise error
        validate_research_mode(config)
    
    def test_research_mode_runs_successfully(self):
        """
        TEST: Research mode executes backtest
        """
        config = MeridianConfig(mode="research")
        prices = create_test_data(50)
        
        results = route_by_mode(config, prices=prices)
        
        assert results['mode'] == 'research'
        assert 'equity' in results
        assert results['execution_type'] == 'ideal_backtest'


class TestPaperMode:
    """Test paper trading mode behavior"""
    
    def test_paper_mode_executes(self):
        """
        TEST 3: Paper mode executes with simulation
        """
        config = MeridianConfig(mode="paper")
        prices = create_test_data(50)
        
        results = route_by_mode(config, prices=prices)
        
        assert results['mode'] == 'paper'
        assert 'equity' in results
        assert results['execution_type'] == 'simulated_with_slippage'
        assert results['slippage_applied'] == True
    
    def test_paper_mode_allows_sweeps(self):
        """
        TEST: Paper mode can run sweeps (for testing)
        """
        config = MeridianConfig(mode="paper")
        config.sweep.enable_sweep = True
        
        # Should not raise error
        validate_paper_mode(config)


class TestLiveMode:
    """Test live trading mode safety"""
    
    def test_live_mode_requires_broker_connection(self):
        """
        TEST 4: Live mode requires broker_connected=True
        """
        config = MeridianConfig(mode="live")
        prices = create_test_data(50)
        
        # Without broker connection → should raise
        with pytest.raises(ValueError, match="broker_connected"):
            route_by_mode(config, prices=prices, broker_connected=False)
    
    def test_live_mode_disallows_sweeps(self):
        """
        TEST: Live mode disallows sweeps
        """
        config = MeridianConfig(mode="live")
        config.sweep.enable_sweep = True
        
        # Should raise error
        with pytest.raises(ValueError, match="Sweeps not allowed"):
            validate_live_mode(config)
    
    def test_live_mode_disallows_walkforward(self):
        """
        TEST: Live mode disallows walk-forward
        """
        config = MeridianConfig(mode="live")
        config.walkforward.enable_walkforward = True
        
        # Should raise error
        with pytest.raises(ValueError, match="Walk-forward not allowed"):
            validate_live_mode(config)
    
    def test_live_mode_with_broker_connection(self):
        """
        TEST: Live mode with broker connection executes
        """
        config = MeridianConfig(mode="live")
        prices = create_test_data(50)
        
        results = route_by_mode(config, prices=prices, broker_connected=True)
        
        assert results['mode'] == 'live'
        assert results['execution_type'] == 'real_broker'
        assert results['safety'] == 'kill_switches_enabled'


class TestModeSeparation:
    """Test that modes are properly separated"""
    
    def test_research_cannot_access_live_features(self):
        """
        TEST 5: Research mode doesn't access live-only features
        """
        config = MeridianConfig(mode="research")
        settings = ResearchSettings()
        
        assert settings.allow_live_orders == False
        assert settings.allow_execution_engine == False
        assert settings.allow_oms == False
    
    def test_modes_produce_different_execution_types(self):
        """
        TEST: Each mode produces appropriate execution type
        """
        prices = create_test_data(50)
        
        # Research
        config_research = MeridianConfig(mode="research")
        results_research = route_by_mode(config_research, prices=prices)
        assert results_research['execution_type'] == 'ideal_backtest'
        
        # Paper
        config_paper = MeridianConfig(mode="paper")
        results_paper = route_by_mode(config_paper, prices=prices)
        assert results_paper['execution_type'] == 'simulated_with_slippage'
        
        # Live (with broker)
        config_live = MeridianConfig(mode="live")
        results_live = route_by_mode(config_live, prices=prices, broker_connected=True)
        assert results_live['execution_type'] == 'real_broker'


class TestDeterminism:
    """Test deterministic behavior across modes"""
    
    def test_research_mode_deterministic(self):
        """
        TEST 6: Research mode is deterministic
        """
        config = MeridianConfig(mode="research")
        prices = create_test_data(50)
        
        results1 = route_by_mode(config, prices=prices)
        results2 = route_by_mode(config, prices=prices)
        
        # Equity curves should match
        pd.testing.assert_series_equal(results1['equity'], results2['equity'])


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

