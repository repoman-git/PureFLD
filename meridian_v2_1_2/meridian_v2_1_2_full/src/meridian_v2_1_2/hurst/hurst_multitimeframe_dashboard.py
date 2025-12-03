"""
Multi-Timeframe Hurst Dashboard

Sentient Trader "Master Cycle View" replication.

3-panel interactive dashboard:
- Panel 1: Daily cycles
- Panel 2: Weekly cycles  
- Panel 3: Combined overlay with FLDs

All synchronized with zoom/pan.
"""

import plotly.graph_objs as go
from plotly.subplots import make_subplots

from .hurst_visual_full import CYCLE_COLORS, detect_peaks_from_phase
from .hurst_fld import FLDEngine


def multi_tf_dashboard(price_daily,
                       price_weekly,
                       phasing_daily,
                       phasing_weekly,
                       title="Multi-Timeframe Hurst Dashboard"):
    """
    3-panel interactive dashboard:
      Panel 1: Daily cycles
      Panel 2: Weekly cycles
      Panel 3: Combined overlay (daily + weekly + FLDs)
    
    Args:
        price_daily: Daily price series
        price_weekly: Weekly price series
        phasing_daily: Daily phasing results
        phasing_weekly: Weekly phasing results
        title: Dashboard title
    
    Returns:
        Plotly figure with 3 synchronized panels
    
    Example:
        >>> from meridian_v2_1_2.hurst import (
        ...     HurstPhasingEngine,
        ...     RightTranslationAdjuster
        ... )
        >>> from meridian_v2_1_2.hurst.hurst_multitimeframe_dashboard import multi_tf_dashboard
        >>> 
        >>> # Daily analysis
        >>> phaser_d = HurstPhasingEngine([20, 40, 80])
        >>> res_d = phaser_d.phase_all(price_daily)
        >>> 
        >>> # Weekly analysis
        >>> phaser_w = HurstPhasingEngine([80, 160, 320])
        >>> res_w = phaser_w.phase_all(price_weekly)
        >>> 
        >>> # Apply right-translation
        >>> adj = RightTranslationAdjuster()
        >>> res_d_adj = adj.adjust_all_cycles(res_d)
        >>> res_w_adj = adj.adjust_all_cycles(res_w)
        >>> 
        >>> # Create dashboard
        >>> fig = multi_tf_dashboard(price_daily, price_weekly, res_d_adj, res_w_adj)
        >>> fig.show()
    """
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=[0.35, 0.35, 0.30],
        subplot_titles=("Daily Cycles", "Weekly Cycles", "Combined Overlay"),
    )

    # ------------------------------------------------------------------
    # PANEL 1 — DAILY
    # ------------------------------------------------------------------
    fig.add_trace(go.Scatter(
        x=price_daily.index,
        y=price_daily.values,
        mode="lines", name="Daily Price",
        line=dict(color="black"),
        hovertemplate='Daily Price: $%{y:.2f}<extra></extra>'
    ), row=1, col=1)

    for period, res in phasing_daily.items():
        color = CYCLE_COLORS.get(period, "#999")
        troughs = res["troughs"]
        phase = res["phase"]
        peaks = detect_peaks_from_phase(price_daily, phase)

        fig.add_trace(go.Scatter(
            x=troughs, y=price_daily.loc[troughs],
            mode="markers",
            marker=dict(size=10 + period*0.1, color=color,
                        line=dict(color="black", width=1)),
            name=f"{period}d troughs (Daily)",
            hovertemplate=f'{period}-day trough<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=peaks, y=price_daily.loc[peaks],
            mode="markers",
            marker=dict(size=8 + period*0.08,
                        color="rgba(0,0,0,0)",
                        line=dict(color=color, width=2),
                        symbol="circle-open"),
            name=f"{period}d peaks (Daily)",
            hovertemplate=f'{period}-day peak<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
        ), row=1, col=1)

    # ------------------------------------------------------------------
    # PANEL 2 — WEEKLY
    # ------------------------------------------------------------------
    fig.add_trace(go.Scatter(
        x=price_weekly.index,
        y=price_weekly.values,
        mode="lines", name="Weekly Price",
        line=dict(color="black"),
        hovertemplate='Weekly Price: $%{y:.2f}<extra></extra>'
    ), row=2, col=1)

    for period, res in phasing_weekly.items():
        color = CYCLE_COLORS.get(period, "#999")
        troughs = res["troughs"]
        phase = res["phase"]
        peaks = detect_peaks_from_phase(price_weekly, phase)

        fig.add_trace(go.Scatter(
            x=troughs, y=price_weekly.loc[troughs],
            mode="markers",
            marker=dict(size=12 + period*0.15,
                        color=color,
                        line=dict(color="black", width=1)),
            name=f"{period}w troughs (Weekly)",
            hovertemplate=f'{period}-week trough<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
        ), row=2, col=1)

        fig.add_trace(go.Scatter(
            x=peaks, y=price_weekly.loc[peaks],
            mode="markers",
            marker=dict(size=10 + period*0.1,
                        color="rgba(0,0,0,0)",
                        line=dict(color=color, width=2),
                        symbol="circle-open"),
            name=f"{period}w peaks (Weekly)",
            hovertemplate=f'{period}-week peak<br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
        ), row=2, col=1)

    # ------------------------------------------------------------------
    # PANEL 3 — Combined Overlay (Daily + Weekly + FLDs)
    # ------------------------------------------------------------------
    fig.add_trace(go.Scatter(
        x=price_daily.index,
        y=price_daily.values,
        mode="lines",
        name="Daily Price",
        line=dict(color="steelblue", width=1),
        hovertemplate='Daily: $%{y:.2f}<extra></extra>'
    ), row=3, col=1)

    fig.add_trace(go.Scatter(
        x=price_weekly.index,
        y=price_weekly.values,
        mode="lines",
        name="Weekly Price",
        line=dict(color="firebrick", width=2),
        hovertemplate='Weekly: $%{y:.2f}<extra></extra>'
    ), row=3, col=1)

    # Add Daily FLDs
    for period, res in phasing_daily.items():
        engine = FLDEngine(period)
        fld = engine.compute_fld(price_daily)
        
        fig.add_trace(go.Scatter(
            x=fld.index,
            y=fld.values,
            mode="lines",
            name=f"Daily FLD {period}",
            line=dict(color=CYCLE_COLORS.get(period, "#888"),
                      width=1.2, dash="dot"),
            opacity=0.7,
            hovertemplate=f'FLD-{period}d: $%{{y:.2f}}<extra></extra>'
        ), row=3, col=1)

    # Add Weekly FLDs
    for period, res in phasing_weekly.items():
        engine = FLDEngine(period)
        fld = engine.compute_fld(price_weekly)
        
        fig.add_trace(go.Scatter(
            x=fld.index,
            y=fld.values,
            mode="lines",
            name=f"Weekly FLD {period}",
            line=dict(color=CYCLE_COLORS.get(period, "#888"),
                      width=1.7, dash="dash"),
            opacity=0.9,
            hovertemplate=f'FLD-{period}w: $%{{y:.2f}}<extra></extra>'
        ), row=3, col=1)

    # ------------------------------------------------------------------
    # FINAL LAYOUT
    # ------------------------------------------------------------------
    fig.update_layout(
        title=title,
        hovermode="x unified",
        template="plotly_white",
        height=1200,
        legend=dict(
            orientation="h",
            x=0, y=1.15
        ),
        margin=dict(l=40, r=40, t=120, b=40),
    )

    fig.update_xaxes(showgrid=True)
    fig.update_yaxes(showgrid=True, title_text="Price")

    return fig

