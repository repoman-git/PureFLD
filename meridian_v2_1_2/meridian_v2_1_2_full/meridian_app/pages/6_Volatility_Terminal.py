"""
Volatility & Risk Terminal

Real-time ATR, compression/expansion detection, risk scoring.

Author: Meridian Team
Date: December 4, 2025
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

st.title("⚠️ Volatility & Risk Terminal")
st.markdown("**Real-time risk metrics and position sizing guidance**")

uploaded = st.file_uploader("Upload market CSV", type=["csv"], key="vol_terminal")

if uploaded:
    df = pd.read_csv(uploaded)
    
    if 'timestamp' in df.columns and 'price' in df.columns:
        prices = pd.Series(df['price'].values, index=pd.to_datetime(df['timestamp']))
        
        st.success(f"✅ Analyzing {len(prices)} bars")
        
        # Calculate volatility metrics
        returns = prices.pct_change()
        volatility_20 = returns.rolling(20).std() * 100
        volatility_60 = returns.rolling(60).std() * 100
        
        # ATR approximation
        high_low = prices.rolling(14).max() - prices.rolling(14).min()
        atr = high_low.rolling(14).mean()
        atr_pct = (atr / prices) * 100
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current ATR", f"${atr.iloc[-1]:.2f}" if len(atr) > 0 else "N/A")
        
        with col2:
            st.metric("ATR %", f"{atr_pct.iloc[-1]:.2f}%" if len(atr_pct) > 0 else "N/A")
        
        with col3:
            st.metric("Vol (20d)", f"{volatility_20.iloc[-1]:.2f}%" if len(volatility_20) > 0 else "N/A")
        
        with col4:
            vol_ratio = volatility_20.iloc[-1] / volatility_60.iloc[-1] if len(volatility_60) > 0 and volatility_60.iloc[-1] > 0 else 1
            st.metric("Vol Ratio", f"{vol_ratio:.2f}")
        
        # Volatility chart
        st.subheader("Volatility Analysis")
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=('Price', 'ATR', 'Volatility'),
            vertical_spacing=0.08
        )
        
        fig.add_trace(
            go.Scatter(x=prices.index, y=prices.values, name='Price'),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=atr.index, y=atr.values, name='ATR', line=dict(color='orange')),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=volatility_20.index, y=volatility_20.values, name='Vol 20d'),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=volatility_60.index, y=volatility_60.values, name='Vol 60d', line=dict(dash='dash')),
            row=3, col=1
        )
        
        fig.update_layout(height=800, template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk assessment
        st.subheader("Risk Assessment")
        
        current_vol = volatility_20.iloc[-1] if len(volatility_20) > 0 else 0
        avg_vol = volatility_20.mean() if len(volatility_20) > 0 else 0
        
        if current_vol > avg_vol * 1.5:
            st.error("⚠️ HIGH RISK: Volatility is elevated")
        elif current_vol < avg_vol * 0.7:
            st.success("✅ LOW RISK: Volatility is compressed")
        else:
            st.info("📊 MODERATE RISK: Normal volatility")

else:
    st.info("Upload a CSV file to analyze volatility and risk")

