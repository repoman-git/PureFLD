"""
Notifications Panel for Meridian Dashboard

In-dashboard notifications and alerts.
"""

try:
    import streamlit as st
    from datetime import datetime, timedelta
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_notifications(api):
    """
    Render notifications panel.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("📨 Notifications")
    
    # Sample notifications
    notifications = [
        {
            'id': '1',
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'severity': 'critical',
            'category': 'drift',
            'message': 'Critical drift detected in GLD position',
            'dismissed': False
        },
        {
            'id': '2',
            'timestamp': (datetime.now() - timedelta(hours=1)).isoformat(),
            'severity': 'warning',
            'category': 'risk',
            'message': 'Model risk score elevated to 0.65',
            'dismissed': False
        },
        {
            'id': '3',
            'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
            'severity': 'info',
            'category': 'approval',
            'message': 'Order approved and executed successfully',
            'dismissed': False
        }
    ]
    
    # Filter controls
    col1, col2 = st.columns([3, 1])
    
    with col1:
        show_dismissed = st.checkbox("Show Dismissed", value=False)
    
    with col2:
        severity_filter = st.selectbox(
            "Filter",
            ["All", "Critical", "Warning", "Info"],
            index=0
        )
    
    # Filter notifications
    filtered = notifications
    
    if not show_dismissed:
        filtered = [n for n in filtered if not n['dismissed']]
    
    if severity_filter != "All":
        filtered = [n for n in filtered if n['severity'] == severity_filter.lower()]
    
    st.markdown("---")
    
    # Display notifications
    if not filtered:
        st.info("No notifications")
    else:
        for notif in filtered:
            severity_emoji = {
                'critical': '🔴',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(notif['severity'], '•')
            
            with st.expander(f"{severity_emoji} {notif['message']}", expanded=False):
                st.text(f"Category: {notif['category']}")
                st.text(f"Time: {notif['timestamp']}")
                
                if not notif['dismissed']:
                    if st.button(f"Dismiss", key=f"dismiss_{notif['id']}"):
                        st.success("Notification dismissed")


