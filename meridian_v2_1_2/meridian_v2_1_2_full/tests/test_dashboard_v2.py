"""
Dashboard v2 Test Suite

Tests for multi-strategy dashboard components.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime

from meridian_v2_1_2.dashboard_v2 import MultiStrategyRouter, MultiStrategyAPI
from meridian_v2_1_2.dashboard_v2.multi_strategy_router import StrategyState
from meridian_v2_1_2.dashboard_v2.components import (
    PortfolioOverview,
    StrategyCards,
    StrategyComparison,
    AllocationPanel,
    CombinedPnL,
    CorrelationMap,
    MultiApprovals,
    PortfolioHeatmap
)


class TestMultiStrategyRouter:
    """Test multi-strategy router"""
    
    def test_router_initialization(self):
        """Test router can be initialized"""
        router = MultiStrategyRouter()
        assert router is not None
        assert len(router.strategies) == 0
    
    def test_register_strategy(self):
        """Test strategy registration"""
        router = MultiStrategyRouter()
        
        # Create mock strategy
        class MockStrategy:
            def get_state(self):
                return {'pnl': 1000.0}
        
        strategy = MockStrategy()
        router.register_strategy("test_strategy", strategy)
        
        assert "test_strategy" in router.list_strategies()
    
    def test_unregister_strategy(self):
        """Test strategy unregistration"""
        router = MultiStrategyRouter()
        
        class MockStrategy:
            pass
        
        router.register_strategy("test", MockStrategy())
        router.unregister_strategy("test")
        
        assert "test" not in router.list_strategies()
    
    def test_aggregate_portfolio_empty(self):
        """Test portfolio aggregation with no strategies"""
        router = MultiStrategyRouter()
        
        portfolio = router.aggregate_portfolio_state()
        
        assert portfolio['total_pnl'] == 0.0
        assert portfolio['num_strategies'] == 0
    
    def test_aggregate_portfolio_with_strategies(self):
        """Test portfolio aggregation with strategies"""
        router = MultiStrategyRouter()
        
        # Register mock strategies first
        class MockStrategy:
            pass
        
        router.register_strategy("strat1", MockStrategy())
        router.register_strategy("strat2", MockStrategy())
        
        # Add mock states
        state1 = StrategyState(
            name="strat1",
            pnl=1000.0,
            exposure=5000.0,
            risk_score=2.5,
            signals={},
            shadow_state={},
            health={'status': 'ok'},
            allocation=0.5,
            last_update=datetime.now()
        )
        
        state2 = StrategyState(
            name="strat2",
            pnl=500.0,
            exposure=3000.0,
            risk_score=1.5,
            signals={},
            shadow_state={},
            health={'status': 'ok'},
            allocation=0.5,
            last_update=datetime.now()
        )
        
        router.update_strategy_state("strat1", state1)
        router.update_strategy_state("strat2", state2)
        
        portfolio = router.aggregate_portfolio_state()
        
        assert portfolio['total_pnl'] == 1500.0
        assert portfolio['total_exposure'] == 8000.0
        assert portfolio['total_risk'] == 4.0


class TestMultiStrategyAPI:
    """Test multi-strategy API"""
    
    def test_api_initialization(self):
        """Test API initialization"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        assert api is not None
    
    def test_get_strategies(self):
        """Test get strategies endpoint"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        result = api.get_strategies()
        
        assert 'strategies' in result
        assert 'count' in result
        assert result['count'] == 0
    
    def test_get_portfolio_overview(self):
        """Test portfolio overview endpoint"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        result = api.get_portfolio_overview()
        
        assert 'total_pnl' in result
        assert 'num_strategies' in result
    
    def test_get_portfolio_risk(self):
        """Test portfolio risk endpoint"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        result = api.get_portfolio_risk()
        
        assert 'total_risk' in result
        assert 'strategies' in result


class TestComponents:
    """Test dashboard components"""
    
    def test_portfolio_overview(self):
        """Test portfolio overview component"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        component = PortfolioOverview(api)
        data = component.get_data()
        
        assert 'total_pnl' in data
        assert 'num_strategies' in data
    
    def test_strategy_cards(self):
        """Test strategy cards component"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        component = StrategyCards(api)
        cards = component.get_data()
        
        assert isinstance(cards, list)
    
    def test_allocation_panel(self):
        """Test allocation panel component"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        component = AllocationPanel(api)
        data = component.get_data()
        
        assert 'allocations' in data
    
    def test_allocation_validation(self):
        """Test allocation validation"""
        router = MultiStrategyRouter()
        api = MultiStrategyAPI(router)
        
        component = AllocationPanel(api)
        
        # Valid allocation
        result = component.validate_allocations({'strat1': 0.6, 'strat2': 0.4})
        assert result['valid'] is True
        
        # Invalid (doesn't sum to 1.0)
        result = component.validate_allocations({'strat1': 0.8, 'strat2': 0.4})
        assert result['valid'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

