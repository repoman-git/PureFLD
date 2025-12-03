"""
Paper Trading Dashboard

Real-time simulated trading with strategy selection.
Complete E2E pipeline: Strategy → Audit → Execution → PnL

⚠️  PAPER TRADING ONLY - NO REAL MONEY
"""

import streamlit as st
import pandas as pd

from meridian_v2_1_2.paper_trading import PaperTradingOrchestrator
from meridian_v2_1_2.strategies import strategy_router

st.set_page_config(
    page_title="Meridian - Paper Trading",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Paper Trading Simulator")
st.markdown("*Real data, simulated execution - Zero risk*")
st.markdown("---")

# Educational disclaimer
st.warning("""
⚠️  **PAPER TRADING SIMULATION - EDUCATIONAL ONLY**

This is a simulation using real market data but simulated execution.
NO REAL MONEY is involved. This is NOT investment advice.
Past performance does not indicate future results.
""")

# Info panel
with st.expander("ℹ️ How Paper Trading Works", expanded=False):
    st.markdown("""
    ### Complete E2E Trading Pipeline
    
    **1. Strategy Selection:**
    - Choose from 4 professional ETF strategies
    - Each with proven track record on specific assets
    
    **2. Live Data:**
    - Real-time price feeds (Yahoo Finance)
    - OHLCV data for signal generation
    
    **3. Signal Generation:**
    - Strategy analyzes current market conditions
    - Generates LONG/SHORT/FLAT signals
    - Provides signal strength metric
    
    **4. Trading Audit:**
    - Pre-trade validation (6 checks)
    - Risk limit enforcement
    - Multi-AI review (optional)
    - Final verdict: APPROVED/WARNING/BLOCKED
    
    **5. Simulated Execution:**
    - Realistic fill simulation
    - Slippage modeling
    - Portfolio updates
    
    **6. PnL Tracking:**
    - Realized/Unrealized PnL
    - Risk metrics (Sharpe, drawdown)
    - Trade history
    
    **Like having a professional trading desk - but 100% simulated!**
    """)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = PaperTradingOrchestrator(
        initial_capital=100000.0,
        slippage_bps=5.0
    )

if 'pipeline_result' not in st.session_state:
    st.session_state.pipeline_result = None

orchestrator = st.session_state.orchestrator

# ═══════════════════════════════════════════════════════════════════
# STRATEGY SELECTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("🎯 Strategy Selection")

col1, col2 = st.columns([1, 2])

with col1:
    strategy_name = st.selectbox(
        "Select Trading Strategy",
        strategy_router.list_strategies(),
        help="Choose strategy for analysis"
    )

with col2:
    if strategy_name:
        metadata = strategy_router.get_strategy_metadata(strategy_name)
        
        st.markdown(f"**{metadata['description']}**")
        st.markdown(f"*Best for: {', '.join(metadata['best_for'])}*")

# Show strategy rules
if strategy_name:
    with st.expander(f"📋 {strategy_name} Rules", expanded=False):
        metadata = strategy_router.get_strategy_metadata(strategy_name)
        
        st.markdown("**Trading Rules:**")
        for rule in metadata['rules']:
            st.markdown(f"- {rule}")
        
        st.markdown("**Default Parameters:**")
        for param, value in metadata['default_params'].items():
            st.markdown(f"- {param}: `{value}`")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# INSTRUMENT SELECTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("📈 Instrument Analysis")

col1, col2, col3 = st.columns(3)

with col1:
    symbol = st.text_input("Symbol", value="GLD", help="Asset symbol (e.g., GLD, SPY, TLT)")

with col2:
    data_period = st.selectbox(
        "Historical Data",
        options=['2y', '5y', '10y', '20y', 'max'],
        index=3,  # Default to 20y
        help="Amount of historical data to fetch"
    )

with col3:
    advanced_mode = st.checkbox("Advanced Mode", value=False, help="Show advanced diagnostics")

# Run E2E analysis button
if st.button("🚀 RUN END-TO-END ANALYSIS", type="primary", use_container_width=True):
    with st.spinner(f"Analyzing {symbol} with {strategy_name}..."):
        try:
            result = orchestrator.run_instrument_pipeline(
                symbol,
                strategy_name,
                advanced_mode
            )
            
            st.session_state.pipeline_result = result
            
        except Exception as e:
            st.error(f"Analysis failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════════

if st.session_state.pipeline_result:
    result = st.session_state.pipeline_result
    
    st.markdown("---")
    
    if result['status'] == 'error':
        st.error(f"❌ **Error:** {result.get('error', 'Unknown error')}")
    else:
        # Success banner
        st.success(f"✅ **Analysis Complete: {result['symbol']} using {result['strategy']}**")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if result['data']:
                st.metric("Current Price", f"${result['data']['current_price']:.2f}")
        
        with col2:
            if result['signal']:
                signal_type = "LONG" if result['signal']['long_signal'] else ("SHORT" if result['signal']['short_signal'] else "FLAT")
                st.metric("Signal", signal_type)
        
        with col3:
            if result['signal']:
                st.metric("Signal Strength", f"{result['signal']['signal_strength']:.2%}")
        
        with col4:
            if result['audit']:
                st.metric("Audit Status", result['audit']['final_status'])
        
        st.markdown("---")
        
        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Signal Details", "🛡️ Trading Audit", "💬 Commentary", "📈 Chart"])
        
        with tab1:
            st.markdown("### Signal Analysis")
            
            if result['signal']:
                sig = result['signal']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Signal Type:**")
                    if sig['long_signal']:
                        st.success("🟢 **LONG** - Buy signal active")
                    elif sig['short_signal']:
                        st.error("🔴 **SHORT** - Sell signal active")
                    else:
                        st.info("⚪ **FLAT** - No position")
                
                with col2:
                    st.markdown("**Signal Strength:**")
                    strength = sig['signal_strength']
                    
                    if abs(strength) > 0.03:
                        st.success(f"Strong: {strength:.2%}")
                    elif abs(strength) > 0.01:
                        st.warning(f"Moderate: {strength:.2%}")
                    else:
                        st.info(f"Weak: {strength:.2%}")
        
        with tab2:
            st.markdown("### Trading Audit Results")
            
            if result['audit']:
                audit = result['audit']
                
                if audit['final_status'] == 'APPROVED':
                    st.success(f"✅ **APPROVED**")
                elif audit['final_status'] == 'BLOCKED':
                    st.error(f"🚫 **BLOCKED**")
                elif audit['final_status'] == 'WARNING':
                    st.warning(f"⚠️  **WARNING**")
                
                st.markdown(f"**Summary:** {audit['summary']}")
                st.markdown(f"**Should Execute:** {'Yes' if audit['should_execute'] else 'No'}")
            else:
                st.info("No audit performed (no actionable signal)")
        
        with tab3:
            st.markdown("### AI Commentary")
            
            if result['commentary']:
                comm = result['commentary']
                
                st.markdown(f"**Summary:** {comm['summary']}")
                st.markdown(f"**Signal:** {comm['signal_interpretation']}")
                
                if comm['risk_notes']:
                    st.markdown("**Risk Notes:**")
                    for note in comm['risk_notes']:
                        st.markdown(f"- {note}")
                
                st.markdown(f"**Market Context:** {comm['market_context']}")
        
        with tab4:
            st.markdown("### Price Chart")
            
            if result['data'] and result['data'].get('ohlc'):
                try:
                    # Convert dict back to DataFrame
                    ohlc_dict = result['data']['ohlc']
                    df = pd.DataFrame(ohlc_dict)
                    
                    if not df.empty and 'Close' in df.columns:
                        st.line_chart(df['Close'])
                    else:
                        st.info("Chart data not available")
                except:
                    st.info("Chart data not available")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# RUN BACKTEST
# ═══════════════════════════════════════════════════════════════════

st.subheader("🔬 Backtest This Strategy")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown(f"""
    **Backtest {strategy_name} on {symbol}**
    
    Run historical simulation to see how this strategy
    would have performed on past data.
    """)

with col2:
    if st.button("🔬 RUN BACKTEST", use_container_width=True):
        st.info("Backtest functionality coming soon! Will integrate with Phase 4 backtesting engine.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# PORTFOLIO PANEL
# ═══════════════════════════════════════════════════════════════════

st.subheader("💼 Paper Portfolio")

col1, col2, col3 = st.columns(3)

portfolio = orchestrator.portfolio

with col1:
    st.metric("Total Value", f"${portfolio.get_total_value():,.2f}")
    st.metric("Cash", f"${portfolio.cash:,.2f}")

with col2:
    positions_value = portfolio.get_total_value() - portfolio.cash
    st.metric("Positions Value", f"${positions_value:,.2f}")
    st.metric("# Positions", len(portfolio.positions))

with col3:
    total_return = ((portfolio.get_total_value() / orchestrator.initial_capital) - 1) * 100
    st.metric("Total Return", f"{total_return:.2f}%")

# Positions table
if portfolio.positions:
    st.markdown("### Current Positions")
    
    positions_data = []
    for symbol, pos in portfolio.positions.items():
        positions_data.append({
            'Symbol': symbol,
            'Quantity': pos.quantity,
            'Entry': f"${pos.entry_price:.2f}",
            'Current': f"${pos.current_price:.2f}",
            'Unrealized PnL': f"${pos.unrealized_pnl:.2f}",
            'PnL %': f"{pos.unrealized_pnl_pct * 100:.2f}%"
        })
    
    st.dataframe(pd.DataFrame(positions_data), use_container_width=True)
else:
    st.info("No positions - Portfolio is 100% cash")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# TRADE HISTORY
# ═══════════════════════════════════════════════════════════════════

st.subheader("📜 Trade History")

trades = orchestrator.history.get_trades(limit=10)

if trades:
    trades_data = []
    for trade in trades:
        trades_data.append({
            'Time': trade.timestamp[:19],
            'Symbol': trade.symbol,
            'Side': trade.side,
            'Qty': trade.quantity,
            'Price': f"${trade.fill_price:.2f}",
            'Audit': trade.audit_status,
            'Strategy': trade.strategy
        })
    
    st.dataframe(pd.DataFrame(trades_data), use_container_width=True)
    
    # Trade stats
    stats = orchestrator.history.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trades", stats['total_trades'])
    with col2:
        st.metric("Buys", stats['total_buys'])
    with col3:
        st.metric("Sells", stats['total_sells'])
    with col4:
        st.metric("Approved %", f"{stats['approved_pct']:.1f}%")

else:
    st.info("No trades yet - Run an analysis and execute trades to begin")

# Footer
st.markdown("---")
st.caption("Phase XI-S | Paper Trading with Strategy Integration")
st.caption("📊 Live data | 🛡️ Pre-trade audit | 💼 Portfolio tracking")
st.caption("⚠️  EDUCATIONAL SIMULATION ONLY - Not investment advice")

