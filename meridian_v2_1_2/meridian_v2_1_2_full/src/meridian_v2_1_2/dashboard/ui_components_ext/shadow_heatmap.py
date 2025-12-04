"""
Shadow Heatmap for Meridian Dashboard

Visualizes drift intensity across dimensions.
"""

try:
    import streamlit as st
    import pandas as pd
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_shadow_heatmap(api):
    """
    Render shadow drift heatmap.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("🔥 Shadow Drift Heatmap")
    
    shadow = api.get_shadow_state()
    
    # Drift metrics
    drift_data = {
        'Dimension': ['Quantity', 'Cost Basis', 'PnL', 'Fills', 'Orders'],
        'Drift Level': ['None', 'None', 'None', 'None', 'None'],
        'Severity': [0, 0, 0, 0, 0]
    }
    
    df = pd.DataFrame(drift_data)
    
    # Color code based on severity
    def color_severity(val):
        if val == 0:
            return 'background-color: green'
        elif val < 0.3:
            return 'background-color: yellow'
        else:
            return 'background-color: red'
    
    styled_df = df.style.applymap(color_severity, subset=['Severity'])
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Overall status
    if shadow['drift_detected']:
        st.warning(f"⚠️ Drift Detected: {shadow['drift_level'].upper()}")
    else:
        st.success("✅ All Dimensions Synced")


