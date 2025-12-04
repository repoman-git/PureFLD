"""Volatility Dashboard"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_volatility_dashboard(df, title="Volatility & Risk Dashboard"):
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                       subplot_titles=["Volatility & Envelope", "Cycle-Aware ATR",
                                     "Cycle Volatility Model", "Risk Window Score & Stops"],
                       vertical_spacing=0.08)
    
    fig.add_trace(go.Scatter(x=df.index, y=df["vol"], name="Vol"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["vol_env_upper"], name="Upper"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["vol_env_lower"], name="Lower"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["catr"], name="C-ATR"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["vcycle"], name="CycleVol"), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["risk_window_score"], name="RWS"), row=4, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df["stop_distance"], name="Stops"), row=4, col=1)
    
    fig.update_layout(height=900, template="plotly_white", title=title)
    fig.show()

class VolatilityDashboard:
    pass  # Placeholder for future Streamlit dashboard

