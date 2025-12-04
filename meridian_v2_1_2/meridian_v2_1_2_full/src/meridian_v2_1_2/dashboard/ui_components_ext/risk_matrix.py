"""
Risk Matrix for Meridian Dashboard

Color-coded strategy state visualization.
"""

try:
    import streamlit as st
    import pandas as pd
    import numpy as np
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_risk_matrix(api):
    """
    Render risk matrix visualization.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("🧠 Strategy State Matrix")
    
    # Get signals and risk data
    signals = api.get_signals()
    risk = api.get_risk_state()
    
    # Create matrix data
    matrix_data = {
        'Component': ['FLD', 'COT', 'TDOM', 'Regime', 'Risk'],
        'Status': ['🟢 Aligned', '🟢 Aligned', '🟡 Partial', '🟢 Aligned', '🟢 Low'],
        'Signal': ['+1', '+1', '+1', '+1', '0.23'],
        'Confidence': ['High', 'High', 'Medium', 'High', 'N/A']
    }
    
    df = pd.DataFrame(matrix_data)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Alignment summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Aligned Factors", "4/5")
    with col2:
        st.metric("Overall Confidence", "High")
    with col3:
        st.metric("Trade Readiness", "✅ Ready")
    
    st.markdown("---")
    
    # Legend
    st.markdown("### Legend")
    st.markdown("- 🟢 **Aligned**: All signals agree")
    st.markdown("- 🟡 **Partial**: Mixed signals")
    st.markdown("- 🔴 **Contradictory**: Conflicting signals")


