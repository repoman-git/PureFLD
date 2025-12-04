"""Chart Components"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def price_chart(price: pd.Series, title: str = "Price Chart") -> go.Figure:
    """Basic price chart"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price.index, y=price.values, mode='lines', name='Price'))
    fig.update_layout(template="plotly_white", height=400, title=title)
    return fig

def multi_asset_chart(price_dict: dict, title: str = "Multi-Asset View") -> go.Figure:
    """Chart multiple assets"""
    fig = go.Figure()
    for symbol, prices in price_dict.items():
        fig.add_trace(go.Scatter(x=prices.index, y=prices.values, mode='lines', name=symbol))
    fig.update_layout(template="plotly_white", height=500, title=title)
    return fig

