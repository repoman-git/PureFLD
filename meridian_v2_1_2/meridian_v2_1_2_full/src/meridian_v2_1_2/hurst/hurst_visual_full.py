"""
Sentient Trader-Style Visualization

Full professional cycle visualization with:
- Multi-degree cycle peaks & troughs
- Color/size coding by cycle period
- Timing arcs between troughs
- Future projection windows
- Cycle timing bars
- Nesting bands
- Interactive overlays

Replicates the professional Sentient Trader visual system.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from typing import Dict, List, Optional


# =============================================================================
# SENTIENT TRADER–STYLE VISUAL SPEC
# =============================================================================

CYCLE_COLORS = {
    20:  "#ffcc00",   # yellow
    40:  "#ff9900",   # orange
    80:  "#3366ff",   # blue
    160: "#9933ff",   # purple
    320: "#009966",   # green
    640: "#cc0000",   # red
}

CYCLE_SIZES = {
    20:  30,
    40:  45,
    80:  65,
    160: 90,
    320: 130,
    640: 180,
}


# =============================================================================
# HELPER: PEAK DETECTION (phase + local maxima)
# =============================================================================

def detect_peaks_from_phase(price: pd.Series,
                            phase: pd.Series,
                            window: int = 3) -> List[pd.Timestamp]:
    """Detect peaks approximately halfway through the cycle."""
    peaks = []
    phase_mask = (phase > 0.45) & (phase < 0.65)
    candidates = price[phase_mask].index

    for ts in candidates:
        local = price.loc[ts - pd.Timedelta(days=window): ts + pd.Timedelta(days=window)]
        if len(local) >= 3 and price.loc[ts] == local.max():
            peaks.append(ts)

    return sorted(peaks)


# =============================================================================
# HELPER: DRAW TIMING ARC (cycle arc)
# =============================================================================

def draw_arc(ax, t1, t2, y_level, color):
    """
    Draw a semicircular arc between two troughs (Sentient Trader style).
    """
    x1 = t1.value
    x2 = t2.value
    xm = (x1 + x2) / 2       # center x in timestamp space
    radius = (x2 - x1) / 2

    # Convert timestamps to matplotlib axis coordinates
    x_conv = [pd.to_datetime(t1), pd.to_datetime(t2)]
    x_start = ax.transData.transform((x_conv[0], y_level))
    x_end   = ax.transData.transform((x_conv[1], y_level))

    # We draw using a patches.Arc in data coords
    arc = patches.Arc(
        xy=(pd.to_datetime((t1 + (t2 - t1) / 2)), y_level),
        width=(t2 - t1).days,
        height=(t2 - t1).days * 0.5,
        angle=0,
        theta1=0,
        theta2=180,
        color=color,
        linewidth=1.2,
        alpha=0.6,
        zorder=3
    )
    ax.add_patch(arc)


# =============================================================================
# HELPER: DRAW CYCLE TIMING BARS (bottom strip)
# =============================================================================

def draw_cycle_bar(ax, price_index, troughs, nominal_period, color):
    """
    Draw horizontal bars under chart showing cycle positions.
    """
    if len(troughs) < 2:
        return

    y_min, _ = ax.get_ylim()
    bar_y = y_min - (0.03 * (nominal_period / 20))  # compress multiple cycles

    for i in range(len(troughs) - 1):
        start = troughs[i]
        end = troughs[i + 1]
        ax.axhline(
            y=bar_y,
            xmin=(start - price_index[0]) / (price_index[-1] - price_index[0]),
            xmax=(end - price_index[0]) / (price_index[-1] - price_index[0]),
            color=color,
            linewidth=6,
            alpha=0.7
        )


# =============================================================================
# HELPER: FUTURE PROJECTION REGION
# =============================================================================

def draw_projection_region(ax,
                           last_trough,
                           nominal_period,
                           color):
    """
    Show the projected next trough time window.
    """
    start = last_trough + pd.Timedelta(days=int(nominal_period * 0.75))
    end   = last_trough + pd.Timedelta(days=int(nominal_period * 1.25))
    ax.axvspan(start, end, color=color, alpha=0.08)


# =============================================================================
# MAIN: SENTIENT TRADER–STYLE PLOT
# =============================================================================

def plot_sentient_trader_full(price: pd.Series,
                              phasing_results: Dict[int, dict],
                              show_peaks=True,
                              show_arcs=True,
                              show_projection=True,
                              show_cycle_bars=True,
                              title="Sentient Trader–Style Full Cycle Plot"):
    """
    Full Sentient Trader visual replication:
      - multi-degree troughs
      - inferred peaks
      - timing arcs between troughs
      - future trough projection
      - bottom cycle bars
      - full color/size coding
    
    Args:
        price: Price series (pandas Series with DatetimeIndex)
        phasing_results: Dict from HurstPhasingEngine.phase_all()
        show_peaks: Show cycle peaks
        show_arcs: Show timing arcs between troughs
        show_projection: Show future projection windows
        show_cycle_bars: Show cycle timing bars at bottom
        title: Chart title
    
    Returns:
        matplotlib figure
    
    Example:
        >>> from meridian_v2_1_2.hurst import HurstPhasingEngine
        >>> from meridian_v2_1_2.hurst.hurst_visual_full import plot_sentient_trader_full
        >>> 
        >>> phaser = HurstPhasingEngine([20, 40, 80])
        >>> results = phaser.phase_all(price)
        >>> 
        >>> plot_sentient_trader_full(price, results, title="GLD - Full Cycle Analysis")
    """

    fig, ax = plt.subplots(figsize=(20, 12))
    ax.plot(price, color="black", linewidth=1.2)

    ymin, ymax = ax.get_ylim()

    # Loop cycles smallest → largest
    for period, result in sorted(phasing_results.items(), key=lambda x: x[0]):
        troughs = result["troughs"]
        phase = result["phase"]

        if len(troughs) == 0:
            continue

        color = CYCLE_COLORS.get(period, "#888888")
        size  = CYCLE_SIZES.get(period, 40)

        # --------------------------------------------------------------
        # TROUGH MARKERS
        # --------------------------------------------------------------
        ax.scatter(troughs,
                   price.loc[troughs],
                   s=size,
                   color=color,
                   edgecolor="black",
                   linewidth=1.0,
                   alpha=0.95,
                   zorder=6,
                   label=f"{period}-bar troughs")

        # --------------------------------------------------------------
        # PEAK MARKERS (inferred)
        # --------------------------------------------------------------
        if show_peaks:
            peaks = detect_peaks_from_phase(price, phase)
            ax.scatter(
                peaks,
                price.loc[peaks],
                s=size * 0.6,
                facecolor="none",
                edgecolor=color,
                linewidth=1.6,
                zorder=5,
                alpha=0.9,
                label=f"{period}-bar peaks"
            )

        # --------------------------------------------------------------
        # ARC BETWEEN TROUGH PAIRS
        # --------------------------------------------------------------
        if show_arcs and len(troughs) > 1:
            for i in range(len(troughs) - 1):
                draw_arc(ax, troughs[i], troughs[i + 1], y_level=ymin + 0.05 * (period/20), color=color)

        # --------------------------------------------------------------
        # PROJECTION REGION
        # --------------------------------------------------------------
        if show_projection and len(troughs) > 0:
            draw_projection_region(ax, troughs[-1], period, color)

        # --------------------------------------------------------------
        # CYCLE TIMING BARS (bottom axis)
        # --------------------------------------------------------------
        if show_cycle_bars:
            draw_cycle_bar(ax, price.index, troughs, period, color)

    # --------------------------------------------------------------
    # FINAL DECORATION
    # --------------------------------------------------------------
    ax.set_title(title, fontsize=20, weight="bold")
    ax.set_xlabel("Date", fontsize=14)
    ax.set_ylabel("Price", fontsize=14)
    ax.grid(True, alpha=0.3)
    handles, labels = ax.get_legend_handles_labels()
    # Deduplicate legend entries
    unique = dict(zip(labels, handles))
    ax.legend(unique.values(), unique.keys(), fontsize=12, loc="upper left")
    plt.tight_layout()
    
    return fig


# =============================================================================
# INTERACTIVE PLOTLY VERSION
# =============================================================================

def plot_sentient_trader_interactive(price: pd.Series,
                                    phasing_results: Dict[int, dict],
                                    title="Interactive Cycle Analysis"):
    """
    Interactive Plotly version of Sentient Trader visualization.
    
    Features:
    - Zoom and pan
    - Hover tooltips
    - Show/hide cycle layers
    - Interactive legend
    
    Args:
        price: Price series
        phasing_results: Results from HurstPhasingEngine
        title: Chart title
    
    Returns:
        plotly figure
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
    except ImportError:
        print("Plotly not available. Install with: pip install plotly")
        return None
    
    fig = go.Figure()
    
    # Add price line
    fig.add_trace(go.Scatter(
        x=price.index,
        y=price.values,
        mode='lines',
        name='Price',
        line=dict(color='black', width=2),
        hovertemplate='Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))
    
    # Add cycle troughs and peaks
    for period, result in sorted(phasing_results.items()):
        troughs = result["troughs"]
        phase = result["phase"]
        
        if len(troughs) == 0:
            continue
        
        color = CYCLE_COLORS.get(period, "#888888")
        size = CYCLE_SIZES.get(period, 40) / 3  # Scale for Plotly
        
        # Troughs
        fig.add_trace(go.Scatter(
            x=troughs,
            y=price.loc[troughs],
            mode='markers',
            name=f'{period}-bar Troughs',
            marker=dict(
                size=size,
                color=color,
                line=dict(color='black', width=1)
            ),
            hovertemplate=f'Trough ({period}-bar)<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
        ))
        
        # Peaks
        peaks = detect_peaks_from_phase(price, phase)
        if len(peaks) > 0:
            fig.add_trace(go.Scatter(
                x=peaks,
                y=price.loc[peaks],
                mode='markers',
                name=f'{period}-bar Peaks',
                marker=dict(
                    size=size * 0.8,
                    color=color,
                    symbol='triangle-down',
                    line=dict(color='black', width=1)
                ),
                hovertemplate=f'Peak ({period}-bar)<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
            ))
    
    # Layout
    fig.update_layout(
        title=dict(text=title, font=dict(size=20)),
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode='x unified',
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

