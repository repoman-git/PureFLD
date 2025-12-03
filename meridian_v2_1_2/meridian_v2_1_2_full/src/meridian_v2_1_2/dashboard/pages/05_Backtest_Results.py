"""
Backtest Results Dashboard

View, manage, and analyze all backtest runs from the registry.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from meridian_v2_1_2.storage import load_all_runs, load_run_by_id, delete_run, get_registry_stats
from meridian_v2_1_2.dashboard.components.backtest_viz import (
    backtest_summary, 
    plot_equity_with_drawdown,
    metrics_table,
    trades_table
)

st.set_page_config(
    page_title="Meridian - Backtest Results",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Backtest Results")
st.markdown("*View and manage all backtest runs*")
st.markdown("---")

# Load all runs
runs = load_all_runs()
stats = get_registry_stats()

# Display registry statistics
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

# Check if there are any runs
if not runs:
    st.info("📭 No backtest runs found in the registry.")
    st.markdown("""
    **Get Started:**
    1. Open the **Notebook Editor** page
    2. Load or create a notebook with backtest code
    3. Click **🚀 Run as Backtest** on a code cell
    4. Results will appear here automatically
    
    **Or use the API:**
    ```python
    from meridian_v2_1_2.api import run_backtest
    from meridian_v2_1_2.storage import save_run
    
    result = run_backtest("FLD", {'fld_offset': 10})
    save_run(result.to_dict())
    ```
    """)
    st.stop()

# ═══════════════════════════════════════════════════════════════════
# FILTER CONTROLS
# ═══════════════════════════════════════════════════════════════════

st.subheader("🔍 Filter Runs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Strategy filter
    strategies = sorted(set(r.get('strategy_name', 'Unknown') for r in runs))
    selected_strategy = st.selectbox("Strategy", ["All"] + strategies)

with col2:
    # Success filter
    success_filter = st.selectbox("Status", ["All", "Successful Only", "Failed Only"])

with col3:
    # Sort by
    sort_by = st.selectbox("Sort By", ["Date (Newest)", "Date (Oldest)", "Sharpe (High)", "Return (High)", "Drawdown (Low)"])

with col4:
    # Show limit
    show_limit = st.number_input("Show Runs", min_value=5, max_value=100, value=20, step=5)

# Apply filters
filtered_runs = runs

if selected_strategy != "All":
    filtered_runs = [r for r in filtered_runs if r.get('strategy_name') == selected_strategy]

if success_filter == "Successful Only":
    filtered_runs = [r for r in filtered_runs if r.get('success', False)]
elif success_filter == "Failed Only":
    filtered_runs = [r for r in filtered_runs if not r.get('success', False)]

# Apply sorting
if sort_by == "Date (Oldest)":
    filtered_runs = list(reversed(filtered_runs))
elif sort_by == "Sharpe (High)":
    filtered_runs = sorted(filtered_runs, key=lambda r: r.get('metrics', {}).get('sharpe_ratio', -999), reverse=True)
elif sort_by == "Return (High)":
    filtered_runs = sorted(filtered_runs, key=lambda r: r.get('metrics', {}).get('total_return', -999), reverse=True)
elif sort_by == "Drawdown (Low)":
    filtered_runs = sorted(filtered_runs, key=lambda r: -r.get('metrics', {}).get('max_drawdown', 999), reverse=True)

# Limit results
filtered_runs = filtered_runs[:show_limit]

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# RESULTS TABLE
# ═══════════════════════════════════════════════════════════════════

st.subheader(f"📊 Results ({len(filtered_runs)} runs)")

if not filtered_runs:
    st.warning("No runs match the filter criteria")
    st.stop()

# Create results DataFrame
results_data = []
for run in filtered_runs:
    metrics = run.get('metrics', {})
    results_data.append({
        'Run ID': run.get('run_id', 'N/A')[:8] + '...',
        'Strategy': run.get('strategy_name', 'Unknown'),
        'Date': run.get('timestamp', '')[:16],
        'Sharpe': f"{metrics.get('sharpe_ratio', 0):.2f}",
        'Return': f"{metrics.get('total_return', 0):.2%}",
        'Max DD': f"{metrics.get('max_drawdown', 0):.2%}",
        'Win Rate': f"{metrics.get('win_rate', 0):.2%}",
        'Trades': metrics.get('num_trades', 0),
        'Final $': f"${metrics.get('final_equity', 0):,.0f}",
        'Status': '✅' if run.get('success') else '❌',
        'Full ID': run.get('run_id', 'N/A')
    })

df = pd.DataFrame(results_data)

# Display table
st.dataframe(
    df.drop(columns=['Full ID']),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# RUN SELECTION AND DETAILS
# ═══════════════════════════════════════════════════════════════════

st.subheader("🔎 View Run Details")

# Select run to view
run_options = [f"{r['Run ID']} - {r['Strategy']} ({r['Date']})" for r in results_data]
selected_option = st.selectbox("Select a run to view details", [""] + run_options)

if selected_option:
    # Find the selected run
    selected_idx = run_options.index(selected_option)
    selected_run_id = results_data[selected_idx]['Full ID']
    
    # Load full run data
    run_data = load_run_by_id(selected_run_id)
    
    if run_data:
        # Display full summary
        st.markdown("---")
        
        # Action buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
        
        with col1:
            if st.button("🗑️ Delete Run", key="delete_run"):
                if delete_run(selected_run_id):
                    st.success("Run deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete run")
        
        with col2:
            if st.button("📋 Copy ID", key="copy_id"):
                st.code(selected_run_id)
                st.success("ID displayed above!")
        
        with col3:
            if st.button("📊 Compare", key="compare_run"):
                st.info("Navigate to 'Multi-Run Compare' page to compare runs")
        
        st.markdown("---")
        
        # Display comprehensive backtest summary
        backtest_summary(run_data)
        
        # Additional details in expandable sections
        with st.expander("📝 Run Metadata", expanded=False):
            st.json({
                'run_id': run_data.get('run_id'),
                'strategy_name': run_data.get('strategy_name'),
                'timestamp': run_data.get('timestamp'),
                'success': run_data.get('success'),
                'params': run_data.get('params', {}),
                'initial_capital': run_data.get('initial_capital'),
                'num_trades': run_data.get('num_trades')
            })
        
        with st.expander("📈 Equity Summary", expanded=False):
            equity = run_data.get('equity_summary', {})
            if equity:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Initial", f"${equity.get('initial', 0):,.2f}")
                with col2:
                    st.metric("Final", f"${equity.get('final', 0):,.2f}")
                with col3:
                    st.metric("Peak", f"${equity.get('peak', 0):,.2f}")
                with col4:
                    st.metric("Trough", f"${equity.get('trough', 0):,.2f}")
            else:
                st.info("No equity summary available")
        
        with st.expander("⚠️ Logs & Errors", expanded=False):
            logs = run_data.get('logs', [])
            if logs:
                for log in logs[-20:]:  # Show last 20 logs
                    st.text(log)
            else:
                st.info("No logs available")
            
            if not run_data.get('success'):
                error = run_data.get('error', 'Unknown error')
                st.error(f"**Error:** {error}")
    else:
        st.error("Failed to load run data")

# ═══════════════════════════════════════════════════════════════════
# BULK ACTIONS
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.subheader("🔧 Bulk Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ Delete All Failed Runs", key="delete_failed"):
        failed_runs = [r for r in runs if not r.get('success', False)]
        if failed_runs:
            for run in failed_runs:
                delete_run(run.get('run_id'))
            st.success(f"Deleted {len(failed_runs)} failed runs")
            st.rerun()
        else:
            st.info("No failed runs to delete")

with col2:
    if st.button("📊 Export All to CSV", key="export_csv"):
        csv = df.drop(columns=['Full ID']).to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="backtest_results.csv",
            mime="text/csv"
        )

with col3:
    if st.button("🔄 Refresh Data", key="refresh"):
        st.rerun()

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.caption(f"📊 Showing {len(filtered_runs)} of {len(runs)} total runs")
st.caption("Phase 4 | Backtest Results Registry")
st.caption("💡 Tip: Use the Multi-Run Compare page to overlay multiple equity curves")

