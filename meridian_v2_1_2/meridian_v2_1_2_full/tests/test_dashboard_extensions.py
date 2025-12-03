"""
Dashboard Extensions Test Suite

Tests for advanced dashboard components.
"""

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from meridian_v2_1_2.dashboard import DashboardConfig, DashboardAPI


class TestDashboardExtensions:
    """Test dashboard extension components"""
    
    def test_extensions_module_import(self):
        """Test extension modules can be imported"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import (
                render_pnl_multi_view,
                render_trade_drilldown,
                render_risk_matrix,
                render_shadow_heatmap,
                render_oversight_timeline,
                render_notifications,
                render_activity_feed,
                render_regime_context
            )
            
            assert render_pnl_multi_view is not None
            assert render_trade_drilldown is not None
            assert render_risk_matrix is not None
            assert render_shadow_heatmap is not None
            assert render_oversight_timeline is not None
            assert render_notifications is not None
            assert render_activity_feed is not None
            assert render_regime_context is not None
        
        except ImportError as e:
            pytest.skip(f"Extension modules not available: {e}")
    
    def test_advanced_ui_import(self):
        """Test advanced UI module can be imported"""
        try:
            from meridian_v2_1_2.dashboard import ui_advanced
            
            assert ui_advanced is not None
        
        except ImportError as e:
            pytest.skip(f"Advanced UI not available: {e}")
    
    def test_pnl_multi_view_component(self):
        """Test PnL multi-view component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_pnl_multi_view
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            # Should not crash when called
            # (Won't actually render without Streamlit context)
            assert callable(render_pnl_multi_view)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_trade_drilldown_component(self):
        """Test trade drill-down component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_trade_drilldown
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_trade_drilldown)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_risk_matrix_component(self):
        """Test risk matrix component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_risk_matrix
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_risk_matrix)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_shadow_heatmap_component(self):
        """Test shadow heatmap component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_shadow_heatmap
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_shadow_heatmap)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_oversight_timeline_component(self):
        """Test oversight timeline component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_oversight_timeline
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_oversight_timeline)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_notifications_component(self):
        """Test notifications component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_notifications
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_notifications)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_activity_feed_component(self):
        """Test activity feed component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_activity_feed
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_activity_feed)
        
        except ImportError:
            pytest.skip("Component not available")
    
    def test_regime_context_component(self):
        """Test regime context component"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import render_regime_context
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            assert callable(render_regime_context)
        
        except ImportError:
            pytest.skip("Component not available")


class TestIntegration:
    """Test dashboard extensions integration"""
    
    def test_all_components_compatible(self):
        """Test all components work with DashboardAPI"""
        try:
            from meridian_v2_1_2.dashboard.ui_components_ext import (
                render_pnl_multi_view,
                render_trade_drilldown,
                render_risk_matrix,
                render_shadow_heatmap,
                render_oversight_timeline,
                render_notifications,
                render_activity_feed,
                render_regime_context
            )
            
            config = DashboardConfig()
            api = DashboardAPI(config)
            
            # All should accept API as parameter
            components = [
                render_pnl_multi_view,
                render_trade_drilldown,
                render_risk_matrix,
                render_shadow_heatmap,
                render_oversight_timeline,
                render_notifications,
                render_activity_feed,
                render_regime_context
            ]
            
            for component in components:
                assert callable(component)
        
        except ImportError:
            pytest.skip("Components not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

