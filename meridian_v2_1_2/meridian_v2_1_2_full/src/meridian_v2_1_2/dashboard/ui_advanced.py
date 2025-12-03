"""
Advanced Dashboard UI for Meridian v2.1.2

Extended dashboard with pro-level visualizations.
Integrates with ui.py as additional views.
"""

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from .dashboard_config import DashboardConfig
from .data_api import DashboardAPI
from .ui_components_ext import (
    render_pnl_multi_view,
    render_trade_drilldown,
    render_risk_matrix,
    render_shadow_heatmap,
    render_oversight_timeline,
    render_notifications,
    render_activity_feed,
    render_regime_context
)


def render_advanced_analytics(api):
    """Render advanced analytics tab"""
    st.header("📊 Advanced Analytics")
    
    tab1, tab2, tab3 = st.tabs(["PnL Analysis", "Risk Matrix", "Regime Context"])
    
    with tab1:
        render_pnl_multi_view(api)
    
    with tab2:
        render_risk_matrix(api)
    
    with tab3:
        render_regime_context(api)


def render_investigate(api):
    """Render investigation tab"""
    st.header("🔍 Trade Investigation")
    
    tab1, tab2, tab3 = st.tabs(["Trade Drill-Down", "Oversight Timeline", "Shadow Heatmap"])
    
    with tab1:
        render_trade_drilldown(api)
    
    with tab2:
        render_oversight_timeline(api)
    
    with tab3:
        render_shadow_heatmap(api)


def render_events(api):
    """Render events and notifications tab"""
    st.header("📨 Events & Notifications")
    
    tab1, tab2 = st.tabs(["Activity Feed", "Notifications"])
    
    with tab1:
        render_activity_feed(api)
    
    with tab2:
        render_notifications(api)


def add_advanced_navigation():
    """
    Add advanced views to dashboard navigation.
    
    Call this from main ui.py to add new pages.
    """
    return [
        "📊 Advanced Analytics",
        "🔍 Investigate",
        "📨 Events & Notifications"
    ]

