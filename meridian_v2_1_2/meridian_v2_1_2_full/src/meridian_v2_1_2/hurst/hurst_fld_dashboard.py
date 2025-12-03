"""
FLD Interactive Dashboard (Plotly)

Interactive FLD visualization with zoom, hover, and toggles.
"""

import plotly.graph_objs as go


def plot_fld_interactive(price, fld, long_crosses, short_crosses,
                         upper=None, lower=None,
                         title="FLD Interactive View"):
    """
    Interactive Plotly FLD chart.
    
    Args:
        price: Price series
        fld: FLD series
        long_crosses: Long cross timestamps
        short_crosses: Short cross timestamps
        upper: Upper envelope (optional)
        lower: Lower envelope (optional)
        title: Chart title
    
    Returns:
        Plotly figure
    
    Features:
    - Zoom and pan
    - Hover tooltips
    - Toggle visibility
    - Cross markers
    
    Example:
        >>> fig = plot_fld_interactive(price, fld, long_crosses, short_crosses)
        >>> fig.show()
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=price.index,
        y=price.values,
        name="Price",
        mode="lines",
        line=dict(color="black", width=1.4),
        hovertemplate='Price: $%{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=fld.index,
        y=fld.values,
        name=fld.name,
        mode="lines",
        line=dict(color="blue", width=1.3),
        hovertemplate='FLD: $%{y:.2f}<extra></extra>'
    ))

    if upper is not None:
        fig.add_trace(go.Scatter(
            x=upper.index,
            y=upper.values,
            name="Envelope High",
            mode="lines",
            line=dict(color="royalblue", dash="dot"),
            opacity=0.5
        ))

        fig.add_trace(go.Scatter(
            x=lower.index,
            y=lower.values,
            name="Envelope Low",
            mode="lines",
            line=dict(color="royalblue", dash="dot"),
            opacity=0.5
        ))

    fig.add_trace(go.Scatter(
        x=long_crosses,
        y=price.loc[long_crosses],
        name="Long FLD Cross",
        mode="markers",
        marker=dict(color="green", size=12, symbol="triangle-up"),
        hovertemplate='LONG Signal<br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=short_crosses,
        y=price.loc[short_crosses],
        name="Short FLD Cross",
        mode="markers",
        marker=dict(color="red", size=12, symbol="triangle-down"),
        hovertemplate='SHORT Signal<br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=title,
        hovermode="x unified",
        template="plotly_white",
        height=600,
        xaxis_title="Date",
        yaxis_title="Price",
        showlegend=True
    )

    fig.update_xaxes(showgrid=True, rangeslider_visible=False)
    fig.update_yaxes(showgrid=True)

    return fig

