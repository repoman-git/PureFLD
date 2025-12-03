"""
Regime Context View for Meridian Dashboard

Market regime visualization and historical performance.
"""

try:
    import streamlit as st
    import pandas as pd
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_regime_context(api):
    """
    Render regime context visualization.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("📈 Regime Context")
    
    risk = api.get_risk_state()
    
    # Current regime
    st.markdown("### Current Market Regime")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vol_regime = risk.get('volatility_regime', 'medium').upper()
        st.metric("Volatility", vol_regime)
    
    with col2:
        st.metric("Trend", "UPTREND")
    
    with col3:
        st.metric("Yield Curve", "NORMAL")
    
    st.markdown("---")
    
    # Historical performance by regime
    st.markdown("### Performance by Regime")
    
    regime_perf = {
        'Regime': ['Low Vol', 'Med Vol', 'High Vol', 'Uptrend', 'Downtrend'],
        'Sharpe': [0.85, 0.92, 0.45, 1.20, 0.38],
        'MAR': [0.62, 0.71, 0.31, 0.95, 0.25],
        'Win Rate %': [58, 61, 48, 65, 45]
    }
    
    df = pd.DataFrame(regime_perf)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Factor sensitivity
    st.markdown("### Factor Sensitivity by Regime")
    
    sensitivity = {
        'Factor': ['FLD', 'COT', 'TDOM', 'Cycle'],
        'Low Vol': [0.8, 0.6, 0.7, 0.9],
        'Med Vol': [0.9, 0.7, 0.8, 0.85],
        'High Vol': [0.5, 0.8, 0.6, 0.4]
    }
    
    df_sens = pd.DataFrame(sensitivity)
    st.dataframe(df_sens, use_container_width=True, hide_index=True)

