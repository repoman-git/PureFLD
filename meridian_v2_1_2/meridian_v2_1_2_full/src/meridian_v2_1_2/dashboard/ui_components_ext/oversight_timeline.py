"""
Oversight Timeline for Meridian Dashboard

Timeline of anomalies, alerts, and AI advisories.
"""

try:
    import streamlit as st
    import pandas as pd
    from datetime import datetime, timedelta
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_oversight_timeline(api):
    """
    Render oversight event timeline.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("⏱️ Oversight Event Timeline")
    
    # Sample timeline data
    events = [
        {
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'type': 'Anomaly',
            'severity': 'warning',
            'message': 'High execution slippage detected'
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=5)).isoformat(),
            'type': 'Advisory',
            'severity': 'info',
            'message': 'Behavioral deviation: signal count +2.1 std devs'
        },
        {
            'timestamp': (datetime.now() - timedelta(hours=8)).isoformat(),
            'type': 'Repair',
            'severity': 'info',
            'message': 'Shadow drift auto-repaired'
        }
    ]
    
    df = pd.DataFrame(events)
    
    # Display as table
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Events (24h)", len(events))
    with col2:
        st.metric("Warnings", sum(1 for e in events if e['severity'] == 'warning'))
    with col3:
        st.metric("Critical", sum(1 for e in events if e['severity'] == 'critical'))


