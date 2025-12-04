"""
Activity Feed for Meridian Dashboard

Real-time event stream.
"""

try:
    import streamlit as st
    from datetime import datetime, timedelta
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


def render_activity_feed(api):
    """
    Render activity feed.
    
    Args:
        api: DashboardAPI instance
    """
    if not AVAILABLE:
        st.error("Required libraries not installed")
        return
    
    st.subheader("📡 Activity Feed")
    
    # Sample activity events
    events = [
        {
            'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
            'type': 'signal',
            'icon': '📊',
            'message': 'Signal generated: BUY GLD (+1)'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=10)).isoformat(),
            'type': 'order',
            'icon': '📝',
            'message': 'Order submitted: BUY 10 GLD @ Market'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=12)).isoformat(),
            'type': 'approval',
            'icon': '✅',
            'message': 'Order approved by operator'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=15)).isoformat(),
            'type': 'fill',
            'icon': '✓',
            'message': 'Fill received: 10 GLD @ $195.50'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=20)).isoformat(),
            'type': 'shadow',
            'icon': '🔄',
            'message': 'Shadow check: No drift detected'
        },
        {
            'timestamp': (datetime.now() - timedelta(minutes=25)).isoformat(),
            'type': 'oversight',
            'icon': '🤖',
            'message': 'Oversight AI: Risk level LOW'
        }
    ]
    
    # Display limit
    limit = st.slider("Show last N events", 5, 50, 10)
    
    st.markdown("---")
    
    # Display events
    for event in events[:limit]:
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"{event['icon']}")
        
        with col2:
            timestamp = datetime.fromisoformat(event['timestamp'])
            time_ago = (datetime.now() - timestamp).total_seconds() / 60
            st.markdown(f"**{event['message']}**")
            st.caption(f"{time_ago:.0f} minutes ago")
        
        st.markdown("---")


