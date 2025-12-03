"""
Trading Decision Audit Dashboard

Professional trading desk compliance system.
Pre-trade validation, risk checks, multi-AI review before execution.
"""

import streamlit as st
import pandas as pd

from meridian_v2_1_2.trading_audit_engine import (
    TradingAuditOrchestrator,
    TradingAuditResult
)
from meridian_v2_1_2.trading_audit_engine.audit_pretrade import CheckStatus

st.set_page_config(
    page_title="Meridian - Trading Audit",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Trading Decision Audit")
st.markdown("*Professional pre-trade validation and risk gating*")
st.markdown("---")

# Info panel
with st.expander("ℹ️ What is Trading Audit?", expanded=False):
    st.markdown("""
    ### Professional Trading Desk Compliance
    
    Before executing ANY trade, this system checks:
    
    **Pre-Trade Validation:**
    - Signal validity & strength
    - Strategy rule alignment
    - Position sizing appropriateness
    - Risk parameters (stop loss, R:R ratio)
    
    **Risk Limit Enforcement:**
    - Hard limits (auto-block if violated)
    - Soft limits (warnings)
    - Portfolio risk budget
    
    **Portfolio Impact:**
    - Concentration risk
    - Correlation exposure
    - Total portfolio risk
    - Exposure drift
    
    **Multi-AI Review:**
    - 4 AI models review each trade
    - Consensus voting
    - Confidence scoring
    
    **Final Verdict:**
    - ✅ APPROVED - Execute trade
    - ⚠️  WARNING - Proceed with caution
    - 🚫 BLOCKED - Do not execute
    
    **Like having a compliance officer for every trade!**
    """)

# Initialize session state
if 'audit_result' not in st.session_state:
    st.session_state.audit_result = None

# ═══════════════════════════════════════════════════════════════════
# TRADE INPUT
# ═══════════════════════════════════════════════════════════════════

st.subheader("📝 Trade Intent")

col1, col2, col3 = st.columns(3)

with col1:
    symbol = st.text_input("Symbol", value="GLD", help="Asset symbol (e.g., GLD, SPY, TLT)")
    direction = st.selectbox("Direction", ["long", "short"])
    strategy_name = st.selectbox(
        "Strategy",
        ["FLD-ETF", "Momentum-ETF", "Cycle-ETF", "Defensive-ETF", "Custom"]
    )

with col2:
    entry_price = st.number_input("Entry Price", min_value=0.01, value=180.0, step=0.1)
    stop_loss = st.number_input("Stop Loss", min_value=0.01, value=175.0, step=0.1)
    take_profit = st.number_input("Take Profit (optional)", min_value=0.01, value=190.0, step=0.1)

with col3:
    size_pct = st.slider("Position Size (%)", min_value=1, max_value=20, value=5, step=1)
    signal_strength = st.slider("Signal Strength", min_value=0.0, max_value=1.0, value=0.75, step=0.05)
    current_volatility = st.slider("Current Volatility", min_value=0.0, max_value=1.0, value=0.15, step=0.05)

# Build trade intent
trade_intent = {
    'symbol': symbol,
    'direction': direction,
    'size': size_pct / 100,
    'entry_price': entry_price,
    'stop_loss': stop_loss,
    'take_profit': take_profit if take_profit > entry_price else None,
    'signal_strength': signal_strength,
    'strategy_name': strategy_name,
    'current_volatility': current_volatility,
    'reward_risk_ratio': (take_profit - entry_price) / (entry_price - stop_loss) if (entry_price - stop_loss) > 0 else 0
}

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# AUDIT CONTROLS
# ═══════════════════════════════════════════════════════════════════

st.subheader("⚙️ Audit Configuration")

col1, col2 = st.columns(2)

with col1:
    run_ai_review = st.checkbox("Run Multi-AI Review", value=True, help="Get 4 AI models to review trade")

with col2:
    strict_mode = st.checkbox("Strict Mode", value=False, help="Block on warnings, not just critical violations")

st.markdown("---")

# Run audit button
if st.button("🛡️ RUN TRADING AUDIT", type="primary", use_container_width=True):
    with st.spinner("Auditing trade decision..."):
        try:
            # Create orchestrator
            orchestrator = TradingAuditOrchestrator()
            
            # Mock portfolio (can integrate with real portfolio later)
            mock_portfolio = {
                'positions': {symbol: 0.03},
                'total_value': 100000,
                'total_risk': 0.02,
                'exposures': {}
            }
            
            # Strategy rules
            strategy_rules = {
                'allow_short': direction == 'short',
                'max_position': 0.10
            }
            
            # Run audit
            result = orchestrator.audit_trade(
                trade_intent,
                strategy_rules,
                mock_portfolio,
                run_ai_review
            )
            
            st.session_state.audit_result = result
            
        except Exception as e:
            st.error(f"Audit failed: {e}")

# ═══════════════════════════════════════════════════════════════════
# DISPLAY RESULTS
# ═══════════════════════════════════════════════════════════════════

if st.session_state.audit_result:
    result = st.session_state.audit_result
    
    st.markdown("---")
    
    # Final Verdict
    if result.final_status == 'APPROVED':
        st.success(f"### ✅ TRADE APPROVED")
        st.markdown(f"**{result.summary}**")
    elif result.final_status == 'BLOCKED':
        st.error(f"### 🚫 TRADE BLOCKED")
        st.markdown(f"**{result.summary}**")
    else:  # WARNING
        st.warning(f"### ⚠️  PROCEED WITH CAUTION")
        st.markdown(f"**{result.summary}**")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pre-Trade", "✅ PASS" if result.pretrade_passed else "❌ FAIL")
    with col2:
        st.metric("Risk Limits", "✅ PASS" if result.risk_passed else "❌ FAIL")
    with col3:
        st.metric("AI Consensus", result.ai_consensus)
    with col4:
        st.metric("AI Confidence", f"{result.ai_confidence:.0f}%")
    
    st.markdown("---")
    
    # Detailed results in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Pre-Trade Checks", "Risk Violations", "Portfolio Impact", "AI Review"])
    
    with tab1:
        st.markdown("### Pre-Trade Validation")
        
        for check in result.pretrade_checks:
            if check.status == CheckStatus.PASS:
                st.success(f"✅ **{check.check_name}**: {check.message}")
            elif check.status == CheckStatus.WARNING:
                st.warning(f"⚠️  **{check.check_name}**: {check.message}")
            else:
                st.error(f"❌ **{check.check_name}**: {check.message}")
    
    with tab2:
        st.markdown("### Risk Limit Violations")
        
        if not result.risk_violations:
            st.success("✅ No risk limit violations")
        else:
            for violation in result.risk_violations:
                if violation.severity.value == 'CRITICAL':
                    st.error(f"🚫 **{violation.rule_name}**: {violation.message}")
                elif violation.severity.value == 'HIGH':
                    st.warning(f"⚠️  **{violation.rule_name}**: {violation.message}")
                else:
                    st.info(f"ℹ️  **{violation.rule_name}**: {violation.message}")
    
    with tab3:
        st.markdown("### Portfolio Impact Analysis")
        
        if not result.portfolio_impacts:
            st.info("No portfolio provided for impact analysis")
        else:
            for impact in result.portfolio_impacts:
                st.markdown(f"**{impact.metric_name}**")
                st.markdown(f"- Current: {impact.current_value:.2%}")
                st.markdown(f"- Projected: {impact.projected_value:.2%}")
                st.markdown(f"- Change: {impact.change:.2%}")
                st.markdown(f"- {impact.message}")
                st.markdown("")
    
    with tab4:
        st.markdown("### Multi-AI Trade Review")
        
        if not result.ai_reviews:
            st.info("AI review not requested")
        else:
            st.markdown(f"**Consensus:** {result.ai_consensus}")
            st.markdown(f"**Confidence:** {result.ai_confidence:.1f}%")
            
            verdicts = result.ai_reviews.get('verdicts', [])
            
            if verdicts:
                st.markdown("#### Individual AI Verdicts:")
                
                for verdict in verdicts:
                    with st.expander(f"🤖 {verdict.model_name.upper()} - {verdict.verdict.value}"):
                        st.markdown(f"**Confidence:** {verdict.confidence:.1%}")
                        st.markdown(f"**Reasoning:** {verdict.reasoning}")
                        
                        if verdict.advantages:
                            st.success("**Advantages:**")
                            for adv in verdict.advantages:
                                st.markdown(f"- {adv}")
                        
                        if verdict.concerns:
                            st.warning("**Concerns:**")
                            for concern in verdict.concerns:
                                st.markdown(f"- {concern}")
    
    # Export
    st.markdown("---")
    st.subheader("📤 Export Audit")
    
    if st.button("📋 Copy JSON to Clipboard"):
        st.code(result.to_json())
    
    if st.button("💾 Download Audit Report"):
        st.download_button(
            label="Download JSON",
            data=result.to_json(),
            file_name=f"trade_audit_{result.audit_id}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.caption("Phase X-Trading | Professional Trading Desk Compliance System")
st.caption("🛡️ Pre-trade validation | Risk gating | Multi-AI consensus")
st.caption("⚠️  This is for risk management only - not financial advice")

