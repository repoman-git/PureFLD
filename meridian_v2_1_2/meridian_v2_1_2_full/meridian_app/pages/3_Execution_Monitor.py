"""Execution Monitoring Page"""
import streamlit as st

st.title("🚀 Execution Monitor")
st.markdown("**Live/Paper trading activity monitor**")

st.info("""
### Execution Engine Status

Connect to Alpaca or IBKR to view:
- Open positions
- Recent orders
- Account balance
- P&L tracking

**Note:** Requires broker API keys configured in execution engine.
""")

st.warning("⚠️ For paper trading setup, see: `STAGE_7_COMPLETE.md`")

# Placeholder for execution monitoring
st.subheader("Recent Activity")
st.info("No active trading session. Start execution engine to see live data.")

