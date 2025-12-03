"""
Trade Drill-Down View for Meridian Dashboard

Deep dive into individual trade execution and context.
"""

try:
    import streamlit as st
    import pandas as pd
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_trade_drilldown(api, trade_id: str = None):
    """
    Render trade drill-down view.
    
    Args:
        api: DashboardAPI instance
        trade_id: Optional trade ID to drill into
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("🔍 Trade Investigation")
    
    # Get fills
    fills = api.get_fills()
    
    if not fills:
        st.info("No trades to investigate")
        return
    
    # Trade selector
    fill_ids = [f['id'] for f in fills]
    selected_fill = st.selectbox("Select Trade", fill_ids)
    
    if selected_fill:
        # Find the selected fill
        fill_data = next((f for f in fills if f['id'] == selected_fill), None)
        
        if fill_data:
            st.markdown("---")
            
            # Trade summary
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Symbol", fill_data['symbol'])
            with col2:
                st.metric("Side", fill_data['side'].upper())
            with col3:
                st.metric("Quantity", fill_data['qty'])
            with col4:
                st.metric("Fill Price", f"${fill_data['price']:.2f}")
            
            # Detailed sections
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Execution",
                "🎯 Signals",
                "⚡ Slippage",
                "📜 Timeline"
            ])
            
            with tab1:
                st.markdown("### Execution Details")
                st.text(f"Order ID: {fill_data.get('order_id', 'N/A')}")
                st.text(f"Timestamp: {fill_data.get('timestamp', 'N/A')}")
                st.text(f"Slippage: {fill_data.get('slippage_bps', 0):.1f} bps")
            
            with tab2:
                st.markdown("### Signal Context (Pre-Trade)")
                signals = api.get_signals()
                
                if 'signals' in signals:
                    st.json(signals['signals'])
                else:
                    st.info("No signal data available")
            
            with tab3:
                st.markdown("### Slippage Analysis")
                slippage_bps = fill_data.get('slippage_bps', 0)
                
                if slippage_bps > 5:
                    st.warning(f"High slippage: {slippage_bps:.1f} bps")
                else:
                    st.success(f"Normal slippage: {slippage_bps:.1f} bps")
            
            with tab4:
                st.markdown("### Execution Timeline")
                st.text("1. Signal Generated")
                st.text("2. Order Submitted")
                st.text("3. Order Filled")
                st.text("4. Position Updated")

