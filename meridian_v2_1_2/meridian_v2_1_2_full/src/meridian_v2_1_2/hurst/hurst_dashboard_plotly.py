"""
Interactive Plotly Dashboard for Hurst Analysis

Professional interactive Sentient Trader-style interface with:
- Multi-cycle peaks + troughs
- Cycle arcs
- Hoverable cycle markers
- Toggle visibility for cycle degrees
- Zoom / pan
- Projection windows
- Cycle timing bars
- Dark mode option
- Real-time re-rendering after right-translation
"""

import plotly.graph_objs as go
import pandas as pd
import numpy as np
from typing import Dict, List

from .hurst_visual_full import (
    CYCLE_COLORS,
    detect_peaks_from_phase
)


def plot_sentient_dashboard(price: pd.Series,
                            phasing_results: Dict[int, dict],
                            title="Sentient Trader – Interactive Dashboard",
                            dark_mode=False):
    """
    Full Plotly dashboard replicating Sentient Trader's interface:
      - interactive peaks/troughs
      - cycle arcs
      - projection regions
      - zoom/pan
      - show/hide cycles by legend click
    
    Args:
        price: Price series with DatetimeIndex
        phasing_results: Results from HurstPhasingEngine.phase_all()
        title: Chart title
        dark_mode: Use dark theme
    
    Returns:
        Plotly figure object
    
    Example:
        >>> from meridian_v2_1_2.hurst import HurstPhasingEngine
        >>> from meridian_v2_1_2.hurst.hurst_dashboard_plotly import plot_sentient_dashboard
        >>> 
        >>> phaser = HurstPhasingEngine([20, 40, 80])
        >>> results = phaser.phase_all(price)
        >>> 
        >>> fig = plot_sentient_dashboard(price, results)
        >>> fig.show()  # Opens in browser
    """

    fig = go.Figure()

    # Base price series
    fig.add_trace(go.Scatter(
        x=price.index,
        y=price.values,
        mode="lines",
        name="Price",
        line=dict(color="black", width=1.5),
        hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))

    for period, res in sorted(phasing_results.items(), key=lambda x: x[0]):

        color = CYCLE_COLORS.get(period, "#888")
        troughs = res["troughs"]
        phase = res["phase"]

        # -------------------------
        # TROUGH markers
        # -------------------------
        if len(troughs) > 0:
            fig.add_trace(go.Scatter(
                x=troughs,
                y=price.loc[troughs],
                mode="markers",
                name=f"{period}-bar troughs",
                marker=dict(
                    size=12 + period * 0.1,
                    color=color,
                    line=dict(width=1, color="black")
                ),
                hovertemplate=f"{period}-bar trough<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>"
            ))

        # -------------------------
        # PEAK markers
        # -------------------------
        peaks = detect_peaks_from_phase(price, phase)
        if len(peaks) > 0:
            fig.add_trace(go.Scatter(
                x=peaks,
                y=price.loc[peaks],
                mode="markers",
                name=f"{period}-bar peaks",
                marker=dict(
                    size=10 + period * 0.08,
                    color="rgba(0,0,0,0)",
                    line=dict(color=color, width=2),
                    symbol="circle-open"
                ),
                hovertemplate=f"{period}-bar peak<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>"
            ))

        # -------------------------
        # PROJECTION window
        # -------------------------
        if len(troughs) > 0:
            last = troughs[-1]
            start = last + pd.Timedelta(days=int(period * 0.75))
            end   = last + pd.Timedelta(days=int(period * 1.25))

            fig.add_vrect(
                x0=start,
                x1=end,
                fillcolor=color,
                opacity=0.08,
                layer="below",
                line_width=0,
                annotation_text=f"{period}d projection",
                annotation_position="top left"
            )

        # -------------------------
        # ARC (using a dense curve)
        # -------------------------
        if len(troughs) > 1:
            for i in range(len(troughs) - 1):
                t1, t2 = troughs[i], troughs[i+1]

                xs = pd.date_range(t1, t2, periods=60)
                midpoint = price.loc[t1:t2].median()
                width = (t2 - t1).days

                ys = midpoint + (width/6) * np.sin(
                    np.linspace(0, np.pi, len(xs))
                )

                fig.add_trace(go.Scatter(
                    x=xs,
                    y=ys,
                    mode="lines",
                    name=f"{period}-bar arc",
                    line=dict(color=color, width=1.2, dash="dot"),
                    opacity=0.7,
                    visible="legendonly",  # hide arcs by default
                    hoverinfo='skip'
                ))

    # Figure layout
    template = "plotly_dark" if dark_mode else "plotly_white"
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        template=template,
        hovermode="x unified",
        legend=dict(
            orientation="v",
            x=1.02,
            y=1,
            bgcolor="rgba(255,255,255,0.6)" if not dark_mode else "rgba(0,0,0,0.6)"
        ),
        margin=dict(l=40, r=250, t=80, b=40),
        height=800,
        xaxis_title="Date",
        yaxis_title="Price"
    )

    fig.update_xaxes(showgrid=True, rangeslider_visible=False)
    fig.update_yaxes(showgrid=True)

    return fig


def create_multi_cycle_comparison(price: pd.Series,
                                 phasing_results: Dict[int, dict],
                                 title="Multi-Cycle Phase Comparison"):
    """
    Create subplot dashboard comparing all cycle phases.
    
    Args:
        price: Price series
        phasing_results: Phasing results
        title: Dashboard title
    
    Returns:
        Plotly figure with subplots
    """
    from plotly.subplots import make_subplots
    
    n_cycles = len(phasing_results)
    
    fig = make_subplots(
        rows=n_cycles + 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=['Price'] + [f'{p}-bar Phase' for p in sorted(phasing_results.keys())]
    )
    
    # Add price on top subplot
    fig.add_trace(
        go.Scatter(x=price.index, y=price.values, mode='lines', name='Price', line=dict(color='black')),
        row=1, col=1
    )
    
    # Add each cycle phase
    for idx, (period, res) in enumerate(sorted(phasing_results.items()), start=2):
        phase = res['phase']
        color = CYCLE_COLORS.get(period, '#888')
        
        if not phase.empty:
            fig.add_trace(
                go.Scatter(
                    x=phase.index, 
                    y=phase.values, 
                    mode='lines', 
                    name=f'{period}-bar', 
                    line=dict(color=color)
                ),
                row=idx, col=1
            )
            
            # Add trough markers
            troughs = res['troughs']
            if len(troughs) > 0:
                fig.add_trace(
                    go.Scatter(
                        x=troughs,
                        y=[0] * len(troughs),
                        mode='markers',
                        marker=dict(size=10, color=color, symbol='triangle-up'),
                        name=f'{period} troughs',
                        showlegend=False
                    ),
                    row=idx, col=1
                )
    
    fig.update_layout(
        title=title,
        height=300 + n_cycles * 150,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

