"""
Backtest Visualization Components

Simple, reusable components for displaying backtest results.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Any


def plot_equity_curve(equity_curve: List[float], title: str = "Equity Curve"):
    """
    Plot an equity curve using Plotly.
    
    Args:
        equity_curve: List of equity values
        title: Chart title
    """
    if not equity_curve:
        st.warning("No equity data to display")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        y=equity_curve,
        mode='lines',
        name='Equity',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Time Period",
        yaxis_title="Equity ($)",
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def plot_equity_with_drawdown(equity_curve: List[float]):
    """
    Plot equity curve with drawdown overlay.
    
    Args:
        equity_curve: List of equity values
    """
    if not equity_curve:
        st.warning("No equity data to display")
        return
    
    # Calculate drawdown
    equity_series = pd.Series(equity_curve)
    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max * 100
    
    # Create subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=('Equity Curve', 'Drawdown %'),
        row_heights=[0.7, 0.3]
    )
    
    # Equity curve
    fig.add_trace(
        go.Scatter(y=equity_curve, mode='lines', name='Equity',
                  line=dict(color='#1f77b4', width=2)),
        row=1, col=1
    )
    
    # Drawdown
    fig.add_trace(
        go.Scatter(y=drawdown.tolist(), mode='lines', name='Drawdown',
                  line=dict(color='#d62728', width=2),
                  fill='tozeroy', fillcolor='rgba(214, 39, 40, 0.2)'),
        row=2, col=1
    )
    
    fig.update_xaxes(title_text="Time Period", row=2, col=1)
    fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    
    fig.update_layout(
        height=600,
        hovermode='x unified',
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def metrics_table(metrics: Dict[str, Any]):
    """
    Display metrics as a formatted table.
    
    Args:
        metrics: Dictionary of metric name -> value
    """
    if not metrics:
        st.info("No metrics available")
        return
    
    # Create formatted display
    col1, col2 = st.columns(2)
    
    metric_items = list(metrics.items())
    mid_point = len(metric_items) // 2
    
    with col1:
        for key, value in metric_items[:mid_point]:
            formatted_key = key.replace('_', ' ').title()
            
            if isinstance(value, float):
                if 'rate' in key or 'ratio' in key:
                    st.metric(formatted_key, f"{value:.2f}")
                elif 'return' in key or 'drawdown' in key:
                    st.metric(formatted_key, f"{value:.2%}")
                else:
                    st.metric(formatted_key, f"{value:,.2f}")
            else:
                st.metric(formatted_key, value)
    
    with col2:
        for key, value in metric_items[mid_point:]:
            formatted_key = key.replace('_', ' ').title()
            
            if isinstance(value, float):
                if 'rate' in key or 'ratio' in key:
                    st.metric(formatted_key, f"{value:.2f}")
                elif 'return' in key or 'drawdown' in key:
                    st.metric(formatted_key, f"{value:.2%}")
                else:
                    st.metric(formatted_key, f"{value:,.2f}")
            else:
                st.metric(formatted_key, value)


def trades_table(trades: List[Dict[str, Any]], max_rows: int = 20):
    """
    Display trades as a DataFrame table.
    
    Args:
        trades: List of trade dictionaries
        max_rows: Maximum number of rows to display
    """
    if not trades:
        st.info("No trades to display")
        return
    
    df = pd.DataFrame(trades)
    
    # Format columns if they exist
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    
    if 'price' in df.columns:
        df['price'] = df['price'].map('${:,.2f}'.format)
    
    if 'equity' in df.columns:
        df['equity'] = df['equity'].map('${:,.0f}'.format)
    
    # Display
    st.dataframe(
        df.head(max_rows),
        use_container_width=True,
        hide_index=True
    )
    
    if len(df) > max_rows:
        st.caption(f"Showing {max_rows} of {len(df)} trades")


def backtest_summary(result: Dict[str, Any]):
    """
    Complete backtest summary display.
    
    Args:
        result: Full backtest result dictionary
    """
    st.subheader("📊 Backtest Summary")
    
    # Header info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Strategy", result.get('strategy_name', 'Unknown'))
    
    with col2:
        st.metric("Run ID", result.get('run_id', 'N/A'))
    
    with col3:
        timestamp = result.get('timestamp', '')
        if timestamp:
            try:
                dt = pd.to_datetime(timestamp)
                st.metric("Date", dt.strftime('%Y-%m-%d %H:%M'))
            except:
                st.metric("Date", timestamp[:16])
    
    st.markdown("---")
    
    # Parameters
    if result.get('params'):
        with st.expander("⚙️ Parameters", expanded=False):
            st.json(result['params'])
    
    # Metrics
    st.markdown("### 📈 Performance Metrics")
    metrics_table(result.get('metrics', {}))
    
    st.markdown("---")
    
    # Equity curve
    st.markdown("### 💰 Equity Curve")
    if result.get('equity_curve'):
        plot_equity_with_drawdown(result['equity_curve'])
    else:
        st.warning("No equity curve data available")
    
    st.markdown("---")
    
    # Trades
    st.markdown("### 📝 Trade History")
    if result.get('trades'):
        trades_table(result['trades'])
    else:
        st.info("No trades executed")
    
    # Logs
    if result.get('logs'):
        with st.expander("📋 Execution Logs", expanded=False):
            for log in result['logs']:
                st.text(log)


def comparison_chart(results: List[Dict[str, Any]]):
    """
    Compare multiple backtest runs on one chart.
    
    Args:
        results: List of backtest result dictionaries
    """
    if not results:
        st.warning("No results to compare")
        return
    
    fig = go.Figure()
    
    for result in results:
        equity = result.get('equity_curve', [])
        if equity:
            label = f"{result.get('strategy_name', 'Unknown')} - {result.get('run_id', '')[:8]}"
            fig.add_trace(go.Scatter(
                y=equity,
                mode='lines',
                name=label
            ))
    
    fig.update_layout(
        title="Equity Curve Comparison",
        xaxis_title="Time Period",
        yaxis_title="Equity ($)",
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


