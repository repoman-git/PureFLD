"""
Cycle Health Monitor

Real-time cycle strength and quality metrics.

Author: Meridian Team
Date: December 4, 2025
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import numpy as np

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

st.title("🌀 Cycle Health Monitor")
st.markdown("**Real-time cycle strength and quality assessment**")

uploaded = st.file_uploader("Upload market CSV", type=["csv"], key="cycle_health")

if uploaded:
    df = pd.read_csv(uploaded)
    
    if 'timestamp' in df.columns and 'price' in df.columns:
        prices = pd.Series(df['price'].values, index=pd.to_datetime(df['timestamp']))
        
        st.success(f"✅ Loaded {len(prices)} bars")
        
        # Calculate cycle metrics
        col1, col2, col3 = st.columns(3)
        
        # Simple cycle strength (volatility normalized)
        returns = prices.pct_change()
        volatility = returns.std()
        cycle_strength = (prices.rolling(40).max() - prices.rolling(40).min()) / prices
        
        with col1:
            st.metric("Avg Cycle Strength", f"{cycle_strength.mean():.2%}")
        
        with col2:
            st.metric("Volatility", f"{volatility:.2%}")
        
        with col3:
            current_strength = cycle_strength.iloc[-1] if len(cycle_strength) > 0 else 0
            st.metric("Current Strength", f"{current_strength:.2%}")
        
        # Cycle strength over time
        st.subheader("Cycle Strength Over Time")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=cycle_strength.index,
            y=cycle_strength.values * 100,
            mode='lines',
            name='Cycle Strength',
            fill='tozeroy'
        ))
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Cycle Strength (%)",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Price with strength overlay
        st.subheader("Price with Cycle Strength Overlay")
        
        from plotly.subplots import make_subplots
        
        fig2 = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=('Price', 'Cycle Strength'),
            vertical_spacing=0.1
        )
        
        fig2.add_trace(
            go.Scatter(x=prices.index, y=prices.values, name='Price'),
            row=1, col=1
        )
        
        fig2.add_trace(
            go.Scatter(x=cycle_strength.index, y=cycle_strength.values * 100,
                      name='Strength', fill='tozeroy'),
            row=2, col=1
        )
        
        fig2.update_layout(height=600, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Upload a CSV file to monitor cycle health")

