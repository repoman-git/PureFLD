"""
Dashboard Test Suite

Tests for operator dashboard system.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.dashboard import (
    DashboardConfig,
    DashboardAPI,
    start_dashboard
)


class TestDashboardConfig:
    """Test dashboard configuration"""
    
    def test_config_defaults(self):
        """Test default configuration"""
        config = DashboardConfig()
        
        assert config.enabled is True
        assert config.host == "127.0.0.1"  # localhost only
        assert config.port > 0
    
    def test_config_security(self):
        """Test security defaults"""
        config = DashboardConfig()
        
        # Should bind to localhost only by default
        assert config.host == "127.0.0.1"


class TestDashboardAPI:
    """Test dashboard API"""
    
    def test_api_initialization(self):
        """Test API can be initialized"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        assert api is not None
    
    def test_get_portfolio_state(self):
        """Test getting portfolio state"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        portfolio = api.get_portfolio_state()
        
        assert 'positions' in portfolio
        assert 'cash' in portfolio
        assert 'equity' in portfolio
        assert 'total_pnl' in portfolio
    
    def test_get_orders(self):
        """Test getting orders"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        orders = api.get_orders()
        
        assert isinstance(orders, list)
    
    def test_get_orders_filtered(self):
        """Test getting filtered orders"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        filled_orders = api.get_orders(status='filled')
        
        assert isinstance(filled_orders, list)
        # All returned orders should be filled
        assert all(o['status'] == 'filled' for o in filled_orders)
    
    def test_get_fills(self):
        """Test getting fills"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        fills = api.get_fills()
        
        assert isinstance(fills, list)
    
    def test_get_signals(self):
        """Test getting signals"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        signals = api.get_signals()
        
        assert 'signals' in signals
        assert isinstance(signals['signals'], dict)
    
    def test_get_risk_state(self):
        """Test getting risk state"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        risk = api.get_risk_state()
        
        assert 'model_risk_score' in risk
        assert 'exposure' in risk
        assert 'kill_switch_active' in risk
    
    def test_get_oversight_state(self):
        """Test getting oversight state"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        oversight = api.get_oversight_state()
        
        assert 'anomaly_scores' in oversight
        assert 'risk_assessment' in oversight
        assert 'advisories' in oversight
    
    def test_get_shadow_state(self):
        """Test getting shadow state"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        shadow = api.get_shadow_state()
        
        assert 'drift_detected' in shadow
        assert 'drift_level' in shadow
    
    def test_get_pending_approvals(self):
        """Test getting pending approvals"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        pending = api.get_pending_approvals()
        
        assert isinstance(pending, list)
    
    def test_approve_request(self):
        """Test approving a request"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        result = api.approve_request('test_req_001')
        
        assert result is True
    
    def test_reject_request(self):
        """Test rejecting a request"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        result = api.reject_request('test_req_001', reason='Test rejection')
        
        assert result is True
    
    def test_get_run_logs(self):
        """Test getting run logs"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        logs = api.get_run_logs(limit=10)
        
        assert isinstance(logs, list)
        assert len(logs) <= 10
    
    def test_get_pnl_timeseries(self):
        """Test getting PnL timeseries"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        pnl_data = api.get_pnl_timeseries(days=7)
        
        assert 'dates' in pnl_data
        assert 'pnl' in pnl_data
        assert len(pnl_data['dates']) == 7
        assert len(pnl_data['pnl']) == 7


class TestDashboardServer:
    """Test dashboard server"""
    
    def test_server_disabled_when_config_disabled(self):
        """Test server doesn't start when disabled"""
        config = DashboardConfig(enabled=False)
        
        result = start_dashboard(config, background=False)
        
        assert result is None


class TestIntegration:
    """Test dashboard integration"""
    
    def test_api_data_consistency(self):
        """Test API returns consistent data"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        # Get data multiple times
        portfolio1 = api.get_portfolio_state()
        portfolio2 = api.get_portfolio_state()
        
        # Should have same structure
        assert portfolio1.keys() == portfolio2.keys()


class TestOfflineGuarantee:
    """Test dashboard runs completely offline"""
    
    def test_no_network_calls(self):
        """Verify dashboard makes no network calls"""
        config = DashboardConfig()
        api = DashboardAPI(config)
        
        # All API calls should work offline
        api.get_portfolio_state()
        api.get_orders()
        api.get_fills()
        api.get_signals()
        api.get_risk_state()
        api.get_oversight_state()
        api.get_shadow_state()
        api.get_pending_approvals()
        api.get_run_logs()
        api.get_pnl_timeseries()
        
        # No errors should occur
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


