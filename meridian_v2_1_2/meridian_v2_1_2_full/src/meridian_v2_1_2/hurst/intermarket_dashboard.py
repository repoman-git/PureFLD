"""
Intermarket Dashboard (Plotly)

Multi-panel interactive dashboard showing:
- Lead/Lag matrix (who leads cycles)
- Cycle synchrony heatmap
- Intermarket pressure vectors
- Composite intermarket cycle
- Turning point alignment
- Forecast overlays

This is a cycle-aware Bloomberg MAP screen equivalent.

Professional macro PM tool for:
- Gold vs USD relationships
- Equity vs Bond cycles
- Commodity synchronization
- Multi-market regime detection
"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd


def intermarket_dashboard(results,
                          title="Intermarket Cycle Intelligence Dashboard"):
    """
    Build a full multi-panel dashboard showing:
    - Lead/Lag Matrix
    - Cycle Synchrony Heatmap
    - Intermarket Pressure Vector
    - Composite Intermarket Cycle
    - Turning Point Alignment (TPA)
    - Forecast Overlays

    Args:
        results: Output from IntermarketCycleEngine.analyze()
        title: Dashboard title
    
    Returns:
        Plotly figure with 6 panels
    
    Example:
        >>> from meridian_v2_1_2.hurst import IntermarketCycleEngine
        >>> from meridian_v2_1_2.hurst.intermarket_dashboard import intermarket_dashboard
        >>> 
        >>> engine = IntermarketCycleEngine()
        >>> results = engine.analyze(price_dict)
        >>> 
        >>> fig = intermarket_dashboard(results)
        >>> fig.show()
    
    Dashboard Panels:
    1. Lead/Lag Matrix - Green=leading, Red=lagging
    2. Cycle Synchrony - Blue=shared cycles
    3. Pressure Vector - Green=up, Red=down
    4. Composite Cycle - Single dominant period
    5. Turning Point Alignment - Trough clusters
    6. Forecast Overlays - AI predictions
    """
    harmonics = results["harmonics"]
    phasing = results["phasing"]
    forecasts = results["forecasts"]
    lead_lag = results["lead_lag"]
    pressure = results["pressure_vector"]
    comp_cycle = results["composite_cycle"]
    tpa = results["turning_point_alignment"]

    symbols = list(harmonics.keys())

    # --------------------------------------------------------------------
    # BUILD THE 2x3 LAYOUT
    # --------------------------------------------------------------------
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=[
            "Lead/Lag Matrix",
            "Cycle Synchrony Heatmap",
            "Intermarket Pressure Vector",
            "Composite Intermarket Cycle",
            "Turning Point Alignment",
            "Forecast Overlays (20-bar)"
        ],
        specs=[
            [{"type": "heatmap"}, {"type": "heatmap"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "bar"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.12,
        row_heights=[0.55, 0.45]
    )

    # --------------------------------------------------------------------
    # 1. Lead/Lag Matrix
    # --------------------------------------------------------------------
    leadlag_matrix = lead_lag.astype(float).values
    
    fig.add_trace(
        go.Heatmap(
            z=leadlag_matrix,
            x=symbols,
            y=symbols,
            colorscale="RdYlGn",
            zmid=0,
            colorbar=dict(title="Lead → Lag", x=0.32),
            hovertemplate='%{y} vs %{x}<br>Lead/Lag: %{z:.3f}<extra></extra>'
        ),
        row=1,
        col=1
    )

    # --------------------------------------------------------------------
    # 2. Cycle Synchrony Heatmap
    # --------------------------------------------------------------------
    # Build synchrony map: cycles x symbols
    all_cycles = sorted({
        c for sym in harmonics for c in harmonics[sym]["dominant_cycles"]
    })
    
    if all_cycles:
        matrix = []
        for cycle in all_cycles:
            row = []
            for sym in symbols:
                cycles = harmonics[sym]["dominant_cycles"]
                row.append(1 if cycle in cycles else 0)
            matrix.append(row)
        
        fig.add_trace(
            go.Heatmap(
                z=matrix,
                x=symbols,
                y=all_cycles,
                colorscale="Blues",
                showscale=False,
                hovertemplate='Cycle: %{y} days<br>%{x}: %{z}<extra></extra>'
            ),
            row=1,
            col=2
        )

    # --------------------------------------------------------------------
    # 3. Intermarket Pressure Vector
    # --------------------------------------------------------------------
    fig.add_trace(
        go.Bar(
            x=pressure.index,
            y=pressure.values,
            marker_color=[
                "green" if v > 0 else "red" for v in pressure.values
            ],
            name="Pressure",
            hovertemplate='%{x}<br>Pressure: %{y:.4f}<extra></extra>'
        ),
        row=1,
        col=3
    )

    # --------------------------------------------------------------------
    # 4. Composite Intermarket Cycle (scalar display)
    # --------------------------------------------------------------------
    cycle_text = f"{comp_cycle} days" if comp_cycle else "N/A"
    
    fig.add_trace(
        go.Scatter(
            x=[0.5],
            y=[0.5],
            mode="text",
            text=[cycle_text],
            textfont=dict(size=40, color="purple"),
            showlegend=False,
            hoverinfo='skip'
        ),
        row=2,
        col=1
    )
    
    # Add label
    fig.add_annotation(
        text="Dominant Cycle",
        xref="x4", yref="y4",
        x=0.5, y=0.2,
        showarrow=False,
        font=dict(size=14)
    )

    # --------------------------------------------------------------------
    # 5. Turning Point Alignment Histogram
    # --------------------------------------------------------------------
    fig.add_trace(
        go.Bar(
            x=tpa.index,
            y=tpa.values,
            marker_color="teal",
            name="TP Alignment",
            hovertemplate='Date: %{x}<br>Markets Aligned: %{y}<extra></extra>'
        ),
        row=2,
        col=2
    )

    # --------------------------------------------------------------------
    # 6. Forecast Overlays
    # --------------------------------------------------------------------
    for sym, fc in forecasts.items():
        fig.add_trace(
            go.Scatter(
                x=fc.index,
                y=fc.values,
                mode="lines",
                name=f"{sym} Forecast",
                line=dict(width=1.6),
                hovertemplate=f'{sym}<br>Date: %{{x}}<br>Forecast: %{{y:.2f}}<extra></extra>'
            ),
            row=2,
            col=3
        )

    # --------------------------------------------------------------------
    # FINAL LAYOUT
    # --------------------------------------------------------------------
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        template="plotly_white",
        height=1100,
        margin=dict(l=40, r=40, t=120, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.05,
            xanchor="center", x=0.5
        )
    )
    
    # Update x-axis for composite cycle panel
    fig.update_xaxes(showticklabels=False, showgrid=False, row=2, col=1)
    fig.update_yaxes(showticklabels=False, showgrid=False, row=2, col=1)

    return fig


def create_macro_regime_view(results, title="Macro Cycle Regime Analysis"):
    """
    Simplified view focusing on regime interpretation.
    
    Args:
        results: Intermarket analysis results
        title: Chart title
    
    Returns:
        Plotly figure
    """
    pressure = results["pressure_vector"]
    comp_cycle = results["composite_cycle"]
    
    # Determine overall regime
    avg_pressure = pressure.mean()
    
    if avg_pressure > 0.01:
        regime = "RISK-ON (Bullish Cycle Pressure)"
        color = "green"
    elif avg_pressure < -0.01:
        regime = "RISK-OFF (Bearish Cycle Pressure)"
        color = "red"
    else:
        regime = "NEUTRAL (Mixed Cycle Signals)"
        color = "gray"
    
    fig = go.Figure()
    
    # Pressure bars
    fig.add_trace(go.Bar(
        x=pressure.index,
        y=pressure.values,
        marker_color=[
            "green" if v > 0 else "red" for v in pressure.values
        ],
        name="Pressure Vector",
        hovertemplate='%{x}<br>Pressure: %{y:.4f}<extra></extra>'
    ))
    
    # Add regime annotation
    fig.add_annotation(
        text=f"Current Regime: {regime}",
        xref="paper", yref="paper",
        x=0.5, y=1.1,
        showarrow=False,
        font=dict(size=18, color=color),
        bgcolor="white",
        bordercolor=color,
        borderwidth=2
    )
    
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=500,
        xaxis_title="Asset",
        yaxis_title="Cycle Pressure"
    )
    
    return fig

