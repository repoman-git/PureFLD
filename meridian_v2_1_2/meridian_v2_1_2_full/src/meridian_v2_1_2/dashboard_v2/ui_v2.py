"""
Dashboard v2 Main UI

Multi-strategy portfolio dashboard interface.
"""

import streamlit as st
from typing import Dict, Any

from .multi_strategy_router import MultiStrategyRouter
from .multi_strategy_api import MultiStrategyAPI
from .components import (
    PortfolioOverview,
    StrategyCards,
    StrategyComparison,
    AllocationPanel,
    CombinedPnL,
    CorrelationMap,
    MultiApprovals,
    PortfolioHeatmap
)


class DashboardV2:
    """
    Main Dashboard v2 UI.
    
    Multi-strategy portfolio visualization and control.
    """
    
    def __init__(self):
        """Initialize dashboard"""
        # Initialize router and API
        self.router = MultiStrategyRouter()
        self.api = MultiStrategyAPI(self.router)
        
        # Initialize components
        self.portfolio_overview = PortfolioOverview(self.api)
        self.strategy_cards = StrategyCards(self.api)
        self.strategy_comparison = StrategyComparison(self.api)
        self.allocation_panel = AllocationPanel(self.api)
        self.combined_pnl = CombinedPnL(self.api)
        self.correlation_map = CorrelationMap(self.api)
        self.multi_approvals = MultiApprovals(self.api)
        self.portfolio_heatmap = PortfolioHeatmap(self.api)
    
    def render(self):
        """
        Render dashboard.
        
        Note: This is a backend-focused implementation.
        Full Streamlit UI integration would go here.
        """
        # Page config
        st.set_page_config(
            page_title="Meridian Dashboard v2",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 Meridian Dashboard v2 - Multi-Strategy Portfolio")
        
        # Main tabs
        tabs = st.tabs([
            "Portfolio Overview",
            "Strategies",
            "Comparison",
            "Allocations",
            "PnL Analysis",
            "Risk & Correlation",
            "Approvals"
        ])
        
        with tabs[0]:
            self._render_portfolio_overview()
        
        with tabs[1]:
            self._render_strategy_cards()
        
        with tabs[2]:
            self._render_strategy_comparison()
        
        with tabs[3]:
            self._render_allocations()
        
        with tabs[4]:
            self._render_pnl_analysis()
        
        with tabs[5]:
            self._render_risk_correlation()
        
        with tabs[6]:
            self._render_approvals()
    
    def _render_portfolio_overview(self):
        """Render portfolio overview tab"""
        st.header("Portfolio Overview")
        
        data = self.portfolio_overview.get_data()
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total PnL", f"${data['total_pnl']:,.2f}")
        
        with col2:
            st.metric("Total Exposure", f"${data['total_exposure']:,.2f}")
        
        with col3:
            st.metric("Total Risk", f"{data['total_risk']:.2f}")
        
        with col4:
            st.metric("Strategies", data['num_strategies'])
        
        # Conflict indicator
        if data['has_conflicts']:
            st.warning(f"⚠️ Conflicts Detected (Severity: {data['drift_severity']:.1%})")
        else:
            st.success("✅ No Conflicts")
    
    def _render_strategy_cards(self):
        """Render strategy cards tab"""
        st.header("Strategy Status Cards")
        
        cards = self.strategy_cards.get_data()
        
        if not cards:
            st.info("No strategies registered")
            return
        
        # Display cards in grid
        cols = st.columns(min(3, len(cards)))
        
        for idx, card in enumerate(cards):
            with cols[idx % 3]:
                st.subheader(f"{card['status_emoji']} {card['name']}")
                st.metric("PnL", f"${card['pnl']:,.2f}")
                st.metric("Exposure", f"${card['exposure']:,.2f}")
                st.metric("Risk", f"{card['risk_score']:.2f}")
                st.caption(f"Allocation: {card['allocation']:.1%}")
    
    def _render_strategy_comparison(self):
        """Render strategy comparison tab"""
        st.header("Strategy Comparison")
        
        data = self.strategy_comparison.get_data()
        
        if not data.get('strategies'):
            st.info("Need at least 2 strategies for comparison")
            return
        
        st.metric("Signal Agreement", f"{data['agreement_pct']:.1f}%")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Long", data['num_long'])
        with col2:
            st.metric("Short", data['num_short'])
        with col3:
            st.metric("Flat", data['num_flat'])
    
    def _render_allocations(self):
        """Render allocations tab"""
        st.header("Capital Allocation")
        
        data = self.allocation_panel.get_data()
        
        if not data.get('allocations'):
            st.info("No strategies registered")
            return
        
        st.subheader("Current Allocations")
        for alloc in data['allocations']:
            st.write(f"**{alloc['name']}**: {alloc['allocation']:.1%}")
    
    def _render_pnl_analysis(self):
        """Render PnL analysis tab"""
        st.header("PnL Analysis")
        
        data = self.combined_pnl.get_data()
        summary = self.combined_pnl.get_summary()
        
        st.metric("Total PnL", f"${data['total_pnl']:,.2f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Contributor")
            if summary['top_contributor']['name']:
                st.write(f"**{summary['top_contributor']['name']}**")
                st.write(f"${summary['top_contributor']['pnl']:,.2f}")
        
        with col2:
            st.subheader("Worst Contributor")
            if summary['worst_contributor']['name']:
                st.write(f"**{summary['worst_contributor']['name']}**")
                st.write(f"${summary['worst_contributor']['pnl']:,.2f}")
    
    def _render_risk_correlation(self):
        """Render risk & correlation tab"""
        st.header("Risk & Correlation")
        
        corr_data = self.correlation_map.get_data()
        
        if not corr_data.get('strategies'):
            st.info("Need at least 2 strategies for correlation")
            return
        
        st.subheader("Strategy Correlations")
        st.write(f"Strategies: {', '.join(corr_data['strategies'])}")
    
    def _render_approvals(self):
        """Render approvals tab"""
        st.header("Pending Approvals")
        
        data = self.multi_approvals.get_data()
        
        st.metric("Pending Count", data['pending_count'])
        
        if data['pending_count'] == 0:
            st.success("✅ No pending approvals")
        else:
            by_priority = self.multi_approvals.get_by_priority()
            
            if by_priority['high']:
                st.error(f"🔴 High Priority: {len(by_priority['high'])}")
            
            if by_priority['medium']:
                st.warning(f"🟡 Medium Priority: {len(by_priority['medium'])}")
            
            if by_priority['low']:
                st.info(f"🟢 Low Priority: {len(by_priority['low'])}")


def main():
    """Main entry point"""
    dashboard = DashboardV2()
    dashboard.render()


if __name__ == '__main__':
    main()

