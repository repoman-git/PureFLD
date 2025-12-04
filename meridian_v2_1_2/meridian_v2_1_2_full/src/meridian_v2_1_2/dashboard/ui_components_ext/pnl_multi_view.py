"""
PnL Multi-View for Meridian Dashboard

Advanced PnL visualizations with multiple timeframes and attribution.
"""

try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_pnl_multi_view(api):
    """
    Render advanced PnL visualizations.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("📈 PnL Multi-Timeframe Analysis")
    
    # Get PnL data
    pnl_30d = api.get_pnl_timeseries(days=30)
    pnl_7d = api.get_pnl_timeseries(days=7)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Equity Curve", "📉 Drawdown", "🎯 Attribution"])
    
    with tab1:
        # Equity curve with multiple timeframes
        st.markdown("### Cumulative PnL")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**7-Day View**")
            df_7d = pd.DataFrame({
                'Date': pd.to_datetime(pnl_7d['dates']),
                'PnL': pnl_7d['pnl']
            })
            st.line_chart(df_7d.set_index('Date'))
        
        with col2:
            st.markdown("**30-Day View**")
            df_30d = pd.DataFrame({
                'Date': pd.to_datetime(pnl_30d['dates']),
                'PnL': pnl_30d['pnl']
            })
            st.line_chart(df_30d.set_index('Date'))
    
    with tab2:
        st.markdown("### Drawdown Analysis")
        
        # Calculate drawdown
        pnl = pnl_30d['pnl']
        cummax = pd.Series(pnl).cummax()
        drawdown = pd.Series(pnl) - cummax
        drawdown_pct = (drawdown / cummax * 100).fillna(0)
        
        df_dd = pd.DataFrame({
            'Date': pd.to_datetime(pnl_30d['dates']),
            'Drawdown %': drawdown_pct
        })
        
        st.line_chart(df_dd.set_index('Date'))
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Max Drawdown", f"{drawdown_pct.min():.2f}%")
        with col2:
            st.metric("Current DD", f"{drawdown_pct.iloc[-1]:.2f}%")
        with col3:
            st.metric("Days in DD", "N/A")
    
    with tab3:
        st.markdown("### PnL Attribution by Strategy")
        
        # Sample attribution data
        attribution = {
            'FLD': 45.2,
            'COT': 22.8,
            'TDOM': 18.5,
            'Regime': 13.5
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(attribution.keys()),
                y=list(attribution.values()),
                marker_color=['green' if v > 0 else 'red' for v in attribution.values()]
            )
        ])
        
        fig.update_layout(
            title="Strategy Contribution (%)",
            xaxis_title="Strategy",
            yaxis_title="Contribution %",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


