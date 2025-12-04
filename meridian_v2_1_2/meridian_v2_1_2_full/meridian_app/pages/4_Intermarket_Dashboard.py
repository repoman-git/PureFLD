"""
Intermarket Live Dashboard

Real-time cross-market cycle intelligence.

Author: Meridian Team
Date: December 4, 2025
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

st.title("📈 Intermarket Dashboard")
st.markdown("**Cross-market cycle intelligence and correlation analysis**")

st.info("💡 Upload multiple market CSVs to see intermarket relationships")

# File upload
uploaded_files = st.file_uploader(
    "Upload market data CSVs (timestamp, price)",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files and len(uploaded_files) >= 2:
    # Load all files
    market_data = {}
    
    for file in uploaded_files:
        df = pd.read_csv(file)
        if 'timestamp' in df.columns and 'price' in df.columns:
            symbol = file.name.replace('.csv', '').upper()
            market_data[symbol] = pd.Series(
                df['price'].values,
                index=pd.to_datetime(df['timestamp'])
            )
    
    if len(market_data) >= 2:
        st.success(f"✅ Loaded {len(market_data)} markets")
        
        # Calculate correlations
        st.subheader("Intermarket Correlation Heatmap")
        
        # Align all series
        df_all = pd.DataFrame(market_data)
        correlation_matrix = df_all.corr()
        
        fig = px.imshow(
            correlation_matrix,
            labels=dict(color="Correlation"),
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1,
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Price comparison
        st.subheader("Multi-Market Price Comparison (Normalized)")
        
        # Normalize to 100
        df_normalized = df_all.div(df_all.iloc[0]) * 100
        
        fig2 = go.Figure()
        for col in df_normalized.columns:
            fig2.add_trace(go.Scatter(
                x=df_normalized.index,
                y=df_normalized[col],
                mode='lines',
                name=col
            ))
        
        fig2.update_layout(
            title="Normalized Price Comparison (Base=100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            template="plotly_white",
            height=500
        )
        st.plotly_chart(fig2, use_container_width=True)
        
        # Correlation table
        st.subheader("Correlation Matrix")
        st.dataframe(correlation_matrix.style.background_gradient(cmap='RdBu', vmin=-1, vmax=1))
        
        # Lead/Lag Analysis
        st.subheader("Lead/Lag Analysis")
        st.info("💡 Use Meridian API endpoint for advanced lead/lag detection")

else:
    st.warning("Please upload at least 2 market CSV files to compare")

