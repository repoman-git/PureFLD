"""
Multi-Run Comparison Dashboard

Compare multiple backtest runs side-by-side.
"""

import streamlit as st
import pandas as pd
from meridian_v2_1_2.storage import load_all_runs, get_registry_stats
from meridian_v2_1_2.dashboard.components.backtest_viz import comparison_chart, metrics_table
import plotly.graph_objects as go

st.set_page_config(
    page_title="Meridian - Multi-Run Compare",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Multi-Run Comparison")
st.markdown("*Compare multiple backtest runs side-by-side*")
st.markdown("---")

# Load all runs
runs = load_all_runs()
stats = get_registry_stats()

if not runs:
    st.info("📭 No backtest runs found in the registry.")
    st.markdown("""
    **Get Started:**
    1. Run a backtest in the Notebook Editor
    2. Or create a backtest using the API
    3. Results will appear here for comparison
    """)
    st.stop()

# Display registry stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Runs", stats.get('total_runs', 0))
with col2:
    st.metric("Successful", stats.get('successful_runs', 0))
with col3:
    st.metric("Failed", stats.get('failed_runs', 0))
with col4:
    st.metric("Strategies", len(stats.get('strategies', {})))

st.markdown("---")

# Filter options
st.subheader("🔍 Filter Runs")

col1, col2, col3 = st.columns(3)

with col1:
    # Strategy filter
    strategies = sorted(set(r.get('strategy_name', 'Unknown') for r in runs))
    selected_strategy = st.selectbox("Strategy", ["All"] + strategies)

with col2:
    # Success filter
    success_filter = st.selectbox("Status", ["All", "Successful Only", "Failed Only"])

with col3:
    # Date range
    show_recent = st.number_input("Show last N runs", min_value=1, max_value=100, value=20)

# Apply filters
filtered_runs = runs

if selected_strategy != "All":
    filtered_runs = [r for r in filtered_runs if r.get('strategy_name') == selected_strategy]

if success_filter == "Successful Only":
    filtered_runs = [r for r in filtered_runs if r.get('success', False)]
elif success_filter == "Failed Only":
    filtered_runs = [r for r in filtered_runs if not r.get('success', False)]

# Limit to recent
filtered_runs = filtered_runs[:show_recent]

st.markdown("---")

# Multi-select for comparison
st.subheader("📋 Select Runs to Compare")

if not filtered_runs:
    st.warning("No runs match the filter criteria")
    st.stop()

# Create a DataFrame for selection
runs_data = []
for run in filtered_runs:
    runs_data.append({
        'Select': False,
        'Run ID': run.get('run_id', 'N/A'),
        'Strategy': run.get('strategy_name', 'Unknown'),
        'Timestamp': run.get('timestamp', '')[:16],
        'Sharpe': run.get('metrics', {}).get('sharpe_ratio', 0),
        'Return': run.get('metrics', {}).get('total_return', 0),
        'Max DD': run.get('metrics', {}).get('max_drawdown', 0),
        'Trades': run.get('num_trades', 0),
        'Success': '✅' if run.get('success') else '❌'
    })

df = pd.DataFrame(runs_data)

# Display with selection
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)

# Manual selection via multiselect
run_ids = [r.get('run_id') for r in filtered_runs]
run_labels = [f"{r.get('run_id', 'N/A')[:8]} - {r.get('strategy_name', 'Unknown')}" for r in filtered_runs]

selected_labels = st.multiselect(
    "Select runs to compare (max 5)",
    run_labels,
    max_selections=5
)

if not selected_labels:
    st.info("👆 Select one or more runs to compare")
    st.stop()

# Get selected runs
selected_ids = [label.split(' - ')[0] for label in selected_labels]
selected_runs = [r for r in filtered_runs if r.get('run_id', '')[:8] in selected_ids]

st.markdown("---")

# Comparison visualization
st.subheader("📈 Equity Curve Comparison")

fig = go.Figure()

for run in selected_runs:
    equity = run.get('equity_summary', {})
    if equity:
        # Create a simple line from initial to final
        label = f"{run.get('run_id', '')[:8]} - {run.get('strategy_name', 'Unknown')}"
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[equity.get('initial', 0), equity.get('final', 0)],
            mode='lines+markers',
            name=label,
            line=dict(width=2),
            marker=dict(size=8)
        ))

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Equity ($)",
    hovermode='x unified',
    template='plotly_white',
    height=500,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

st.caption("⚠️ Note: Full equity curves not stored in registry. Summary shown (initial → final).")

st.markdown("---")

# Metrics comparison
st.subheader("📊 Performance Metrics Comparison")

metrics_data = []
for run in selected_runs:
    run_id_short = run.get('run_id', 'N/A')[:8]
    metrics = run.get('metrics', {})
    
    metrics_data.append({
        'Run ID': run_id_short,
        'Strategy': run.get('strategy_name', 'Unknown'),
        'Sharpe': f"{metrics.get('sharpe_ratio', 0):.2f}",
        'Total Return': f"{metrics.get('total_return', 0):.2%}",
        'Max Drawdown': f"{metrics.get('max_drawdown', 0):.2%}",
        'Win Rate': f"{metrics.get('win_rate', 0):.2%}",
        'Profit Factor': f"{metrics.get('profit_factor', 0):.2f}",
        'Trades': metrics.get('num_trades', 0),
        'Final Equity': f"${metrics.get('final_equity', 0):,.0f}"
    })

comparison_df = pd.DataFrame(metrics_data)
st.dataframe(comparison_df, use_container_width=True, hide_index=True)

# Best performers
st.markdown("---")
st.subheader("🏆 Best Performers")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Highest Sharpe:**")
    best_sharpe = max(selected_runs, key=lambda r: r.get('metrics', {}).get('sharpe_ratio', -999))
    st.metric(
        best_sharpe.get('run_id', '')[:8],
        f"{best_sharpe.get('metrics', {}).get('sharpe_ratio', 0):.2f}"
    )

with col2:
    st.markdown("**Highest Return:**")
    best_return = max(selected_runs, key=lambda r: r.get('metrics', {}).get('total_return', -999))
    st.metric(
        best_return.get('run_id', '')[:8],
        f"{best_return.get('metrics', {}).get('total_return', 0):.2%}"
    )

with col3:
    st.markdown("**Lowest Drawdown:**")
    best_dd = max(selected_runs, key=lambda r: -r.get('metrics', {}).get('max_drawdown', 999))
    st.metric(
        best_dd.get('run_id', '')[:8],
        f"{best_dd.get('metrics', {}).get('max_drawdown', 0):.2%}"
    )

# Export
st.markdown("---")
st.subheader("📤 Export Comparison")

if st.button("📋 Copy Metrics to Clipboard"):
    st.code(comparison_df.to_csv(index=False))
    st.success("✅ Data ready to copy!")

if st.button("💾 Download as CSV"):
    csv = comparison_df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="backtest_comparison.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption(f"📊 Comparing {len(selected_runs)} runs | {stats.get('total_runs', 0)} total in registry")
st.caption("Phase 4B | Multi-Run Comparison")


