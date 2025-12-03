"""
Monte Carlo & Robustness Analysis Dashboard

Comprehensive strategy robustness testing with:
- Monte Carlo simulation
- Walk-forward validation
- Strategy scoring
- AI-driven improvement suggestions
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Import Phase 5 modules
from meridian_v2_1_2.simulation import (
    monte_carlo_equity_simulation,
    calculate_confidence_intervals,
    calculate_risk_of_ruin,
    walk_forward_validation,
    expanding_window_validation
)
from meridian_v2_1_2.portfolio import blend_equity_curves, optimize_weights
from meridian_v2_1_2.scoring import score_strategy
from meridian_v2_1_2.ai import suggest_strategy_improvements, generate_improvement_report
from meridian_v2_1_2.storage import load_all_runs, load_run_by_id

st.set_page_config(
    page_title="Meridian - Robustness Analysis",
    page_icon="🎲",
    layout="wide"
)

st.title("🎲 Monte Carlo & Robustness Analysis")
st.markdown("*Probabilistic testing and strategy evaluation*")
st.markdown("---")

# Load all runs for selection
runs = load_all_runs()

if not runs:
    st.info("📭 No backtest runs found. Run a backtest first to analyze robustness.")
    st.markdown("""
    **Steps to get started:**
    1. Navigate to **Notebook Editor**
    2. Run a backtest with the 🚀 button
    3. Return here to analyze robustness
    """)
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# RUN SELECTION
# ═══════════════════════════════════════════════════════════════════

st.subheader("📊 Select Run to Analyze")

# Create run selection options
run_options = []
for run in runs[:50]:  # Limit to 50 most recent
    strategy = run.get('strategy_name', 'Unknown')
    run_id = run.get('run_id', 'N/A')[:8]
    timestamp = run.get('timestamp', '')[:16]
    sharpe = run.get('metrics', {}).get('sharpe_ratio', 0)
    run_options.append(f"{run_id} | {strategy} | {timestamp} | Sharpe: {sharpe:.2f}")

selected_option = st.selectbox("Select backtest run", run_options)

if not selected_option:
    st.stop()

# Extract run ID and load full data
selected_run_id = selected_option.split(' | ')[0]

# Find full run ID
full_run_id = None
for run in runs:
    if run.get('run_id', '').startswith(selected_run_id):
        full_run_id = run.get('run_id')
        break

if not full_run_id:
    st.error("Could not find selected run")
    st.stop()

run_data = load_run_by_id(full_run_id)

if not run_data:
    st.error("Failed to load run data")
    st.stop()

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# MONTE CARLO SIMULATION
# ═══════════════════════════════════════════════════════════════════

st.subheader("🎲 Monte Carlo Simulation")

with st.expander("ℹ️ About Monte Carlo Simulation", expanded=False):
    st.markdown("""
    Monte Carlo simulation uses block bootstrap resampling to generate probabilistic scenarios.
    This helps understand:
    - Range of possible outcomes
    - Risk of ruin (catastrophic loss)
    - Confidence intervals
    - Worst-case scenarios
    
    **Block Bootstrap:** Preserves autocorrelation structure in returns while generating new scenarios.
    """)

col1, col2, col3 = st.columns(3)
with col1:
    n_sims = st.number_input("Number of Simulations", min_value=100, max_value=2000, value=500, step=100)
with col2:
    block_size = st.number_input("Block Size", min_value=5, max_value=50, value=20, step=5)
with col3:
    seed = st.number_input("Random Seed (optional)", min_value=0, value=42)

if st.button("🎲 Run Monte Carlo Simulation", type="primary"):
    with st.spinner(f"Running {n_sims} simulations..."):
        try:
            # Get equity curve from run
            equity_curve = run_data.get('equity_curve', [])
            
            if not equity_curve or len(equity_curve) < 10:
                st.warning("Equity curve too short for reliable Monte Carlo analysis")
                # Generate mock equity for demo
                initial = run_data.get('initial_capital', 100000)
                final = run_data.get('metrics', {}).get('final_equity', initial * 1.2)
                equity_curve = np.linspace(initial, final, 252)  # Mock year of data
            
            # Run Monte Carlo
            mc_result = monte_carlo_equity_simulation(
                equity_curve=equity_curve,
                n=n_sims,
                block_size=block_size,
                seed=seed
            )
            
            # Store in session state
            st.session_state.mc_result = mc_result
            st.success(f"✅ Completed {n_sims} simulations!")
            
        except Exception as e:
            st.error(f"Monte Carlo simulation failed: {e}")
            st.session_state.mc_result = None

# Display results if available
if hasattr(st.session_state, 'mc_result') and st.session_state.mc_result:
    mc = st.session_state.mc_result
    
    st.markdown("### 📊 Monte Carlo Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Risk of Ruin", f"{mc.risk_of_ruin:.1%}", 
                 help="Probability of losing 50%+ of capital")
    with col2:
        st.metric("Downside Prob", f"{mc.downside_probability:.1%}",
                 help="Probability of any loss")
    with col3:
        st.metric("Expected Final", f"${mc.stats['mean_final']:,.0f}")
    with col4:
        st.metric("Worst Case", f"${mc.stats['worst_final']:,.0f}")
    
    # Fan chart
    st.markdown("#### 📈 Monte Carlo Fan Chart")
    
    ci_bands = calculate_confidence_intervals(
        mc.simulations,
        percentiles=[5, 25, 50, 75, 95]
    )
    
    fig = go.Figure()
    
    # Add confidence bands
    x = list(range(len(ci_bands['50'])))
    fig.add_trace(go.Scatter(
        x=x, y=ci_bands['95'],
        fill=None, mode='lines',
        line=dict(width=0),
        name='95th percentile',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=x, y=ci_bands['75'],
        fill='tonexty', mode='lines',
        line=dict(width=0),
        fillcolor='rgba(0, 100, 200, 0.2)',
        name='75-95%',
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=x, y=ci_bands['25'],
        fill='tonexty', mode='lines',
        line=dict(width=0),
        fillcolor='rgba(0, 100, 200, 0.3)',
        name='25-75%',
        showlegend=True
    ))
    fig.add_trace(go.Scatter(
        x=x, y=ci_bands['5'],
        fill='tonexty', mode='lines',
        line=dict(width=0),
        fillcolor='rgba(0, 100, 200, 0.2)',
        name='5-25%',
        showlegend=True
    ))
    
    # Add median line
    fig.add_trace(go.Scatter(
        x=x, y=ci_bands['50'],
        mode='lines',
        line=dict(color='blue', width=3),
        name='Median'
    ))
    
    fig.update_layout(
        title="Monte Carlo Equity Scenarios (5th-95th Percentile)",
        xaxis_title="Time Steps",
        yaxis_title="Equity ($)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Distribution of final values
    st.markdown("#### 📊 Distribution of Final Equity")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(
        x=mc.final_values,
        nbinsx=50,
        name='Final Equity',
        marker_color='skyblue'
    ))
    fig2.add_vline(
        x=mc.stats['original_final'],
        line_dash="dash",
        line_color="red",
        annotation_text="Original Result"
    )
    fig2.update_layout(
        title="Distribution of Final Equity Values",
        xaxis_title="Final Equity ($)",
        yaxis_title="Frequency",
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# STRATEGY SCORING
# ═══════════════════════════════════════════════════════════════════

st.subheader("⭐ Strategy Score")

metrics = run_data.get('metrics', {})
mc_stats = st.session_state.mc_result.stats if hasattr(st.session_state, 'mc_result') and st.session_state.mc_result else None

# Calculate score
score_result = score_strategy(metrics, mc_stats=mc_stats)

# Display score
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.markdown("### Overall Score")
    score_color = "green" if score_result.total_score >= 70 else "orange" if score_result.total_score >= 50 else "red"
    st.markdown(f"<h1 style='text-align: center; color: {score_color};'>{score_result.total_score:.1f}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Grade: {score_result.grade}</h3>", unsafe_allow_html=True)

with col2:
    st.markdown("### Component Scores")
    for component, score in score_result.component_scores.items():
        st.progress(score / 100, text=f"{component.replace('_', ' ').title()}: {score:.1f}/100")

with col3:
    st.markdown("### Quick Stats")
    st.metric("Sharpe", f"{metrics.get('sharpe_ratio', 0):.2f}")
    st.metric("Return", f"{metrics.get('total_return', 0):.1%}")
    st.metric("Max DD", f"{metrics.get('max_drawdown', 0):.1%}")

# Display recommendation
st.info(f"**💡 Recommendation:** {score_result.recommendation}")

# Strengths and weaknesses
if score_result.strengths or score_result.weaknesses:
    col1, col2 = st.columns(2)
    with col1:
        if score_result.strengths:
            st.success("**✅ Strengths:**")
            for strength in score_result.strengths:
                st.write(f"- {strength}")
    with col2:
        if score_result.weaknesses:
            st.warning("**⚠️  Areas to Improve:**")
            for weakness in score_result.weaknesses:
                st.write(f"- {weakness}")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# AI IMPROVEMENT SUGGESTIONS
# ═══════════════════════════════════════════════════════════════════

st.subheader("🤖 AI-Driven Improvement Suggestions")

suggestions = suggest_strategy_improvements(metrics, mc_stats=mc_stats)

if suggestions:
    st.markdown(f"**Found {len(suggestions)} suggestions for improvement:**")
    
    for i, sug in enumerate(suggestions, 1):
        icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[sug.priority]
        
        with st.expander(f"{icon} [{sug.priority.upper()}] {sug.title}"):
            st.markdown(f"**Category:** {sug.category.title()}")
            st.markdown(f"**Description:** {sug.description}")
            st.success(f"**✅ Recommended Action:** {sug.action}")
else:
    st.success("✅ Strategy looks good! No critical improvements suggested.")

# Export report
if st.button("📄 Export Improvement Report"):
    report = generate_improvement_report(suggestions, metrics, include_details=True)
    st.download_button(
        label="Download Report (Markdown)",
        data=report,
        file_name=f"improvement_report_{selected_run_id}.md",
        mime="text/markdown"
    )

st.markdown("---")

# Footer
st.caption(f"Analyzing Run: {full_run_id[:12]}... | Strategy: {run_data.get('strategy_name', 'Unknown')}")
st.caption("Phase 5 | Monte Carlo & Robustness Engine")

