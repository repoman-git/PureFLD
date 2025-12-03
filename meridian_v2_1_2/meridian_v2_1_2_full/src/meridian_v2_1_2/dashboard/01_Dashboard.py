"""
Dashboard UI for Meridian v2.1.2

Streamlit-based operator interface.
"""

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

from meridian_v2_1_2.dashboard.dashboard_config import DashboardConfig
from meridian_v2_1_2.dashboard.data_api import DashboardAPI


def main():
    """Main dashboard application"""
    
    if not STREAMLIT_AVAILABLE:
        print("Streamlit not installed. Install with: pip install streamlit")
        return
    
    # Page config
    st.set_page_config(
        page_title="Meridian v2.1.2 - Operator Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize
    config = DashboardConfig()
    api = DashboardAPI(config)
    
    # Title
    st.title("🎯 Meridian v2.1.2 - Operator Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select View",
        [
            "🏠 Home",
            "💼 Portfolio",
            "📊 Signals",
            "📝 Orders",
            "✅ Fills",
            "🔄 Shadow/Drift",
            "⚠️ Risk",
            "🤖 Oversight AI",
            "✋ Approvals",
            "📜 Logs"
        ]
    )
    
    # Render selected page
    if page == "🏠 Home":
        render_home(api)
    elif page == "💼 Portfolio":
        render_portfolio(api)
    elif page == "📊 Signals":
        render_signals(api)
    elif page == "📝 Orders":
        render_orders(api)
    elif page == "✅ Fills":
        render_fills(api)
    elif page == "🔄 Shadow/Drift":
        render_shadow(api)
    elif page == "⚠️ Risk":
        render_risk(api)
    elif page == "🤖 Oversight AI":
        render_oversight(api)
    elif page == "✋ Approvals":
        render_approvals(api)
    elif page == "📜 Logs":
        render_logs(api)


def render_home(api):
    """Render home dashboard"""
    st.header("System Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    portfolio = api.get_portfolio_state()
    risk = api.get_risk_state()
    oversight = api.get_oversight_state()
    shadow = api.get_shadow_state()
    
    with col1:
        st.metric("Portfolio Equity", f"${portfolio['equity']:,.0f}", 
                  f"${portfolio['total_pnl']:+,.0f}")
    
    with col2:
        risk_level = oversight['risk_assessment']['level'].upper()
        risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}.get(risk_level, '⚪')
        st.metric("Risk Level", f"{risk_emoji} {risk_level}")
    
    with col3:
        drift_emoji = '✅' if not shadow['drift_detected'] else '⚠️'
        st.metric("Shadow Status", f"{drift_emoji} {shadow['drift_level'].upper()}")
    
    with col4:
        pending = api.get_pending_approvals()
        st.metric("Pending Approvals", len(pending))
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("Recent Activity")
    logs = api.get_run_logs(limit=5)
    
    for log in logs:
        st.text(f"[{log['timestamp']}] {log['status'].upper()} - Signals: {log['signals_generated']}, PnL: ${log['pnl']:,.2f}")


def render_portfolio(api):
    """Render portfolio view"""
    st.header("Portfolio")
    
    portfolio = api.get_portfolio_state()
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cash", f"${portfolio['cash']:,.0f}")
    with col2:
        st.metric("Equity", f"${portfolio['equity']:,.0f}")
    with col3:
        st.metric("Total PnL", f"${portfolio['total_pnl']:+,.0f}")
    
    # Positions table
    st.subheader("Positions")
    if portfolio['positions']:
        import pandas as pd
        df = pd.DataFrame(portfolio['positions'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No positions")
    
    # PnL chart
    st.subheader("PnL History")
    pnl_data = api.get_pnl_timeseries(days=30)
    
    import pandas as pd
    chart_df = pd.DataFrame({
        'Date': pd.to_datetime(pnl_data['dates']),
        'PnL': pnl_data['pnl']
    })
    st.line_chart(chart_df.set_index('Date'))


def render_signals(api):
    """Render signals view"""
    st.header("Strategy Signals")
    
    signals = api.get_signals()
    
    st.subheader("Current Signals")
    
    import pandas as pd
    signal_data = signals['signals']
    
    # Convert to DataFrame
    df = pd.DataFrame(signal_data).T
    st.dataframe(df, use_container_width=True)


def render_orders(api):
    """Render orders view"""
    st.header("Orders")
    
    orders = api.get_orders()
    
    if orders:
        import pandas as pd
        df = pd.DataFrame(orders)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders")


def render_fills(api):
    """Render fills view"""
    st.header("Fill History")
    
    fills = api.get_fills()
    
    if fills:
        import pandas as pd
        df = pd.DataFrame(fills)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No fills")


def render_shadow(api):
    """Render shadow/drift view"""
    st.header("Broker Shadow Status")
    
    shadow = api.get_shadow_state()
    
    # Status
    if shadow['drift_detected']:
        st.warning(f"⚠️ Drift Detected: {shadow['drift_level'].upper()}")
    else:
        st.success("✅ No Drift - Positions Synced")
    
    st.text(f"Last Check: {shadow['last_check']}")


def render_risk(api):
    """Render risk view"""
    st.header("Risk Monitor")
    
    risk = api.get_risk_state()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Model Risk Score", f"{risk['model_risk_score']:.2f}")
    
    with col2:
        st.metric("Gross Exposure", f"${risk['exposure']['gross']:,.0f}",
                 f"/{risk['exposure']['max_allowed']:,.0f}")
    
    with col3:
        st.metric("Volatility Regime", risk['volatility_regime'].upper())
    
    # Kill switch
    if risk['kill_switch_active']:
        st.error("🛑 KILL SWITCH ACTIVE")
    else:
        st.success("✅ Kill Switch: Inactive")


def render_oversight(api):
    """Render oversight AI view"""
    st.header("🤖 Oversight AI")
    
    oversight = api.get_oversight_state()
    
    # Anomaly scores
    st.subheader("Anomaly Scores")
    scores = oversight['anomaly_scores']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Strategy", f"{scores['strategy']:.2f}")
    with col2:
        st.metric("Execution", f"{scores['execution']:.2f}")
    with col3:
        st.metric("Shadow", f"{scores['shadow']:.2f}")
    with col4:
        st.metric("Portfolio", f"{scores['portfolio']:.2f}")
    with col5:
        st.metric("Overall", f"{scores['overall']:.2f}", 
                 delta=None, delta_color="inverse")
    
    # Risk assessment
    st.subheader("Risk Assessment")
    assessment = oversight['risk_assessment']
    
    risk_level = assessment['level'].upper()
    risk_emoji = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}.get(risk_level, '⚪')
    
    st.markdown(f"### {risk_emoji} Risk Level: **{risk_level}**")
    st.metric("Risk Score", f"{assessment['score']:.2f}")
    
    if assessment['should_halt']:
        st.error("⚠️ RECOMMENDATION: HALT TRADING")
    
    # Advisories
    st.subheader("AI Advisories")
    advisories = oversight['advisories']
    
    if advisories:
        for adv in advisories:
            priority_emoji = {'urgent': '🚨', 'warning': '⚠️', 'info': 'ℹ️'}.get(adv.get('priority', 'info'), '•')
            st.markdown(f"{priority_emoji} **{adv.get('category', 'General').upper()}**: {adv.get('message', 'No message')}")
    else:
        st.info("No active advisories")


def render_approvals(api):
    """Render approvals view"""
    st.header("✋ Pending Approvals")
    
    pending = api.get_pending_approvals()
    
    if pending:
        for req in pending:
            with st.expander(f"Request {req['id']}"):
                st.text(f"Type: {req['type']}")
                st.text(f"Details: {req['details']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Approve {req['id']}", key=f"approve_{req['id']}"):
                        api.approve_request(req['id'])
                        st.success("Approved!")
                        st.rerun()
                
                with col2:
                    if st.button(f"❌ Reject {req['id']}", key=f"reject_{req['id']}"):
                        api.reject_request(req['id'])
                        st.warning("Rejected")
                        st.rerun()
    else:
        st.info("No pending approvals")


def render_logs(api):
    """Render logs view"""
    st.header("📜 Run Logs")
    
    logs = api.get_run_logs(limit=50)
    
    if logs:
        import pandas as pd
        df = pd.DataFrame(logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No logs")


if __name__ == "__main__":
    main()

